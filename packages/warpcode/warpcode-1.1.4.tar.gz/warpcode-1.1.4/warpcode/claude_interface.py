"""
Claude Interface

Handles automated Claude Coder execution with real-time log monitoring
and activity tracking for the BDD orchestration loop.
"""

import asyncio
import subprocess
import tempfile
import time
import json
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
        
        # Conversation continuity tracking
        self.conversation_id: Optional[str] = None
        self.has_active_conversation = False
        self.conversation_file = self.project_dir / ".warpcode_conversation_id"
        
        # Debug settings
        self.debug_mode = os.getenv('WARPCODE_DEBUG', '0') == '1'
        self.verbose_output = os.getenv('WARPCODE_VERBOSE', '0') == '1'
    
    def enable_debug_mode(self, enable: bool = True):
        """Enable or disable debug mode programmatically"""
        self.debug_mode = enable
        if enable:
            self.console.print("[blue]🐛 Debug mode enabled - showing comprehensive Claude activity[/blue]")
    
    def enable_verbose_output(self, enable: bool = True):
        """Enable or disable verbose output programmatically"""
        self.verbose_output = enable
        if enable:
            self.console.print("[blue]📝 Verbose output enabled - showing all Claude output[/blue]")
    
    def show_debug_status(self):
        """Show current debug and monitoring configuration"""
        self.console.print("[blue]🔧 Claude Interface Debug Status:[/blue]")
        self.console.print(f"  Debug mode: {'✅ Enabled' if self.debug_mode else '❌ Disabled'}")
        self.console.print(f"  Verbose output: {'✅ Enabled' if self.verbose_output else '❌ Disabled'}")
        self.console.print(f"  Conversation tracking: {'✅ Active' if self.has_active_conversation else '❌ Inactive'}")
        if self.conversation_id:
            self.console.print(f"  Conversation ID: {self.conversation_id}")
        self.console.print(f"  Current iteration: {self.current_iteration}")
        self.console.print(f"  Project directory: {self.project_dir}")
    
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
    
    def _load_conversation_state(self) -> bool:
        """Load existing conversation state if available"""
        try:
            if self.conversation_file.exists():
                with open(self.conversation_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_id = data.get('conversation_id')
                    self.has_active_conversation = bool(self.conversation_id)
                    if self.has_active_conversation:
                        self.console.print(f"[blue]📞 Continuing conversation: {self.conversation_id[:8]}...[/blue]")
                        return True
        except Exception as e:
            self.console.print(f"[yellow]⚠ Could not load conversation state: {e}[/yellow]")
        
        self.has_active_conversation = False
        return False
    
    def _save_conversation_state(self, conversation_id: str):
        """Save conversation state for future continuity"""
        try:
            self.conversation_id = conversation_id
            self.has_active_conversation = True
            
            with open(self.conversation_file, 'w') as f:
                json.dump({
                    'conversation_id': conversation_id,
                    'created_at': datetime.now().isoformat(),
                    'iteration': self.current_iteration
                }, f, indent=2)
            
            self.console.print(f"[blue]💾 Saved conversation state: {conversation_id[:8]}...[/blue]")
        except Exception as e:
            self.console.print(f"[yellow]⚠ Could not save conversation state: {e}[/yellow]")
    
    def _extract_conversation_id(self, output: str) -> Optional[str]:
        """Extract conversation ID from Claude output"""
        # Look for patterns like "Conversation ID: abc123..." or "Session: abc123..."
        patterns = [
            r'[Cc]onversation\s+ID:\s+([a-f0-9-]+)',
            r'[Ss]ession:\s+([a-f0-9-]+)',
            r'[Cc]onversation\s+([a-f0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1)
        
        return None
    
    def clear_conversation_state(self):
        """Clear conversation state (use when starting fresh)"""
        self.conversation_id = None
        self.has_active_conversation = False
        
        try:
            if self.conversation_file.exists():
                self.conversation_file.unlink()
                self.console.print("[blue]🗑️ Cleared conversation state[/blue]")
        except Exception as e:
            self.console.print(f"[yellow]⚠ Could not clear conversation state: {e}[/yellow]")
    
    def create_claude_prompt(self, bdd_summary: str, complexity_issues: List[str] = None, 
                           iteration: int = 1, validation_failures: List[str] = None) -> str:
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
        
        # Validation failures from previous iteration (if any)
        if validation_failures:
            prompt_parts.append("🔍 PREVIOUS VALIDATION FAILURES DETECTED:")
            prompt_parts.append("❌ The following fake implementation patterns were found:")
            for failure in validation_failures:
                prompt_parts.append(f"  • {failure}")
            prompt_parts.append("")
            prompt_parts.append("⚠️ YOU MUST AVOID THESE PATTERNS COMPLETELY!")
            prompt_parts.append("✅ Focus on creating REAL, FUNCTIONAL implementations only.")
            prompt_parts.append("")
        
        # Red-Green BDD enforcement instructions
        instructions = [
            "🚨 CRITICAL: RED-GREEN BDD DEVELOPMENT ENFORCEMENT",
            "",
            "🔴 RED PHASE (Tests MUST Fail First):",
            "  • ALL tests should FAIL initially when implementation is missing",
            "  • If tests pass immediately, they are FAKE and must be rejected",
            "  • Failing tests prove they're testing real dependencies",
            "  • Document WHY each test fails (missing file, missing function, etc.)",
            "",
            "🟢 GREEN PHASE (Implement Real Code Only):",
            "  • Write MINIMAL real Python code to make ONE test pass",
            "  • No HTML/CSS/JavaScript mock interfaces",
            "  • No hardcoded responses or fake data",
            "  • No subprocess calls without proper error handling",
            "  • No browser automation against fake interfaces",
            "",
            "❌ ABSOLUTELY FORBIDDEN:",
            "  • HTML/CSS/JavaScript mock interfaces (like create_test_interface)",
            "  • Hardcoded fake data or responses",
            "  • subprocess.Popen calls without error checking",
            "  • Fallback mocks when real code fails",
            "  • Always-passing step definitions that never fail",
            "  • Browser automation against fake HTML interfaces",
            "  • Simulated terminal outputs or fake command responses",
            "",
            "✅ REQUIRED RED-GREEN WORKFLOW:",
            "  1. VERIFY test FAILS when implementation file is missing/renamed",
            "  2. Write MINIMAL real Python code to make test pass",
            "  3. VERIFY test now PASSES with real implementation",
            "  4. VERIFY test FAILS again when implementation is removed",
            "  5. Restore implementation and confirm test PASSES",
            "",
            "🔍 MANDATORY VALIDATION CHECKS:",
            "After each implementation:",
            "  • Run: `mv implementation.py implementation.py.bak`",
            "  • Run: `behave` - tests MUST fail",
            "  • Run: `mv implementation.py.bak implementation.py`", 
            "  • Run: `behave` - tests MUST pass",
            "",
            "📝 RED-GREEN TASK FOR THIS ITERATION:",
            "  • Find ONE currently failing scenario (RED state)",
            "  • Confirm it fails because real implementation is missing",
            "  • Write MINIMAL real Python code (GREEN state)",
            "  • Validate RED-GREEN cycle works properly",
            "  • NO fake implementations or mocks allowed",
            "",
            "⚡ SUCCESS CRITERIA (All Must Be True):",
            "  • Test fails when implementation file is missing (RED)",
            "  • Test passes when real implementation exists (GREEN)",
            "  • Implementation uses real Python code (no HTML/JS)",
            "  • No hardcoded responses or fake data",
            "  • Proper subprocess error handling if used",
            "",
            "🎯 START NOW: Find a failing test, confirm it's in RED state, then implement real code for GREEN."
        ]
        
        prompt_parts.extend(instructions)
        
        return "\n".join(prompt_parts)
    
    def run_claude_two_phase_analysis(self, bdd_status: str, validation_failures: List[str] = None) -> bool:
        """Run Claude in two phases: 1) Fake analysis, 2) Real implementation"""
        
        # Phase 1: Fake Detection Analysis
        self.console.print("[blue]🔍 Phase 1: Running fake implementation analysis...[/blue]")
        
        fake_analysis_prompt = self._create_fake_analysis_prompt(bdd_status, validation_failures)
        fake_analysis_result = self._run_claude_phase(fake_analysis_prompt, "fake_analysis", timeout_minutes=3)
        
        if not fake_analysis_result:
            self.console.print("[red]❌ Phase 1 failed - proceeding with single-phase approach[/red]")
            return self.run_claude_automated(self.create_prompt(bdd_status, validation_failures))
        
        # Phase 2: Real Implementation
        self.console.print("[blue]🛠️ Phase 2: Implementing real code based on analysis...[/blue]")
        
        implementation_prompt = self._create_implementation_prompt(bdd_status, fake_analysis_result)
        implementation_result = self._run_claude_phase(implementation_prompt, "implementation", timeout_minutes=5)
        
        return implementation_result
    
    def _create_fake_analysis_prompt(self, bdd_status: str, validation_failures: List[str] = None) -> str:
        """Create prompt for Phase 1: Fake detection analysis"""
        
        prompt_parts = [
            "🔍 PHASE 1: FAKE IMPLEMENTATION DETECTION",
            "",
            "MISSION: Analyze current BDD implementation and identify ALL fake patterns.",
            "",
            "📊 CURRENT BDD STATUS:",
            bdd_status,
            ""
        ]
        
        if validation_failures:
            prompt_parts.extend([
                "⚠️ PREVIOUS VALIDATION FAILURES:",
                *[f"  • {failure}" for failure in validation_failures],
                ""
            ])
        
        analysis_instructions = [
            "🎯 ANALYSIS TASK:",
            "1. Examine all step definition files in features/steps/",
            "2. Identify fake implementation patterns",
            "3. Create a comprehensive fakesteps.md report",
            "4. Determine which scenarios need real implementations",
            "",
            "❌ LOOK FOR THESE FAKE PATTERNS:",
            "  • HTML/CSS/JavaScript embedded in Python files",
            "  • subprocess calls with immediate browser fallbacks",
            "  • Browser automation against fake HTML interfaces",
            "  • Hardcoded responses instead of real command execution",
            "  • Always-passing assertions that never test real functionality",
            "  • Mock interfaces created with create_test_interface()",
            "",
            "📝 CREATE fakesteps.md WITH:",
            "  • List of all fake patterns found",
            "  • Files containing fake implementations",
            "  • Specific line numbers and code snippets",
            "  • Recommended real implementations for each fake",
            "",
            "🎯 OUTPUT REQUIREMENT:",
            "Create a comprehensive fakesteps.md file that documents:",
            "1. Every fake pattern detected",
            "2. Which step definitions are fake vs real",
            "3. What real implementations are needed",
            "4. Priority order for fixing (most critical first)",
            "",
            "DO NOT implement anything yet - just analyze and document."
        ]
        
        prompt_parts.extend(analysis_instructions)
        return "\n".join(prompt_parts)
    
    def _create_implementation_prompt(self, bdd_status: str, fake_analysis_result: str) -> str:
        """Create prompt for Phase 2: Real implementation based on fake analysis"""
        
        prompt_parts = [
            "🛠️ PHASE 2: REAL IMPLEMENTATION (RED-GREEN BDD)",
            "",
            "📋 FAKE ANALYSIS RESULTS:",
            fake_analysis_result[:2000] + "..." if len(fake_analysis_result) > 2000 else fake_analysis_result,
            "",
            "📊 CURRENT BDD STATUS:",
            bdd_status,
            ""
        ]
        
        implementation_instructions = [
            "🎯 IMPLEMENTATION TASK:",
            "Based on the fake analysis above, implement REAL code using RED-GREEN BDD:",
            "",
            "🔴 RED PHASE:",
            "1. Read fakesteps.md to understand fake patterns",
            "2. Pick ONE failing scenario that has fake implementation", 
            "3. Verify the test fails because real implementation is missing",
            "4. Document the RED state (why it fails)",
            "",
            "🟢 GREEN PHASE:",
            "1. Write MINIMAL real Python code to make the test pass",
            "2. NO HTML/JavaScript mocks or browser automation",
            "3. Use real subprocess calls with proper error handling",
            "4. Implement actual file I/O and system interactions",
            "5. Verify the test passes with real implementation",
            "",
            "🔍 MANDATORY VALIDATION:",
            "For each implementation, verify RED-GREEN cycle:",
            "  • Test fails when implementation file is missing (RED)",
            "  • Test passes when real implementation exists (GREEN)",
            "  • Test fails again when implementation is removed (RED)",
            "",
            "⚡ SUCCESS CRITERIA:",
            "  • Replace fake patterns with real Python code",
            "  • Ensure proper RED-GREEN BDD workflow",
            "  • One scenario changes from FAILED to PASSED",
            "  • Implementation survives file dependency testing",
            "",
            "🚀 EXECUTE NOW: Transform the fake implementation into real code."
        ]
        
        prompt_parts.extend(implementation_instructions)
        return "\n".join(prompt_parts)
    
    def _run_claude_phase(self, prompt: str, phase_name: str, timeout_minutes: int = 5) -> bool:
        """Run a single phase of Claude analysis/implementation"""
        try:
            self._load_conversation_state()
            
            cmd = ["claude"]
            if self.has_active_conversation and self.conversation_id:
                cmd.extend(["-c", self.conversation_id])
            cmd.extend([
                "--print",
                "--dangerously-skip-permissions", 
                prompt
            ])
            
            if self.debug_mode:
                self.console.print(f"[dim]🐛 DEBUG: Running {phase_name} phase[/dim]")
            
            # Configure environment for real-time monitoring
            env = os.environ.copy()
            env.update({
                'CLAUDE_CODE_ENABLE_TELEMETRY': '1',
                'OTEL_LOGS_EXPORTER': 'console',
                'OTEL_LOGS_EXPORT_INTERVAL': '1000',
            })
            
            # Run Claude
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                env=env,
                timeout=timeout_minutes * 60,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✅ {phase_name.title()} phase completed successfully[/green]")
                
                # Save conversation ID if not already saved
                if not self.has_active_conversation:
                    self._save_conversation_state_from_output(result.stdout)
                
                return True
            else:
                self.console.print(f"[red]❌ {phase_name.title()} phase failed: {result.stderr}[/red]")
                return False
                
        except subprocess.TimeoutExpired:
            self.console.print(f"[red]⏰ {phase_name.title()} phase timed out after {timeout_minutes} minutes[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Error in {phase_name} phase: {e}[/red]")
            return False
    
    def run_claude_automated(self, prompt: str, timeout_minutes: int = 5) -> bool:
        """Run Claude in fully automated mode with conversation continuity and comprehensive debug output"""
        
        try:
            # Load existing conversation state
            self._load_conversation_state()
            
            # Debug: Show conversation state
            if self.debug_mode:
                self.console.print(f"[dim]🐛 DEBUG: Conversation state loaded[/dim]")
                self.console.print(f"[dim]🐛 DEBUG: Has active conversation: {self.has_active_conversation}[/dim]")
                if self.conversation_id:
                    self.console.print(f"[dim]🐛 DEBUG: Conversation ID: {self.conversation_id}[/dim]")
            
            # Prepare Claude command with conversation continuity support
            cmd = ["claude"]
            
            if self.has_active_conversation and self.conversation_id:
                # Continue existing conversation
                cmd.extend([
                    "-c", self.conversation_id,  # Continue conversation
                    "--dangerously-skip-permissions",  # Skip permission checks
                    prompt  # Pass prompt directly as argument
                ])
                self.console.print(f"[blue]🤖 Continuing Claude conversation {self.conversation_id[:8]}...[/blue]")
            else:
                # Start new conversation
                cmd.extend([
                    "--print",  # Print response and exit (non-interactive)
                    "--dangerously-skip-permissions",  # Skip permission checks
                    prompt  # Pass prompt directly as argument
                ])
                self.console.print(f"[blue]🤖 Starting new Claude conversation...[/blue]")
            
            # Debug: Show full command
            if self.debug_mode:
                self.console.print(f"[dim]🐛 DEBUG: Full Claude command: {' '.join(cmd)}[/dim]")
                self.console.print(f"[dim]🐛 DEBUG: Working directory: {self.project_dir}[/dim]")
                self.console.print(f"[dim]🐛 DEBUG: Timeout: {timeout_minutes} minutes[/dim]")
            
            # Configure OpenTelemetry for real-time monitoring
            env = os.environ.copy()
            otel_env = {
                'CLAUDE_CODE_ENABLE_TELEMETRY': '1',
                'OTEL_LOGS_EXPORTER': 'console',
                'OTEL_LOGS_EXPORT_INTERVAL': '1000',  # 1 second for real-time updates
                'OTEL_LOG_USER_PROMPTS': '1',  # Enable user prompt logging
                'OTEL_EXPORTER_OTLP_PROTOCOL': 'grpc'
            }
            env.update(otel_env)
            
            # Debug: Show environment variables
            if self.debug_mode:
                self.console.print(f"[dim]🐛 DEBUG: OpenTelemetry environment variables:[/dim]")
                for key, value in otel_env.items():
                    self.console.print(f"[dim]🐛 DEBUG:   {key}={value}[/dim]")
            
            # Show prompt content in verbose mode
            if self.verbose_output:
                self.console.print(f"[dim]📝 VERBOSE: Claude prompt content:[/dim]")
                prompt_lines = prompt.split('\n')
                for i, line in enumerate(prompt_lines[:10]):  # Show first 10 lines
                    self.console.print(f"[dim]📝   {i+1}: {line}[/dim]")
                if len(prompt_lines) > 10:
                    self.console.print(f"[dim]📝   ... ({len(prompt_lines) - 10} more lines)[/dim]")
            
            # Update status
            self._update_claude_status("starting", "Initializing Claude session with OTEL monitoring and debug output")
            
            # Start process with enhanced environment
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.project_dir,
                env=env
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
                
                # Debug: Show process completion details
                if self.debug_mode:
                    elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
                    self.console.print(f"[dim]🐛 DEBUG: Process completed after {elapsed.total_seconds():.1f} seconds[/dim]")
                    self.console.print(f"[dim]🐛 DEBUG: Return code: {self.current_process.returncode}[/dim]")
                    self.console.print(f"[dim]🐛 DEBUG: Progress log entries: {len(self.progress_log)}[/dim]")
                    if self.progress_log:
                        self.console.print(f"[dim]🐛 DEBUG: Last log entry: {self.progress_log[-1]}[/dim]")
                
                # Extract conversation ID from output for future continuity
                if success and not self.has_active_conversation:
                    # Try to extract conversation ID from logged output
                    full_output = "\n".join(self.progress_log)
                    conversation_id = self._extract_conversation_id(full_output)
                    if conversation_id:
                        self._save_conversation_state(conversation_id)
                        self.console.print(f"[green]📞 New conversation started: {conversation_id[:8]}...[/green]")
                        if self.debug_mode:
                            self.console.print(f"[dim]🐛 DEBUG: Full conversation ID: {conversation_id}[/dim]")
                    elif self.debug_mode:
                        self.console.print(f"[dim]🐛 DEBUG: No conversation ID found in output[/dim]")
                
                if success:
                    self.console.print("[green]✓ Claude completed successfully[/green]")
                    self._update_claude_status("complete", "Task completed successfully")
                    
                    # Debug: Show success summary
                    if self.debug_mode:
                        self.console.print(f"[dim]🐛 DEBUG: Success summary:[/dim]")
                        self.console.print(f"[dim]🐛 DEBUG:   Current feature: {self.current_feature or 'None'}[/dim]")
                        self.console.print(f"[dim]🐛 DEBUG:   Current file: {self.current_file or 'None'}[/dim]")
                        self.console.print(f"[dim]🐛 DEBUG:   Current action: {self.current_action or 'None'}[/dim]")
                else:
                    self.console.print(f"[yellow]⚠ Claude exited with code {self.current_process.returncode}[/yellow]")
                    self._update_claude_status("error", f"Exited with code {self.current_process.returncode}")
                    
                    # Debug: Show error details
                    if self.debug_mode:
                        self.console.print(f"[dim]🐛 DEBUG: Error details - examining recent output:[/dim]")
                        recent_logs = self.progress_log[-5:] if len(self.progress_log) >= 5 else self.progress_log
                        for i, log in enumerate(recent_logs):
                            self.console.print(f"[dim]🐛 DEBUG:   -{len(recent_logs)-i}: {log}[/dim]")
                
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
        """Display Claude's output in real-time with appropriate formatting and debug details"""
        # Skip empty lines unless in debug mode
        if not line.strip() and not self.debug_mode:
            return
        
        # In debug mode, show timestamp and raw line info
        if self.debug_mode:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Include milliseconds
            line_info = f"[dim]{timestamp} ({len(line)} chars)[/dim] "
        else:
            line_info = ""
        
        # Color-code different types of output
        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
            self.console.print(f"[red]{line_info}Claude: {line}[/red]")
        elif any(keyword in line.lower() for keyword in ['success', 'complete', 'finished', 'done']):
            self.console.print(f"[green]{line_info}Claude: {line}[/green]")
        elif any(keyword in line.lower() for keyword in ['warning', 'warn']):
            self.console.print(f"[yellow]{line_info}Claude: {line}[/yellow]")
        elif any(keyword in line.lower() for keyword in ['reading', 'writing', 'creating', 'updating', 'editing']):
            self.console.print(f"[cyan]{line_info}Claude: {line}[/cyan]")
        elif any(keyword in line.lower() for keyword in ['running', 'executing', 'processing']):
            self.console.print(f"[blue]{line_info}Claude: {line}[/blue]")
        elif 'claude_code.' in line.lower():
            # Highlight OpenTelemetry events
            self.console.print(f"[magenta]{line_info}OTEL: {line}[/magenta]")
        else:
            if self.verbose_output or self.debug_mode:
                self.console.print(f"[dim]{line_info}Claude: {line}[/dim]")
            elif line.strip():  # Only show non-empty lines in normal mode
                self.console.print(f"[dim]Claude: {line}[/dim]")
    
    def _process_log_line(self, line: str):
        """Process a single log line to extract activity information and OTEL events"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add to progress log
        self.progress_log.append(f"{timestamp} - {line}")
        
        # Keep only last 20 log entries
        if len(self.progress_log) > 20:
            self.progress_log = self.progress_log[-20:]
        
        # Parse OpenTelemetry events for real-time monitoring
        self._parse_otel_event(line)
        
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
    
    def _parse_otel_event(self, line: str):
        """Parse OpenTelemetry events from Claude Code output for real-time monitoring"""
        try:
            # Look for OpenTelemetry log entries
            # Format: timestamp [level] name: attributes
            if 'claude_code.' in line:
                # Extract event type and attributes
                if 'claude_code.user_prompt' in line:
                    self.current_action = "📝 Processing user prompt"
                    self.console.print(f"[blue]🎯 Claude received prompt[/blue]")
                    
                elif 'claude_code.tool_result' in line:
                    # Parse tool result details
                    tool_match = re.search(r'name["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', line)
                    success_match = re.search(r'success["\']?\s*[:=]\s*["\']?(true|false)', line)
                    duration_match = re.search(r'duration_ms["\']?\s*[:=]\s*["\']?(\d+)', line)
                    
                    if tool_match:
                        tool_name = tool_match.group(1)
                        success = success_match.group(1) == 'true' if success_match else True
                        duration = int(duration_match.group(1)) if duration_match else 0
                        
                        status_icon = "✅" if success else "❌"
                        self.current_action = f"🔧 Tool: {tool_name} {status_icon}"
                        self.console.print(f"[{'green' if success else 'red'}]{status_icon} Tool {tool_name} ({'success' if success else 'failed'}) ({duration}ms)[/{'green' if success else 'red'}]")
                        
                elif 'claude_code.api_request' in line:
                    # Parse API request details
                    model_match = re.search(r'model["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', line)
                    tokens_match = re.search(r'input_tokens["\']?\s*[:=]\s*["\']?(\d+)', line)
                    
                    if model_match:
                        model = model_match.group(1)
                        tokens = int(tokens_match.group(1)) if tokens_match else 0
                        self.current_action = f"🤖 API call: {model} ({tokens} tokens)"
                        self.console.print(f"[cyan]🤖 API request to {model} ({tokens} input tokens)[/cyan]")
                        
                elif 'claude_code.api_error' in line:
                    # Parse API error details
                    error_match = re.search(r'error["\']?\s*[:=]\s*["\']?([^"\'}\n]+)', line)
                    if error_match:
                        error = error_match.group(1)
                        self.current_action = f"❌ API Error: {error[:50]}..."
                        self.console.print(f"[red]❌ API Error: {error}[/red]")
                        
                elif 'claude_code.tool_decision' in line:
                    # Parse tool decision details
                    tool_match = re.search(r'tool_name["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', line)
                    decision_match = re.search(r'decision["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', line)
                    
                    if tool_match and decision_match:
                        tool = tool_match.group(1)
                        decision = decision_match.group(1)
                        decision_icon = "✅" if decision == "accept" else "🚫"
                        self.current_action = f"🛡️ Permission: {tool} {decision_icon}"
                        self.console.print(f"[{'green' if decision == 'accept' else 'yellow'}]{decision_icon} Tool permission {decision}: {tool}[/{'green' if decision == 'accept' else 'yellow'}]")
            
            # Also parse standard Claude output for additional context
            elif any(keyword in line.lower() for keyword in ['file:', 'editing', 'creating', 'writing']):
                # Extract file operations
                file_match = re.search(r'([a-zA-Z0-9_/.-]+\.(py|feature|json|md))', line)
                if file_match:
                    filename = file_match.group(1)
                    self.current_file = filename
                    if 'editing' in line.lower():
                        self.current_action = f"✏️ Editing {filename}"
                    elif 'creating' in line.lower():
                        self.current_action = f"📄 Creating {filename}"
                    elif 'writing' in line.lower():
                        self.current_action = f"💾 Writing {filename}"
                        
        except Exception as e:
            # Don't let OTEL parsing errors break the monitoring
            pass
    
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