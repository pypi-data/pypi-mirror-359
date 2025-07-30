"""
Claude OpenTelemetry Monitor

Monitors Claude Code execution using OpenTelemetry console output
to provide real-time feedback on what Claude is actually doing.
"""

import os
import subprocess
import threading
import tempfile
import time
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from rich.console import Console


@dataclass
class ClaudeEvent:
    """Represents a Claude OpenTelemetry event"""
    timestamp: str
    event_name: str
    attributes: Dict[str, any]
    raw_log: str


class ClaudeOTELMonitor:
    """Monitors Claude Code using OpenTelemetry console output"""
    
    def __init__(self, project_dir: Path, console: Optional[Console] = None):
        self.project_dir = project_dir
        self.console = console or Console()
        
        # Process management
        self.claude_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        
        # Event tracking
        self.events: List[ClaudeEvent] = []
        self.current_status = "idle"
        self.current_activity = ""
        self.last_event_time = None
        
        # Callbacks
        self.on_event_callback: Optional[Callable[[ClaudeEvent], None]] = None
        self.on_status_change_callback: Optional[Callable[[str, str], None]] = None
    
    def set_event_callback(self, callback: Callable[[ClaudeEvent], None]):
        """Set callback for when new events are received"""
        self.on_event_callback = callback
    
    def set_status_change_callback(self, callback: Callable[[str, str], None]):
        """Set callback for when status changes"""
        self.on_status_change_callback = callback
    
    def run_claude_with_monitoring(self, prompt: str, timeout_minutes: int = 30) -> bool:
        """Run Claude with full OpenTelemetry monitoring"""
        
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            # Set up OpenTelemetry environment for Claude
            env = os.environ.copy()
            env.update({
                'CLAUDE_CODE_ENABLE_TELEMETRY': '1',
                'OTEL_LOGS_EXPORTER': 'console',
                'OTEL_LOGS_EXPORT_INTERVAL': '1000',  # 1 second
                'OTEL_LOG_USER_PROMPTS': '1',  # Enable prompt logging
            })
            
            # Claude command for interactive session
            cmd = [
                'claude',
                '--dangerously-skip-permissions',
                f'@{prompt_file}'  # Use file input for better handling
            ]
            
            self.console.print(f"[blue]🤖 Starting Claude with OpenTelemetry monitoring...[/blue]")
            self._update_status("starting", "Initializing Claude session")
            
            # Start Claude process
            self.claude_process = subprocess.Popen(
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
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_otel_output, daemon=True)
            self.monitor_thread.start()
            
            # Wait for completion with timeout
            try:
                start_time = time.time()
                while self.claude_process.poll() is None:
                    elapsed = time.time() - start_time
                    if elapsed > (timeout_minutes * 60):
                        self.console.print(f"[red]⚠ Claude timed out after {timeout_minutes} minutes[/red]")
                        self._terminate_claude()
                        return False
                    
                    time.sleep(1)
                
                success = self.claude_process.returncode == 0
                
                if success:
                    self.console.print("[green]✓ Claude completed successfully[/green]")
                    self._update_status("complete", "Task completed successfully")
                else:
                    self.console.print(f"[yellow]⚠ Claude exited with code {self.claude_process.returncode}[/yellow]")
                    self._update_status("error", f"Exited with code {self.claude_process.returncode}")
                
                return success
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupting Claude...[/yellow]")
                self._terminate_claude()
                return False
            
        finally:
            # Cleanup
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            # Remove temporary file
            try:
                os.unlink(prompt_file)
            except:
                pass
    
    def _monitor_otel_output(self):
        """Monitor OpenTelemetry console output from Claude"""
        if not self.claude_process or not self.claude_process.stdout:
            return
        
        try:
            for line in iter(self.claude_process.stdout.readline, ''):
                if not self.is_monitoring:
                    break
                
                line = line.strip()
                if line:
                    self._process_otel_line(line)
                    
        except Exception as e:
            self.console.print(f"[red]Error monitoring Claude output: {e}[/red]")
    
    def _process_otel_line(self, line: str):
        """Process a line of OpenTelemetry output"""
        try:
            # Look for Claude events in the output
            event = self._parse_claude_event(line)
            if event:
                self.events.append(event)
                self.last_event_time = datetime.now()
                
                # Update status based on event
                self._handle_event(event)
                
                # Call callback if set
                if self.on_event_callback:
                    self.on_event_callback(event)
            
            # Also show regular Claude output
            if not self._is_otel_log(line):
                self._display_claude_output(line)
                
        except Exception as e:
            # Don't let parsing errors break monitoring
            self._display_claude_output(line)
    
    def _parse_claude_event(self, line: str) -> Optional[ClaudeEvent]:
        """Parse Claude OpenTelemetry event from log line"""
        
        # Look for structured log output patterns
        # OpenTelemetry console exporter outputs in specific formats
        
        # Pattern 1: JSON-like structured logs
        if '"event.name"' in line or '"claude_code.' in line:
            try:
                # Try to extract JSON from the line
                json_match = re.search(r'\{.*\}', line)
                if json_match:
                    event_data = json.loads(json_match.group())
                    
                    event_name = event_data.get('event.name', 'unknown')
                    timestamp = event_data.get('event.timestamp', datetime.now().isoformat())
                    
                    return ClaudeEvent(
                        timestamp=timestamp,
                        event_name=event_name,
                        attributes=event_data,
                        raw_log=line
                    )
            except:
                pass
        
        # Pattern 2: Key-value pair logs
        if any(keyword in line for keyword in ['claude_code.', 'tool_result', 'api_request', 'user_prompt']):
            # Extract basic info from key-value format
            timestamp = datetime.now().isoformat()
            
            if 'claude_code.user_prompt' in line:
                event_name = 'user_prompt'
            elif 'claude_code.tool_result' in line:
                event_name = 'tool_result'
            elif 'claude_code.api_request' in line:
                event_name = 'api_request'
            elif 'claude_code.api_error' in line:
                event_name = 'api_error'
            else:
                event_name = 'activity'
            
            # Simple attribute extraction
            attributes = {'raw_line': line}
            
            # Extract tool name if present
            tool_match = re.search(r'tool["\']?\s*[:=]\s*["\']?([^"\'\\s,}]+)', line, re.IGNORECASE)
            if tool_match:
                attributes['tool_name'] = tool_match.group(1)
            
            # Extract success status
            if 'success' in line.lower():
                if 'true' in line.lower() or 'success' in line.lower():
                    attributes['success'] = 'true'
                else:
                    attributes['success'] = 'false'
            
            return ClaudeEvent(
                timestamp=timestamp,
                event_name=event_name,
                attributes=attributes,
                raw_log=line
            )
        
        return None
    
    def _handle_event(self, event: ClaudeEvent):
        """Handle a parsed Claude event"""
        
        if event.event_name == 'user_prompt':
            self._update_status("processing", "Processing user prompt")
            
        elif event.event_name == 'tool_result':
            tool_name = event.attributes.get('tool_name', 'unknown tool')
            success = event.attributes.get('success', 'unknown')
            
            if success == 'true':
                self._update_status("working", f"Successfully executed {tool_name}")
            else:
                self._update_status("working", f"Failed to execute {tool_name}")
                
        elif event.event_name == 'api_request':
            model = event.attributes.get('model', 'Claude')
            self._update_status("thinking", f"API request to {model}")
            
        elif event.event_name == 'api_error':
            error = event.attributes.get('error', 'Unknown error')
            self._update_status("error", f"API error: {error}")
    
    def _is_otel_log(self, line: str) -> bool:
        """Check if line is OpenTelemetry log output"""
        otel_indicators = [
            'ResourceLogs',
            'ScopeLogs', 
            'LogRecord',
            'claude_code.',
            'event.name',
            'event.timestamp'
        ]
        return any(indicator in line for indicator in otel_indicators)
    
    def _display_claude_output(self, line: str):
        """Display Claude's regular output with color coding"""
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
    
    def _update_status(self, status: str, activity: str):
        """Update current status and activity"""
        if self.current_status != status or self.current_activity != activity:
            self.current_status = status
            self.current_activity = activity
            
            if self.on_status_change_callback:
                self.on_status_change_callback(status, activity)
    
    def _terminate_claude(self):
        """Terminate Claude process"""
        if self.claude_process:
            try:
                self.claude_process.terminate()
                self.claude_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.claude_process.kill()
                self.claude_process.wait()
            except Exception:
                pass
    
    def get_recent_events(self, limit: int = 10) -> List[ClaudeEvent]:
        """Get recent Claude events"""
        return self.events[-limit:] if self.events else []
    
    def get_status_summary(self) -> Dict[str, any]:
        """Get current status summary"""
        return {
            "status": self.current_status,
            "activity": self.current_activity,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "total_events": len(self.events),
            "is_running": self.claude_process and self.claude_process.poll() is None
        }