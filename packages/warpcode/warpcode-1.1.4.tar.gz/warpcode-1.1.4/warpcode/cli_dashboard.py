"""
CLI Dashboard

Provides concise real-time CLI output showing BDD progress, complexity status,
and Claude activity in a clean, readable format.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn

from .scoreboard_manager import ScoreboardManager, BDDStatus, ComplexityStatus, ClaudeStatus


class CLIDashboard:
    """Real-time CLI dashboard for orchestration status"""
    
    def __init__(self, project_dir: Path, scoreboard_manager: ScoreboardManager, 
                 console: Optional[Console] = None):
        self.project_dir = project_dir
        self.scoreboard_manager = scoreboard_manager
        self.console = console or Console()
        self.live_display: Optional[Live] = None
        
    def show_single_line_status(self, iteration: int, bdd_status: Optional[BDDStatus] = None,
                               complexity_status: Optional[ComplexityStatus] = None,
                               claude_status: Optional[ClaudeStatus] = None):
        """Show single-line concise status update"""
        
        # Get current statuses if not provided
        if not bdd_status:
            bdd_status = self.scoreboard_manager.get_bdd_status()
        if not complexity_status:
            complexity_status = self.scoreboard_manager.get_complexity_status()
        if not claude_status:
            claude_status = self.scoreboard_manager.get_claude_status()
        
        # Build status line
        status_parts = [f"[Iter {iteration}]"]
        
        # BDD status
        if bdd_status and bdd_status.total_scenarios > 0:
            if bdd_status.failed == 0 and bdd_status.undefined == 0:
                bdd_text = f"[green]{bdd_status.passed}/{bdd_status.total_scenarios} ✓[/green]"
            else:
                bdd_text = f"[yellow]{bdd_status.passed}/{bdd_status.total_scenarios} ✓[/yellow]"
            status_parts.append(f"BDD: {bdd_text}")
        else:
            status_parts.append("BDD: [dim]0/0[/dim]")
        
        # Complexity status
        if complexity_status and complexity_status.total_functions > 0:
            avg_grade = self.scoreboard_manager._calculate_average_grade(complexity_status.complexity_grades)
            if complexity_status.needs_refactoring:
                complexity_text = f"[yellow]{avg_grade} avg[/yellow]"
            else:
                complexity_text = f"[green]{avg_grade} avg[/green]"
            status_parts.append(f"Complexity: {complexity_text}")
        else:
            status_parts.append("Complexity: [dim]-[/dim]")
        
        # Claude status
        if claude_status:
            if claude_status.status == "working":
                claude_text = f"[blue]Working on {claude_status.current_feature or 'project'}[/blue]"
            elif claude_status.status == "complete":
                claude_text = "[green]COMPLETE ✨[/green]"
            elif claude_status.status == "error":
                claude_text = "[red]ERROR[/red]"
            else:
                claude_text = f"[dim]{claude_status.status}[/dim]"
            
            # Add current file if available
            if claude_status.current_file and claude_status.status == "working":
                claude_text += f" → [dim]{Path(claude_status.current_file).name}[/dim]"
            
            status_parts.append(f"Claude: {claude_text}")
        else:
            status_parts.append("Claude: [dim]idle[/dim]")
        
        # Print status line
        status_line = " | ".join(status_parts)
        self.console.print(status_line)
    
    def show_error_summary(self, bdd_status: Optional[BDDStatus] = None,
                          complexity_status: Optional[ComplexityStatus] = None):
        """Show concise error summary"""
        
        if not bdd_status:
            bdd_status = self.scoreboard_manager.get_bdd_status()
        if not complexity_status:
            complexity_status = self.scoreboard_manager.get_complexity_status()
        
        errors = []
        
        # BDD errors
        if bdd_status:
            if bdd_status.failed_scenarios:
                failed_list = ", ".join(bdd_status.failed_scenarios[:3])
                if len(bdd_status.failed_scenarios) > 3:
                    failed_list += f" (+{len(bdd_status.failed_scenarios) - 3} more)"
                errors.append(f"[red]❌ {bdd_status.failed} scenarios failed: {failed_list}[/red]")
            
            if bdd_status.undefined_steps:
                undefined_list = ", ".join(bdd_status.undefined_steps[:2])
                if len(bdd_status.undefined_steps) > 2:
                    undefined_list += f" (+{len(bdd_status.undefined_steps) - 2} more)"
                errors.append(f"[yellow]🔧 {bdd_status.undefined} steps undefined: {undefined_list}[/yellow]")
        
        # Complexity errors
        if complexity_status and complexity_status.needs_refactoring:
            worst = complexity_status.worst_offenders[:2]
            if worst:
                worst_list = ", ".join([f"{w['function']} ({w['grade']})" for w in worst])
                errors.append(f"[yellow]🔧 High complexity in: {worst_list}[/yellow]")
        
        # Print errors
        for error in errors:
            self.console.print(error)
    
    def create_live_dashboard(self) -> Table:
        """Create live dashboard table"""
        table = Table(title="BDD Claude Orchestrator Dashboard", show_header=True, header_style="bold blue")
        
        table.add_column("Component", style="cyan", width=15)
        table.add_column("Status", style="green", width=20)
        table.add_column("Details", style="white", width=40)
        
        # Get current statuses
        bdd_status = self.scoreboard_manager.get_bdd_status()
        complexity_status = self.scoreboard_manager.get_complexity_status()
        claude_status = self.scoreboard_manager.get_claude_status()
        master_status = self.scoreboard_manager.get_master_status()
        
        # BDD row
        if bdd_status and bdd_status.total_scenarios > 0:
            if bdd_status.failed == 0 and bdd_status.undefined == 0:
                bdd_status_text = f"[green]{bdd_status.passed}/{bdd_status.total_scenarios} passing[/green]"
            else:
                bdd_status_text = f"[yellow]{bdd_status.passed} pass, {bdd_status.failed} fail[/yellow]"
            
            bdd_details = f"{bdd_status.completion_percentage:.1f}% complete"
            if bdd_status.current_feature:
                bdd_details += f" | {bdd_status.current_feature}"
        else:
            bdd_status_text = "[dim]No scenarios[/dim]"
            bdd_details = "Awaiting feature files"
        
        table.add_row("BDD Tests", bdd_status_text, bdd_details)
        
        # Complexity row
        if complexity_status and complexity_status.total_functions > 0:
            avg_grade = self.scoreboard_manager._calculate_average_grade(complexity_status.complexity_grades)
            if complexity_status.needs_refactoring:
                complexity_status_text = f"[yellow]Grade {avg_grade} (needs work)[/yellow]"
            else:
                complexity_status_text = f"[green]Grade {avg_grade} (good)[/green]"
            
            complexity_details = f"{complexity_status.total_functions} functions analyzed"
        else:
            complexity_status_text = "[dim]Not analyzed[/dim]"
            complexity_details = "Awaiting analysis"
        
        table.add_row("Complexity", complexity_status_text, complexity_details)
        
        # Claude row
        if claude_status:
            if claude_status.status == "working":
                claude_status_text = "[blue]Working[/blue]"
                claude_details = f"{claude_status.current_action}"
                if claude_status.current_file:
                    claude_details += f" | {Path(claude_status.current_file).name}"
            elif claude_status.status == "complete":
                claude_status_text = "[green]Complete[/green]"
                claude_details = "Task finished successfully"
            elif claude_status.status == "error":
                claude_status_text = "[red]Error[/red]"
                claude_details = "Execution failed"
            else:
                claude_status_text = f"[dim]{claude_status.status.title()}[/dim]"
                claude_details = claude_status.current_action or "Idle"
        else:
            claude_status_text = "[dim]Idle[/dim]"
            claude_details = "Awaiting instructions"
        
        table.add_row("Claude", claude_status_text, claude_details)
        
        # Overall row
        if master_status:
            if master_status.overall_status == "complete":
                overall_status_text = "[green]Complete[/green]"
                overall_details = "All tests passing!"
            elif master_status.overall_status == "in_progress":
                overall_status_text = f"[blue]Iteration {master_status.iteration}[/blue]"
                overall_details = f"Working on iteration {master_status.iteration}"
            else:
                overall_status_text = f"[yellow]{master_status.overall_status.title()}[/yellow]"
                overall_details = "Setting up..."
        else:
            overall_status_text = "[dim]Initializing[/dim]"
            overall_details = "Starting up..."
        
        table.add_row("Overall", overall_status_text, overall_details)
        
        return table
    
    def start_live_dashboard(self):
        """Start live updating dashboard"""
        self.live_display = Live(
            self.create_live_dashboard(),
            refresh_per_second=1,
            console=self.console
        )
        self.live_display.start()
    
    def update_live_dashboard(self):
        """Update live dashboard content"""
        if self.live_display:
            self.live_display.update(self.create_live_dashboard())
    
    def stop_live_dashboard(self):
        """Stop live dashboard"""
        if self.live_display:
            self.live_display.stop()
            self.live_display = None
    
    def show_progress_bar(self, current: int, total: int, description: str = "Progress"):
        """Show progress bar for current iteration"""
        if total == 0:
            return
        
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        with progress:
            task = progress.add_task(description, total=total)
            progress.update(task, completed=current)
            
    def show_completion_summary(self, iteration: int, total_time: str, success: bool):
        """Show final completion summary"""
        if success:
            panel = Panel(
                Text(f"🎉 BDD ORCHESTRATION COMPLETE! 🎉\n\nCompleted in {iteration} iterations\nTotal time: {total_time}", 
                     style="bold green", justify="center"),
                border_style="green",
                title="Success",
                padding=(1, 2)
            )
        else:
            panel = Panel(
                Text(f"⚠ ORCHESTRATION INCOMPLETE\n\nStopped after {iteration} iterations\nTotal time: {total_time}", 
                     style="bold yellow", justify="center"),
                border_style="yellow", 
                title="Incomplete",
                padding=(1, 2)
            )
        
        self.console.print(panel)