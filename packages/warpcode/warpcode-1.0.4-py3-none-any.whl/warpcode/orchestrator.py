"""
Orchestrator

Main automation loop that coordinates all components to achieve 100% BDD test coverage
with zero human intervention.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text

from .environment_manager import EnvironmentManager
from .scoreboard_manager import ScoreboardManager
from .bdd_runner import BDDRunner, BDDResults
from .claude_interface import ClaudeInterface
from .activity_dashboard import ActivityDashboard


class Orchestrator:
    """Main orchestration controller for automated BDD development"""
    
    def __init__(self, project_dir: Path, max_iterations: int = 10, 
                 claude_timeout_minutes: int = 30, enable_dashboard: bool = True):
        self.project_dir = project_dir
        self.max_iterations = max_iterations
        self.claude_timeout_minutes = claude_timeout_minutes
        self.enable_dashboard = enable_dashboard
        self.console = Console()
        
        # Component managers
        self.environment_manager = EnvironmentManager(project_dir, self.console)
        self.scoreboard_manager = ScoreboardManager(project_dir)
        self.bdd_runner = BDDRunner(project_dir, self.environment_manager, self.scoreboard_manager, self.console)
        self.claude_interface = ClaudeInterface(project_dir, self.scoreboard_manager, self.console)
        self.activity_dashboard = ActivityDashboard(project_dir, self.scoreboard_manager, self.console) if enable_dashboard else None
        
        # Orchestration state
        self.current_iteration = 1
        self.start_time: Optional[datetime] = None
        self.total_time: Optional[timedelta] = None
        self.final_results: Optional[BDDResults] = None
        
    def run(self) -> bool:
        """Main orchestration loop - returns True if all tests pass"""
        try:
            self.start_time = datetime.now()
            self.console.print("\n[bold blue]🚀 Starting BDD Claude Orchestrator[/bold blue]\n")
            
            # Phase 1: Environment Setup
            if not self._setup_environment():
                return False
            
            # Phase 2: Initial Validation
            if not self._validate_setup():
                return False
            
            # Phase 3: Main Orchestration Loop
            success = self._run_orchestration_loop()
            
            # Phase 4: Final Summary
            self._show_final_summary(success)
            
            return success
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]🛑 Orchestration interrupted by user[/yellow]")
            self._cleanup()
            return False
        except Exception as e:
            self.console.print(f"\n\n[red]💥 Orchestration failed: {e}[/red]")
            self._cleanup()
            return False
    
    def _setup_environment(self) -> bool:
        """Setup the development environment"""
        self.console.print("[bold]Phase 1: Environment Setup[/bold]")
        
        # Check if environment is already set up
        if self.environment_manager.is_environment_ready():
            status = self.environment_manager.get_environment_status()
            self.console.print("[green]✓ Environment already set up[/green]")
            venv_name = Path(status["venv_path"]).name
            if status.get("venv_python_version"):
                self.console.print(f"[green]✓ Using virtual environment: {venv_name} ({status['venv_python_version']})[/green]")
            else:
                self.console.print(f"[green]✓ Using virtual environment: {venv_name}[/green]")
        else:
            # Setup complete environment
            if not self.environment_manager.setup_complete_environment():
                self.console.print("[red]✗ Environment setup failed[/red]")
                return False
        
        # Initialize scoreboards
        self.scoreboard_manager.create_initial_scoreboards(self.current_iteration)
        self.console.print("[green]✓ Scoreboards initialized[/green]")
        
        return True
    
    def _validate_setup(self) -> bool:
        """Validate that everything is properly configured"""
        self.console.print("\n[bold]Phase 2: Validation[/bold]")
        
        # Check BDD setup
        is_valid, issues = self.bdd_runner.validate_bdd_setup()
        if not is_valid:
            self.console.print("[red]✗ BDD setup validation failed:[/red]")
            for issue in issues:
                self.console.print(f"  - {issue}")
            return False
        
        self.console.print("[green]✓ BDD setup validated[/green]")
        
        # Check Claude availability
        if not self.claude_interface.check_claude_availability():
            return False
        
        return True
    
    def _run_orchestration_loop(self) -> bool:
        """Main orchestration loop"""
        self.console.print("\n[bold]Phase 3: Orchestration Loop[/bold]")
        
        # Start activity dashboard if enabled
        if self.activity_dashboard:
            self.console.print("[blue]🎯 Starting live activity dashboard...[/blue]")
            self.activity_dashboard.start_dashboard()
            self.activity_dashboard.log_activity("Orchestration loop started")
        
        # Show initial status
        self._show_iteration_header(self.current_iteration)
        
        for iteration in range(1, self.max_iterations + 1):
            self.current_iteration = iteration
            self.claude_interface.set_iteration(iteration)
            
            self.console.print(f"\n[bold cyan]━━━ Iteration {iteration} ━━━[/bold cyan]")
            
            # Log iteration start
            if self.activity_dashboard:
                self.activity_dashboard.log_activity(f"Starting iteration {iteration}")
            
            # Step 1: Run BDD tests
            self.console.print(f"[blue]📊 Running BDD tests...[/blue]")
            if self.activity_dashboard:
                self.activity_dashboard.log_activity("Running BDD tests")
            
            bdd_results = self.bdd_runner.run_behave_tests(use_progress_format=True)
            self.bdd_runner.update_scoreboard(bdd_results, iteration)
            
            # Show current status
            self._show_iteration_status(bdd_results)
            
            # Step 2: Check if all tests pass
            if self.bdd_runner.check_if_all_tests_pass(bdd_results):
                self.console.print(f"\n[bold green]🎉 All tests passing! Orchestration complete.[/bold green]")
                if self.activity_dashboard:
                    self.activity_dashboard.log_activity("All tests passing - orchestration complete!")
                self.final_results = bdd_results
                return True
            
            # Step 3: Prepare Claude prompt
            bdd_summary = self.bdd_runner.get_behave_summary_for_claude(bdd_results)
            claude_prompt = self.claude_interface.create_claude_prompt(
                bdd_summary=bdd_summary,
                iteration=iteration
            )
            
            # Step 4: Run Claude
            self.console.print(f"[blue]🤖 Running Claude Coder (iteration {iteration})...[/blue]")
            if not self.activity_dashboard:
                self.console.print(f"[dim]Real-time output from Claude:[/dim]")
            
            if self.activity_dashboard:
                self.activity_dashboard.log_activity(f"Starting Claude execution for iteration {iteration}")
            
            # Reset Claude status for new iteration
            self.claude_interface.reset_status()
            
            claude_success = self.claude_interface.run_claude_automated(
                prompt=claude_prompt,
                timeout_minutes=self.claude_timeout_minutes
            )
            
            # Show completion status
            if claude_success:
                self.console.print(f"[green]✓ Claude completed iteration {iteration}[/green]")
                if self.activity_dashboard:
                    self.activity_dashboard.log_activity(f"Claude completed iteration {iteration} successfully")
            else:
                self.console.print(f"[yellow]⚠ Claude had issues in iteration {iteration}[/yellow]")
                if self.activity_dashboard:
                    self.activity_dashboard.log_activity(f"Claude had issues in iteration {iteration}")
            
            if not claude_success:
                self.console.print(f"[yellow]⚠ Claude execution failed in iteration {iteration}[/yellow]")
                # Continue to next iteration - Claude might have made partial progress
            
            # Step 5: Update master scoreboard
            self.scoreboard_manager.aggregate_master_status(iteration, "in_progress")
            
            # Step 6: Brief pause between iterations
            time.sleep(2)
        
        # If we reach here, we've exceeded max iterations
        self.console.print(f"\n[yellow]⚠ Maximum iterations ({self.max_iterations}) reached[/yellow]")
        
        # Run final test to see current status
        final_results = self.bdd_runner.run_behave_tests(use_progress_format=False)
        self.final_results = final_results
        
        # Update final status
        self.scoreboard_manager.aggregate_master_status(
            self.current_iteration, 
            "complete" if self.bdd_runner.check_if_all_tests_pass(final_results) else "incomplete"
        )
        
        return self.bdd_runner.check_if_all_tests_pass(final_results)
    
    def _show_iteration_header(self, iteration: int):
        """Show iteration header with current status"""
        header_text = f"BDD Claude Orchestrator - Iteration {iteration}"
        header_panel = Panel(
            Text(header_text, style="bold cyan"),
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(header_panel)
    
    def _show_iteration_status(self, results: BDDResults):
        """Show concise iteration status"""
        if results.total_scenarios == 0:
            status_text = f"[yellow]📊 No scenarios found[/yellow]"
        else:
            passed_color = "green" if results.passed > 0 else "dim"
            failed_color = "red" if results.failed > 0 else "dim"
            undefined_color = "yellow" if results.undefined > 0 else "dim"
            
            status_text = (
                f"[{passed_color}]{results.passed} passed[/{passed_color}] | "
                f"[{failed_color}]{results.failed} failed[/{failed_color}] | "
                f"[{undefined_color}]{results.undefined} undefined[/{undefined_color}] | "
                f"[dim]{results.skipped} skipped[/dim]"
            )
            
            if results.completion_percentage > 0:
                status_text += f" | [{passed_color}]{results.completion_percentage:.1f}% complete[/{passed_color}]"
        
        self.console.print(f"📊 BDD Status: {status_text}")
        
        # Show failed scenarios if any
        if results.failed_scenarios:
            failed_list = ", ".join(results.failed_scenarios[:3])
            if len(results.failed_scenarios) > 3:
                failed_list += f" (and {len(results.failed_scenarios) - 3} more)"
            self.console.print(f"[red]❌ Failed: {failed_list}[/red]")
        
        # Show undefined steps if any
        if results.undefined_steps:
            undefined_list = ", ".join(results.undefined_steps[:2])
            if len(results.undefined_steps) > 2:
                undefined_list += f" (and {len(results.undefined_steps) - 2} more)"
            self.console.print(f"[yellow]🔧 Undefined: {undefined_list}[/yellow]")
    
    def _show_final_summary(self, success: bool):
        """Show final orchestration summary"""
        self.total_time = datetime.now() - self.start_time
        
        # Stop activity dashboard before showing summary
        if self.activity_dashboard:
            self.activity_dashboard.log_activity("Orchestration complete - showing final summary")
            self.activity_dashboard.stop_dashboard()
        
        self.console.print("\n" + "=" * 60)
        
        if success:
            summary_panel = Panel(
                Text("🎉 BDD ORCHESTRATION COMPLETE! 🎉", style="bold green"),
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(summary_panel)
            
            if self.final_results:
                self.console.print(f"[green]✓ All {self.final_results.total_scenarios} scenarios passing[/green]")
                self.console.print(f"[green]✓ {self.final_results.passed} tests successful[/green]")
        else:
            summary_panel = Panel(
                Text("⚠ BDD ORCHESTRATION INCOMPLETE", style="bold yellow"),
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(summary_panel)
            
            if self.final_results:
                self.console.print(f"[yellow]📊 Final status: {self.final_results.passed} passed, {self.final_results.failed} failed, {self.final_results.undefined} undefined[/yellow]")
        
        # Show statistics
        self.console.print(f"\n[blue]📈 Statistics:[/blue]")
        self.console.print(f"  Total iterations: {self.current_iteration}")
        self.console.print(f"  Total time: {self._format_duration(self.total_time)}")
        self.console.print(f"  Average per iteration: {self._format_duration(self.total_time / self.current_iteration)}")
        
        # Show scoreboards location
        self.console.print(f"\n[blue]📊 Scoreboards saved to:[/blue]")
        self.console.print(f"  {self.scoreboard_manager.scoreboards_dir}")
        
        # Show next steps if not successful
        if not success and self.final_results:
            self.console.print(f"\n[blue]🔧 Next steps:[/blue]")
            if self.final_results.failed_scenarios:
                self.console.print("  - Review failed scenarios and fix implementations")
            if self.final_results.undefined_steps:
                self.console.print("  - Implement undefined step definitions")
            self.console.print("  - Run orchestrator again to continue from current state")
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable form"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def _cleanup(self):
        """Cleanup resources and update final status"""
        try:
            # Stop activity dashboard
            if self.activity_dashboard:
                self.activity_dashboard.log_activity("Orchestration interrupted - cleaning up")
                self.activity_dashboard.stop_dashboard()
            
            # Terminate any running Claude process
            if self.claude_interface.is_claude_running():
                self.claude_interface._terminate_claude()
            
            # Update final master status
            self.scoreboard_manager.aggregate_master_status(
                self.current_iteration, 
                "interrupted"
            )
            
        except Exception:
            pass  # Ignore cleanup errors
    
    def get_status_summary(self) -> Dict:
        """Get current orchestration status summary"""
        return {
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "elapsed_time": self._format_duration(datetime.now() - self.start_time) if self.start_time else None,
            "environment_ready": self.environment_manager.is_environment_ready(),
            "claude_running": self.claude_interface.is_claude_running(),
            "scoreboards_dir": str(self.scoreboard_manager.scoreboards_dir)
        }