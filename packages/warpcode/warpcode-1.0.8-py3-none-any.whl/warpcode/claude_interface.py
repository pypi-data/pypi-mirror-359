"""
Claude Interface

Handles automated Claude Coder execution with real-time log monitoring
and activity tracking for the BDD orchestration loop.
"""

import asyncio
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import threading
import queue
import re
import os

from rich.console import Console

from .scoreboard_manager import ScoreboardManager, ClaudeStatus
from .claude_otel_monitor import ClaudeOTELMonitor, ClaudeEvent


class ClaudeInterface:
    """Manages Claude Coder execution and monitoring"""
    
    def __init__(self, project_dir: Path, scoreboard_manager: ScoreboardManager, 
                 console: Optional[Console] = None):
        self.project_dir = project_dir
        self.scoreboard_manager = scoreboard_manager
        self.console = console or Console()
        
        # Process management
        self.current_process: Optional[subprocess.Popen] = None
        self.log_queue = queue.Queue()
        self.log_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        
        # Status tracking
        self.current_iteration = 1
        self.start_time: Optional[datetime] = None
        self.estimated_completion: Optional[datetime] = None
        
        # Activity tracking
        self.current_feature = ""
        self.current_file = ""
        self.current_action = ""
        self.progress_log: List[str] = []
    
    def check_claude_availability(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.console.print(f"[green]✓ Claude Code CLI available: {result.stdout.strip()}[/green]")
                return True
            else:
                self.console.print("[red]✗ Claude Code CLI not responding properly[/red]")
                return False
        except subprocess.TimeoutExpired:
            self.console.print("[red]✗ Claude Code CLI check timed out[/red]")
            return False
        except FileNotFoundError:
            self.console.print("[red]✗ Claude Code CLI not found. Please install Claude Code first.[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]✗ Error checking Claude Code CLI: {e}[/red]")
            return False
    
    def create_claude_prompt(self, bdd_summary: str, complexity_issues: List[str] = None, 
                           iteration: int = 1) -> str:
        """Create focused, time-limited prompt for Claude with strict anti-mock enforcement"""
        prompt_parts = []
        
        # Critical time and focus constraints
        prompt_parts.append(f"🎯 FOCUSED BDD TASK - ITERATION {iteration} (5 MIN MAX)")
        prompt_parts.append("=" * 60)
        prompt_parts.append("⏰ TIME LIMIT: Complete this task in 5 minutes or less")
        prompt_parts.append("📍 FOCUS: Fix ONE specific failing scenario at a time")
        prompt_parts.append("📊 PROGRESS: Update status every 30 seconds")
        prompt_parts.append("")
        
        # Current BDD status
        prompt_parts.append("📋 CURRENT BDD STATUS:")
        prompt_parts.append(bdd_summary)
        prompt_parts.append("")
        
        # Complexity issues (if any)
        if complexity_issues:
            prompt_parts.append("⚠️ CODE COMPLEXITY ISSUES:")
            for issue in complexity_issues:
                prompt_parts.append(f"  • {issue}")
            prompt_parts.append("")
        
        # Strict anti-mock instructions
        instructions = [
            "🚨 CRITICAL: ZERO TOLERANCE FOR FAKE IMPLEMENTATIONS",
            "",
            "❌ ABSOLUTELY FORBIDDEN:",
            "  • HTML/CSS/JavaScript mock interfaces (like create_test_interface)",
            "  • Hardcoded fake data or responses",
            "  • subprocess.Popen calls without error checking",
            "  • Fallback mocks when real code fails",
            "  • 'pass' statements or placeholder functions",
            "  • Always-passing step definitions",
            "  • Fake terminal outputs or simulated responses",
            "",
            "✅ REQUIRED IMPLEMENTATIONS:",
            "  • Real Python classes and functions that actually work",
            "  • Proper error handling for subprocess calls",
            "  • Tests that FAIL when .py files are missing",
            "  • Actual file I/O, not simulated",
            "  • Real command execution, not fake responses",
            "",
            "🔍 VERIFICATION REQUIREMENT:",
            "After implementing, the test must:",
            "  1. PASS when the .py file exists and works",
            "  2. FAIL when the .py file is renamed to .old",
            "  3. PASS again when the .py file is restored",
            "",
            "📝 SPECIFIC TASK FOR THIS ITERATION:",
            "  • Pick ONE failing scenario from the BDD status above",
            "  • Implement ONLY the real Python code needed for that scenario",
            "  • Ensure subprocess calls check return codes and handle errors",
            "  • Test the implementation by temporarily moving files",
            "  • Provide progress updates every 30 seconds",
            "",
            "⚡ QUICK SUCCESS CRITERIA:",
            "  • One scenario changes from FAILED to PASSED",
            "  • Implementation uses real Python code (not HTML mocks)",
            "  • Test fails when implementation file is missing",
            "  • No hardcoded or fake responses",
            "",
            "🎯 START NOW: Pick the first failing scenario and implement real code for it."
        ]
        
        prompt_parts.extend(instructions)
        
        return "\n".join(prompt_parts)
    
    def run_claude_automated(self, prompt: str, timeout_minutes: int = 5) -> bool:
        """Run Claude in fully automated mode with the given prompt"""
        
        try:
            # Prepare Claude command with correct flags for current CLI version
            cmd = [
                "claude",
                "--print",  # Print response and exit (non-interactive)
                "--dangerously-skip-permissions",  # Skip permission checks
                prompt  # Pass prompt directly as argument
            ]
            
            self.console.print(f"[blue]🤖 Starting Claude with automated flags...[/blue]")
            
            # Update status
            self._update_claude_status("starting", "Initializing Claude session")
            
            # Start process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.project_dir
            )
            
            # Start monitoring
            self.start_time = datetime.now()
            self.estimated_completion = self.start_time + timedelta(minutes=timeout_minutes)
            self._start_log_monitoring()
            
            # Initial status update
            self._update_claude_status("starting", "Claude session initializing")
            
            # Wait for completion with timeout with periodic status updates
            try:
                start_wait = time.time()
                poll_interval = 2.0  # Check every 2 seconds
                last_status_update = time.time()
                
                while self.current_process.poll() is None:
                    # Check if we've exceeded timeout
                    if time.time() - start_wait > (timeout_minutes * 60):
                        raise subprocess.TimeoutExpired(self.current_process.args, timeout_minutes * 60)
                    
                    # Update status every 5 seconds even if no output
                    current_time = time.time()
                    if current_time - last_status_update > 5.0:
                        self._update_claude_status("working", self.current_action or "Processing request")
                        last_status_update = current_time
                    
                    time.sleep(poll_interval)
                
                success = self.current_process.returncode == 0
                
                if success:
                    self.console.print("[green]✓ Claude completed successfully[/green]")
                    self._update_claude_status("complete", "Task completed successfully")
                else:
                    self.console.print(f"[yellow]⚠ Claude exited with code {self.current_process.returncode}[/yellow]")
                    self._update_claude_status("error", f"Exited with code {self.current_process.returncode}")
                
                return success
                
            except subprocess.TimeoutExpired:
                self.console.print(f"[red]⚠ Claude timed out after {timeout_minutes} minutes[/red]")
                self._terminate_claude()
                self._update_claude_status("timeout", f"Timed out after {timeout_minutes} minutes")
                return False
            
        except Exception as e:
            self.console.print(f"[red]✗ Error running Claude: {e}[/red]")
            self._update_claude_status("error", f"Error: {e}")
            return False
        
        finally:
            # Cleanup
            self._stop_log_monitoring()
    
    def _start_log_monitoring(self):
        """Start monitoring Claude's output in a separate thread"""
        self.is_monitoring = True
        self.log_thread = threading.Thread(target=self._monitor_output, daemon=True)
        self.log_thread.start()
    
    def _stop_log_monitoring(self):
        """Stop monitoring Claude's output"""
        self.is_monitoring = False
        if self.log_thread:
            self.log_thread.join(timeout=5)
    
    def _monitor_output(self):
        """Monitor Claude's output and extract activity information"""
        if not self.current_process or not self.current_process.stdout:
            return
        
        try:
            for line in iter(self.current_process.stdout.readline, ''):
                if not self.is_monitoring:
                    break
                
                line = line.strip()
                if line:
                    # Add to log queue for processing
                    self.log_queue.put(line)
                    
                    # Process line for activity tracking
                    self._process_log_line(line)
                    
                    # Show real-time output to user
                    self._display_claude_output(line)
                    
                    # Update status periodically
                    self._update_claude_status("working", self.current_action)
                    
        except Exception as e:
            self.console.print(f"[red]Error monitoring Claude output: {e}[/red]")
    
    def _display_claude_output(self, line: str):
        """Display Claude's output in real-time with appropriate formatting"""
        # Skip empty lines
        if not line.strip():
            return
        
        # Color-code different types of output
        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
            self.console.print(f"[red]Claude: {line}[/red]")
        elif any(keyword in line.lower() for keyword in ['success', 'complete', 'finished', 'done']):
            self.console.print(f"[green]Claude: {line}[/green]")
        elif any(keyword in line.lower() for keyword in ['warning', 'warn']):
            self.console.print(f"[yellow]Claude: {line}[/yellow]")
        elif any(keyword in line.lower() for keyword in ['reading', 'writing', 'creating', 'updating', 'editing']):
            self.console.print(f"[cyan]Claude: {line}[/cyan]")
        elif any(keyword in line.lower() for keyword in ['running', 'executing', 'processing']):
            self.console.print(f"[blue]Claude: {line}[/blue]")
        else:
            self.console.print(f"[dim]Claude: {line}[/dim]")
    
    def _process_log_line(self, line: str):
        """Process a single log line to extract activity information"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add to progress log
        self.progress_log.append(f"{timestamp} - {line}")
        
        # Keep only last 20 log entries
        if len(self.progress_log) > 20:
            self.progress_log = self.progress_log[-20:]
        
        # Extract current feature being worked on
        feature_patterns = [
            r'(?i)working on\s+(.+\.feature)',
            r'(?i)feature:\s+(.+)',
            r'(?i)processing\s+(.+\.feature)',
            r'(?i)analyzing\s+(.+\.feature)'
        ]
        
        for pattern in feature_patterns:
            match = re.search(pattern, line)
            if match:
                self.current_feature = match.group(1)
                break
        
        # Extract current file being worked on
        file_patterns = [
            r'(?i)editing\s+(.+\.(py|feature))',
            r'(?i)creating\s+(.+\.(py|feature))',
            r'(?i)updating\s+(.+\.(py|feature))',
            r'(?i)file:\s+(.+\.(py|feature))'
        ]
        
        for pattern in file_patterns:
            match = re.search(pattern, line)
            if match:
                self.current_file = match.group(1)
                break
        
        # Extract current action
        action_patterns = [
            (r'(?i)implementing\s+(.+)', 'implementing {}'),
            (r'(?i)creating\s+(.+)', 'creating {}'),
            (r'(?i)updating\s+(.+)', 'updating {}'),
            (r'(?i)fixing\s+(.+)', 'fixing {}'),
            (r'(?i)analyzing\s+(.+)', 'analyzing {}'),
            (r'(?i)testing\s+(.+)', 'testing {}'),
            (r'(?i)debugging\s+(.+)', 'debugging {}')
        ]
        
        for pattern, action_format in action_patterns:
            match = re.search(pattern, line)
            if match:
                self.current_action = action_format.format(match.group(1))
                break
        
        # Default action if nothing specific found
        if not self.current_action and line:
            self.current_action = "processing request"
    
    def _update_claude_status(self, status: str, action: str):
        """Update Claude status in scoreboard"""
        claude_status = ClaudeStatus(
            timestamp=self.scoreboard_manager._get_timestamp(),
            iteration=self.current_iteration,
            status=status,
            current_feature=self.current_feature,
            current_file=self.current_file,
            current_action=action,
            progress_log=self.progress_log.copy(),
            estimated_completion=self.estimated_completion.isoformat() if self.estimated_completion else None
        )
        
        self.scoreboard_manager.update_claude_status(claude_status)
    
    def _terminate_claude(self):
        """Terminate Claude process if running"""
        if self.current_process:
            try:
                self.current_process.terminate()
                # Wait a bit for graceful termination
                self.current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if still running
                self.current_process.kill()
                self.current_process.wait()
            except Exception:
                pass  # Ignore errors during termination
        
        # Also cleanup OTEL monitor
        if hasattr(self, 'otel_monitor'):
            try:
                self.otel_monitor._terminate_claude()
            except:
                pass
    
    def get_current_logs(self) -> List[str]:
        """Get current log entries from the queue"""
        logs = []
        try:
            while True:
                log_line = self.log_queue.get_nowait()
                logs.append(log_line)
        except queue.Empty:
            pass
        return logs
    
    def is_claude_running(self) -> bool:
        """Check if Claude is currently running"""
        return (
            self.current_process is not None and 
            self.current_process.poll() is None
        )
    
    def wait_for_completion(self, check_interval: float = 0.5) -> bool:
        """Wait for Claude to complete and return success status"""
        if not self.current_process:
            return False
        
        try:
            last_update = time.time()
            while self.is_claude_running():
                time.sleep(check_interval)
                
                # Show periodic status updates
                current_time = time.time()
                if current_time - last_update > 5.0:  # Every 5 seconds
                    if self.current_action:
                        self.console.print(f"[blue]Status: {self.current_action}[/blue]")
                    last_update = current_time
            
            return self.current_process.returncode == 0
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupting Claude...[/yellow]")
            self._terminate_claude()
            return False
    
    def set_iteration(self, iteration: int):
        """Set current iteration number"""
        self.current_iteration = iteration
    
    def reset_status(self):
        """Reset tracking status for new iteration"""
        self.current_feature = ""
        self.current_file = ""
        self.current_action = ""
        self.progress_log = []
        self.start_time = None
        self.estimated_completion = None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current status summary"""
        otel_status = self.otel_monitor.get_status_summary()
        
        return {
            "is_running": self.is_claude_running(),
            "current_feature": self.current_feature,
            "current_file": self.current_file,
            "current_action": self.current_action or otel_status.get("activity", ""),
            "progress_entries": len(self.progress_log),
            "iteration": self.current_iteration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "otel_status": otel_status["status"],
            "otel_activity": otel_status["activity"],
            "total_events": otel_status["total_events"]
        }
    
    def _handle_claude_event(self, event: ClaudeEvent):
        """Handle Claude OpenTelemetry events"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add to progress log
        log_entry = f"{timestamp} - {event.event_name}: {event.attributes.get('tool_name', event.attributes.get('activity', 'activity'))}"
        self.progress_log.append(log_entry)
        
        # Keep only last 20 entries
        if len(self.progress_log) > 20:
            self.progress_log = self.progress_log[-20:]
        
        # Extract relevant info for tracking
        if event.event_name == 'tool_result':
            tool_name = event.attributes.get('tool_name', '')
            if tool_name:
                if 'edit' in tool_name.lower() or 'write' in tool_name.lower():
                    self.current_action = f"editing with {tool_name}"
                elif 'read' in tool_name.lower():
                    self.current_action = f"reading with {tool_name}"
                else:
                    self.current_action = f"using {tool_name}"
    
    def _handle_status_change(self, status: str, activity: str):
        """Handle status changes from OpenTelemetry monitor"""
        self.current_action = activity
        
        # Update scoreboard with real-time status
        self._update_claude_status(status, activity)