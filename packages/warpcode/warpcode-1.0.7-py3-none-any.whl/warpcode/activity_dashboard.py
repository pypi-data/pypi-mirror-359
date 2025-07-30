"""
Activity Dashboard

Real-time dashboard that displays Claude's progress, BDD status, and overall
orchestration activity in a live updating format.
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.align import Align

from .scoreboard_manager import ScoreboardManager


class ActivityDashboard:
    """Live activity dashboard for real-time orchestration monitoring"""
    
    def __init__(self, project_dir: Path, scoreboard_manager: ScoreboardManager, 
                 console: Optional[Console] = None):
        self.project_dir = project_dir
        self.scoreboard_manager = scoreboard_manager
        self.console = console or Console()
        
        # Dashboard state
        self.is_running = False
        self.dashboard_thread: Optional[threading.Thread] = None
        self.live_display: Optional[Live] = None
        self.update_interval = 1.0  # seconds - faster updates
        
        # Activity tracking
        self.start_time: Optional[datetime] = None
        self.last_activity_time: Optional[datetime] = None
        self.activity_log: List[str] = []
        self.last_update_time: Optional[datetime] = None
        self.heartbeat_count = 0
        
    def start_dashboard(self):
        """Start the live activity dashboard"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_time = datetime.now()
        
        # Create initial layout
        layout = self._create_layout()
        
        # Start live display
        self.live_display = Live(layout, refresh_per_second=0.5, screen=False)
        self.live_display.start()
        
        # Start update thread
        self.dashboard_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.dashboard_thread.start()
        
    def stop_dashboard(self):
        """Stop the live activity dashboard"""
        self.is_running = False
        
        if self.dashboard_thread:
            self.dashboard_thread.join(timeout=5)
            
        if self.live_display:
            self.live_display.stop()
            
    def _create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        # Split into main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main section
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left section
        layout["left"].split_column(
            Layout(name="claude_status"),
            Layout(name="bdd_status")
        )
        
        # Split right section
        layout["right"].split_column(
            Layout(name="activity_log"),
            Layout(name="stats")
        )
        
        return layout
    
    def _update_loop(self):
        """Main update loop for the dashboard"""
        while self.is_running:
            try:
                # Update dashboard layout
                if self.live_display:
                    layout = self._create_updated_layout()
                    self.live_display.update(layout)
                    
                # Track update time and heartbeat
                self.last_update_time = datetime.now()
                self.heartbeat_count += 1
                
                # Log periodic heartbeat to show dashboard is alive
                if self.heartbeat_count % 10 == 0:  # Every 10 seconds
                    self.log_activity(f"Dashboard heartbeat #{self.heartbeat_count // 10}")
                    
                time.sleep(self.update_interval)
                
            except Exception as e:
                # Don't let dashboard errors crash the orchestrator
                self.console.print(f"[red]Dashboard error: {e}[/red]")
                break
    
    def _create_updated_layout(self) -> Layout:
        """Create updated layout with current data"""
        layout = self._create_layout()
        
        # Update header
        layout["header"].update(self._create_header())
        
        # Update Claude status
        layout["claude_status"].update(self._create_claude_status())
        
        # Update BDD status  
        layout["bdd_status"].update(self._create_bdd_status())
        
        # Update activity log
        layout["activity_log"].update(self._create_activity_log())
        
        # Update stats
        layout["stats"].update(self._create_stats())
        
        # Update footer
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel"""
        elapsed = self._get_elapsed_time()
        title = Text("🚀 WARPCODE ACTIVITY DASHBOARD", style="bold cyan")
        subtitle = Text(f"Elapsed: {elapsed}", style="dim")
        
        header_content = Text()
        header_content.append(title)
        header_content.append("\n")
        header_content.append(subtitle)
        
        return Panel(
            Align.center(header_content),
            style="blue",
            height=3
        )
    
    def _create_claude_status(self) -> Panel:
        """Create Claude status panel"""
        claude_data = self._get_claude_status()
        
        content = Text()
        
        if not claude_data:
            content.append("🤖 Claude: ", style="cyan")
            content.append("IDLE", style="dim")
            content.append("\n")
            content.append("No scoreboard data found", style="dim")
        else:
            status = claude_data.get("status", "unknown")
            current_action = claude_data.get("current_action", "")
            current_file = claude_data.get("current_file", "")
            timestamp = claude_data.get("timestamp", "")
            iteration = claude_data.get("iteration", "N/A")
            
            # Status indicator with timestamp
            if status == "working":
                content.append("🤖 Claude: ", style="cyan")
                content.append("ACTIVE", style="bold green")
            elif status == "starting":
                content.append("🤖 Claude: ", style="cyan")
                content.append("INITIALIZING", style="bold yellow")
            elif status == "complete":
                content.append("🤖 Claude: ", style="cyan")
                content.append("COMPLETE", style="bold green")
            elif status == "error":
                content.append("🤖 Claude: ", style="cyan")
                content.append("ERROR", style="bold red")
            else:
                content.append("🤖 Claude: ", style="cyan")
                content.append(status.upper(), style="yellow")
            
            content.append("\n")
            
            # Show iteration and timestamp
            content.append(f"Iteration: {iteration}", style="white")
            if timestamp:
                try:
                    # Parse timestamp and show relative time
                    ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    now = datetime.now(ts.tzinfo)
                    elapsed = now - ts
                    content.append(f" | Updated: {elapsed.total_seconds():.0f}s ago", style="dim")
                except:
                    content.append(f" | {timestamp[-8:]}", style="dim")
            content.append("\n")
            
            # Current action
            if current_action:
                content.append(f"Action: {current_action}", style="white")
                content.append("\n")
            else:
                content.append("Action: Setting up environment", style="white")
                content.append("\n")
                
            # Current file
            if current_file:
                content.append(f"File: {current_file}", style="dim")
                content.append("\n")
                
            # Progress log (last few entries)
            progress_log = claude_data.get("progress_log", [])
            if progress_log:
                content.append("Recent Activity:", style="bold")
                content.append("\n")
                for entry in progress_log[-3:]:  # Show last 3 entries
                    content.append(f"• {entry}", style="dim")
                    content.append("\n")
            else:
                content.append("Recent Activity:", style="bold")
                content.append("\n")
                content.append("• Waiting for Claude output...", style="dim")
        
        return Panel(
            content,
            title="Claude Status",
            border_style="cyan"
        )
    
    def _create_bdd_status(self) -> Panel:
        """Create BDD status panel"""
        bdd_data = self._get_bdd_status()
        
        if not bdd_data:
            content = Text("📊 BDD: No data", style="dim")
        else:
            passed = bdd_data.get("passed", 0)
            failed = bdd_data.get("failed", 0)
            undefined = bdd_data.get("undefined", 0)
            total = bdd_data.get("total_scenarios", 0)
            completion = bdd_data.get("completion_percentage", 0)
            
            content = Text()
            content.append("📊 BDD Test Status", style="bold")
            content.append("\n\n")
            
            # Progress bar
            if total > 0:
                progress = Progress(
                    TextColumn("[bold blue]Progress", justify="right"),
                    BarColumn(bar_width=20),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    expand=True
                )
                progress.add_task("", completed=completion, total=100)
                content.append(f"Progress: {completion:.1f}%", style="bold green")
                content.append("\n")
            
            # Test counts
            content.append(f"Passed: {passed}", style="green")
            content.append(f" | Failed: {failed}", style="red" if failed > 0 else "dim")
            content.append(f" | Undefined: {undefined}", style="yellow" if undefined > 0 else "dim")
            content.append(f" | Total: {total}", style="white")
            
            # Failed scenarios
            failed_scenarios = bdd_data.get("failed_scenarios", [])
            if failed_scenarios:
                content.append("\n\nFailed Scenarios:", style="bold red")
                for scenario in failed_scenarios[:3]:  # Show first 3
                    content.append(f"\n• {scenario}", style="red")
                if len(failed_scenarios) > 3:
                    content.append(f"\n... and {len(failed_scenarios) - 3} more", style="dim")
        
        return Panel(
            content,
            title="BDD Status",
            border_style="green"
        )
    
    def _create_activity_log(self) -> Panel:
        """Create activity log panel"""
        # Get recent activity from scoreboards
        recent_activity = self._get_recent_activity()
        
        content = Text()
        content.append("Recent Activity:", style="bold")
        content.append("\n")
        
        if not recent_activity:
            content.append("No recent activity", style="dim")
        else:
            for entry in recent_activity[-10:]:  # Show last 10 entries
                content.append(f"• {entry}", style="white")
                content.append("\n")
        
        return Panel(
            content,
            title="Activity Log",
            border_style="yellow"
        )
    
    def _create_stats(self) -> Panel:
        """Create statistics panel"""
        stats = self._get_orchestration_stats()
        
        content = Text()
        content.append("Statistics:", style="bold")
        content.append("\n")
        
        content.append(f"Current Iteration: {stats.get('iteration', 'N/A')}", style="white")
        content.append("\n")
        content.append(f"Total Time: {self._get_elapsed_time()}", style="white")
        content.append("\n")
        content.append(f"Environment: {stats.get('environment_status', 'Unknown')}", style="white")
        content.append("\n")
        content.append(f"Scoreboards: {len(self._get_scoreboard_files())} files", style="white")
        
        return Panel(
            content,
            title="Stats",
            border_style="magenta"
        )
    
    def _create_footer(self) -> Panel:
        """Create footer panel"""
        update_time = self.last_update_time.strftime('%H:%M:%S') if self.last_update_time else datetime.now().strftime('%H:%M:%S')
        footer_text = Text(f"🎯 WarpCode - Automated BDD Development | Update: {update_time} | Beat: {self.heartbeat_count}", 
                          style="dim")
        
        return Panel(
            Align.center(footer_text),
            style="dim",
            height=3
        )
    
    def _get_claude_status(self) -> Optional[Dict[str, Any]]:
        """Get current Claude status from scoreboards"""
        try:
            claude_file = self.scoreboard_manager.scoreboards_dir / "claude_status.json"
            if claude_file.exists():
                with open(claude_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def _get_bdd_status(self) -> Optional[Dict[str, Any]]:
        """Get current BDD status from scoreboards"""
        try:
            bdd_file = self.scoreboard_manager.scoreboards_dir / "bdd_status.json"
            if bdd_file.exists():
                with open(bdd_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def _get_recent_activity(self) -> List[str]:
        """Get recent activity from logs"""
        activity = []
        
        # Get Claude progress log
        claude_data = self._get_claude_status()
        if claude_data and "progress_log" in claude_data:
            activity.extend(claude_data["progress_log"])
        
        # Sort by timestamp if available
        return sorted(activity)[-10:]  # Return last 10 items
    
    def _get_orchestration_stats(self) -> Dict[str, Any]:
        """Get overall orchestration statistics"""
        try:
            master_file = self.scoreboard_manager.scoreboards_dir / "master_status.json"
            if master_file.exists():
                with open(master_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _get_scoreboard_files(self) -> List[Path]:
        """Get list of scoreboard files"""
        try:
            return list(self.scoreboard_manager.scoreboards_dir.glob("*.json"))
        except Exception:
            return []
    
    def debug_scoreboards(self):
        """Debug method to check scoreboard status"""
        scoreboards_dir = self.scoreboard_manager.scoreboards_dir
        self.console.print(f"[blue]Scoreboards directory: {scoreboards_dir}[/blue]")
        
        if not scoreboards_dir.exists():
            self.console.print("[red]Scoreboards directory does not exist![/red]")
            return
            
        files = list(scoreboards_dir.glob("*.json"))
        self.console.print(f"[blue]Found {len(files)} scoreboard files:[/blue]")
        
        for file in files:
            try:
                stat = file.stat()
                age = time.time() - stat.st_mtime
                self.console.print(f"  {file.name}: {age:.1f}s old")
                
                if file.name == "claude_status.json":
                    with open(file, 'r') as f:
                        data = json.load(f)
                        self.console.print(f"    Status: {data.get('status', 'unknown')}")
                        self.console.print(f"    Action: {data.get('current_action', 'none')}")
                        
            except Exception as e:
                self.console.print(f"  {file.name}: Error reading - {e}")
    
    def _get_elapsed_time(self) -> str:
        """Get elapsed time since dashboard started"""
        if not self.start_time:
            return "0s"
            
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def log_activity(self, message: str):
        """Log an activity message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"{timestamp} - {message}"
        self.activity_log.append(entry)
        
        # Keep only last 50 entries
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[-50:]
        
        self.last_activity_time = datetime.now()
    
    def force_claude_status_update(self):
        """Force a Claude status update for testing"""
        from .scoreboard_manager import ClaudeStatus
        
        test_status = ClaudeStatus(
            timestamp=datetime.now().isoformat(),
            iteration=1,
            status="working", 
            current_feature="test.feature",
            current_file="test.py",
            current_action="Testing dashboard updates",
            progress_log=[f"{datetime.now().strftime('%H:%M:%S')} - Dashboard test update"],
            estimated_completion=None
        )
        
        self.scoreboard_manager.update_claude_status(test_status)
        self.log_activity("Force updated Claude status for testing")