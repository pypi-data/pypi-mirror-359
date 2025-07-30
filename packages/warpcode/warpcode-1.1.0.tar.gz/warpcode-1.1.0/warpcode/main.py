#!/usr/bin/env python3
"""
WarpCode - Main CLI Entry Point

Warp through development cycles with automated BDD development using Claude Coder.
Zero human intervention required - just define your mission and let WarpCode
orchestrate until 100% test coverage is achieved.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from . import __version__


class WarpCode:
    def __init__(self):
        self.console = Console()
        self.project_dir = Path.cwd()
        
    def show_startup_banner(self):
        """Display animated ASCII art startup banner"""
        ascii_file = Path(__file__).parent / "ascii_art" / "startup.txt"
        
        if ascii_file.exists():
            ascii_art = ascii_file.read_text()
        else:
            ascii_art = "🚀 WarpCode v{} 🚀".format(__version__)
        
        # Create animated banner with rich
        banner_text = Text(ascii_art, style="bold cyan")
        banner_panel = Panel(
            Align.center(banner_text),
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(banner_panel)
        self.console.print()
        
        # Animated loading effect
        with self.console.status("[bold green]Initializing WarpCode...", spinner="dots") as status:
            time.sleep(2)
            status.update("[bold green]Loading configuration...")
            time.sleep(1)
            status.update("[bold green]Checking dependencies...")
            time.sleep(1)
            status.update("[bold green]Ready to warp! 🚀")
            time.sleep(1)
    
    def show_main_menu(self) -> str:
        """Display the main questionary menu and return user choice"""
        choices = [
            "🚀 Quick Start (Full Automation)",
            "📝 Create Mission & Generate Features",
            "⚙️  Configure Project Settings", 
            "📊 Set Complexity Thresholds",
            "🔧 Enable/Disable Features",
            "📋 View Current Status",
            "❌ Exit"
        ]
        
        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:#673ab7 bold'),
                ('question', 'bold'),
                ('answer', 'fg:#f44336 bold'),
                ('pointer', 'fg:#673ab7 bold'),
                ('highlighted', 'fg:#673ab7 bold'),
                ('selected', 'fg:#cc5454'),
                ('separator', 'fg:#cc5454'),
                ('instruction', ''),
                ('text', ''),
                ('disabled', 'fg:#858585 italic')
            ])
        ).ask()
        
        return choice
    
    def quick_start(self):
        """Execute quick start with full automation"""
        self.console.print("\n[bold green]🚀 Starting Full Automation Mode[/bold green]")
        self.console.print("[dim]This will run completely autonomously until all BDD tests pass...[/dim]\n")
        
        # Check if we have feature files, if not, offer to create from mission
        features_dir = self.project_dir / "features"
        feature_files = list(features_dir.glob("*.feature")) if features_dir.exists() else []
        
        if not feature_files:
            self.console.print("[yellow]⚠ No .feature files found![/yellow]")
            create_features = questionary.confirm(
                "Would you like to create features from a mission.md file first?",
                default=True
            ).ask()
            
            if create_features:
                if not self.create_mission_and_features():
                    return
        
        # Confirm the user wants to proceed
        proceed = questionary.confirm(
            "This will create a virtual environment and run Claude Coder automatically. Continue?",
            default=True
        ).ask()
        
        if proceed:
            # Ask about dashboard preference
            enable_dashboard = questionary.confirm(
                "Enable live activity dashboard? (Shows real-time Claude progress)",
                default=True
            ).ask()
            
            from .orchestrator import Orchestrator
            orchestrator = Orchestrator(self.project_dir, enable_dashboard=enable_dashboard)
            orchestrator.run()
        else:
            self.console.print("[yellow]Quick start cancelled.[/yellow]")
    
    def configure_settings(self):
        """Configure project settings interactively"""
        self.console.print("\n[bold blue]⚙️  Project Configuration[/bold blue]")
        
        # Get project details
        project_name = questionary.text(
            "Project name:",
            default=self.project_dir.name
        ).ask()
        
        max_iterations = questionary.text(
            "Maximum iterations:",
            default="10",
            validate=lambda text: text.isdigit() and int(text) > 0
        ).ask()
        
        claude_model = questionary.select(
            "Claude model to use:",
            choices=[
                "claude-sonnet-4-20250514",     # Latest Claude 4 Sonnet (May 2025)
                "claude-opus-4-20250514",       # Latest Claude 4 Opus (May 2025)
                "claude-3-5-sonnet-20241022",   # Claude 3.5 Sonnet (fallback)
                "claude-3-5-haiku-20241022"     # Claude 3.5 Haiku (fast/cheap)
            ]
        ).ask()
        
        # Save configuration
        config = {
            "project_name": project_name,
            "max_iterations": int(max_iterations),
            "claude_model": claude_model
        }
        
        self.console.print(f"\n[green]✓ Configuration saved: {config}[/green]")
    
    def set_complexity_thresholds(self):
        """Set code complexity thresholds"""
        self.console.print("\n[bold blue]📊 Complexity Threshold Configuration[/bold blue]")
        
        warning_grade = questionary.select(
            "Warning complexity grade:",
            choices=["A", "B", "C", "D", "E", "F"],
            default="C"
        ).ask()
        
        fail_grade = questionary.select(
            "Fail complexity grade:",
            choices=["A", "B", "C", "D", "E", "F"],
            default="F"
        ).ask()
        
        max_complexity = questionary.text(
            "Maximum function complexity:",
            default="10",
            validate=lambda text: text.isdigit() and int(text) > 0
        ).ask()
        
        self.console.print(f"\n[green]✓ Complexity thresholds set: Warning={warning_grade}, Fail={fail_grade}, Max={max_complexity}[/green]")
    
    def toggle_features(self):
        """Enable/disable features"""
        self.console.print("\n[bold blue]🔧 Feature Configuration[/bold blue]")
        
        features = questionary.checkbox(
            "Select features to enable:",
            choices=[
                "Screenshot capture for UI tests",
                "Mock detection and prevention", 
                "Dependency management",
                "Real-time complexity monitoring",
                "Automatic backup creation",
                "Web dashboard (future)"
            ],
            default=["Screenshot capture for UI tests", "Mock detection and prevention", "Dependency management"]
        ).ask()
        
        self.console.print(f"\n[green]✓ Features configured: {len(features)} enabled[/green]")
    
    def create_mission_and_features(self) -> bool:
        """Create mission.md and generate BDD feature files from it"""
        self.console.print("\n[bold blue]📝 Mission & Feature Generation[/bold blue]")
        
        mission_file = self.project_dir / "mission.md"
        
        # Check if mission.md already exists
        if mission_file.exists():
            self.console.print(f"[green]✓ Found existing mission.md[/green]")
            use_existing = questionary.confirm(
                "Use existing mission.md file?",
                default=True
            ).ask()
            
            if not use_existing:
                # Let user edit the mission
                return self._edit_mission_file(mission_file)
        else:
            # Create new mission.md
            self.console.print("[yellow]No mission.md found. Let's create one![/yellow]")
            return self._create_new_mission_file(mission_file)
        
        # Generate features from existing mission
        return self._generate_features_from_mission(mission_file)
    
    def _create_new_mission_file(self, mission_file: Path) -> bool:
        """Create a new mission.md file"""
        self.console.print("\n[blue]Creating mission.md...[/blue]")
        
        project_name = questionary.text(
            "What is your project name?",
            default=self.project_dir.name
        ).ask()
        
        project_description = questionary.text(
            "Brief description of your project:",
            default="A web application"
        ).ask()
        
        main_goal = questionary.text(
            "What is the main goal/purpose of this project?",
            default="Provide users with a platform to..."
        ).ask()
        
        key_features = questionary.text(
            "Key features (comma-separated):",
            default="user registration, authentication, dashboard"
        ).ask()
        
        target_users = questionary.text(
            "Who are the target users?",
            default="General users, administrators"
        ).ask()
        
        # Create mission.md content
        mission_content = f"""# {project_name} - Project Mission

## Project Overview
{project_description}

## Main Goal
{main_goal}

## Key Features
{key_features}

## Target Users
{target_users}

## Success Criteria
- Users can successfully complete core workflows
- System is reliable and performant
- User experience is intuitive and smooth

## Technical Requirements
- Web-based application
- Responsive design for mobile and desktop
- Secure user authentication and data handling
- Real-time updates where applicable

## Constraints
- Must be maintainable and scalable
- Follow security best practices
- Provide clear error handling and user feedback
"""
        
        mission_file.write_text(mission_content)
        self.console.print(f"[green]✓ Created {mission_file}[/green]")
        
        # Ask if user wants to edit it
        edit_mission = questionary.confirm(
            "Would you like to edit the mission file before generating features?",
            default=False
        ).ask()
        
        if edit_mission:
            self.console.print(f"[blue]Please edit {mission_file} and press Enter when done...[/blue]")
            questionary.press_any_key_to_continue().ask()
        
        return self._generate_features_from_mission(mission_file)
    
    def _edit_mission_file(self, mission_file: Path) -> bool:
        """Let user edit existing mission file"""
        self.console.print(f"[blue]Please edit {mission_file} and press Enter when done...[/blue]")
        questionary.press_any_key_to_continue().ask()
        return self._generate_features_from_mission(mission_file)
    
    def _generate_features_from_mission(self, mission_file: Path) -> bool:
        """Generate BDD feature files from mission.md using Claude"""
        if not mission_file.exists():
            self.console.print("[red]✗ Mission file not found[/red]")
            return False
        
        mission_content = mission_file.read_text()
        
        # Create prompt for Claude to generate features
        claude_prompt = f"""# BDD Feature Generation from Mission

Please analyze the following project mission and generate BDD feature files using proper BDD project structure.

## Mission:
{mission_content}

## IMPORTANT: BDD Directory Structure
FIRST, create the proper BDD directory structure:
1. Create a `features/` directory in the project root
2. Create a `features/steps/` subdirectory for step definitions
3. Place ALL .feature files inside the `features/` directory (NOT in project root)

## Instructions:
1. Create separate .feature files for different functional areas/concerns
2. Focus on happy path and minimal viable functionality only
3. Use proper Gherkin syntax (Feature, Scenario, Given, When, Then)
4. Keep scenarios simple and focused on core user value
5. Separate concerns into different .feature files (auth, user management, core features, etc.)
6. Do NOT create step definition files - only .feature files
7. Make scenarios realistic and testable
8. **CRITICAL**: All .feature files MUST be created inside the `features/` directory

## Output Format:
Create the following directory structure:
```
features/
├── steps/                     (empty directory for future step definitions)
├── user_authentication.feature
├── user_registration.feature  
├── dashboard.feature
└── [other logical groupings].feature
```

Each .feature file should have:
- Clear Feature description
- 2-5 simple scenarios covering the core happy path
- Realistic Given/When/Then steps that can be implemented

**REMINDER**: All .feature files go in features/ directory, NOT in project root!

Focus on what users actually need to accomplish, not technical implementation details.
"""
        
        self.console.print("[blue]🤖 Generating BDD features from mission using Claude...[/blue]")
        
        # Use Claude interface to generate features
        from .claude_interface import ClaudeInterface
        from .scoreboard_manager import ScoreboardManager
        
        scoreboard_manager = ScoreboardManager(self.project_dir)
        claude_interface = ClaudeInterface(self.project_dir, scoreboard_manager, self.console)
        
        # Check Claude availability
        if not claude_interface.check_claude_availability():
            self.console.print("[red]✗ Claude Code CLI not available[/red]")
            return False
        
        # Run Claude to generate features
        success = claude_interface.run_claude_automated(
            prompt=claude_prompt,
            timeout_minutes=10
        )
        
        if success:
            # Check if feature files were created
            features_dir = self.project_dir / "features"
            if features_dir.exists():
                feature_files = list(features_dir.glob("*.feature"))
                if feature_files:
                    self.console.print(f"[green]✓ Generated {len(feature_files)} feature files:[/green]")
                    for feature_file in feature_files:
                        self.console.print(f"  - {feature_file.name}")
                    return True
            
            self.console.print("[yellow]⚠ Claude completed but no feature files found[/yellow]")
            return False
        else:
            self.console.print("[red]✗ Failed to generate features with Claude[/red]")
            return False
    
    def view_status(self):
        """View current project status"""
        self.console.print("\n[bold blue]📋 Current Status[/bold blue]")
        
        scoreboards_dir = self.project_dir / "scoreboards"
        if scoreboards_dir.exists():
            self.console.print("[green]✓ Scoreboards directory exists[/green]")
            
            # Check for existing scoreboard files
            files = list(scoreboards_dir.glob("*.json"))
            if files:
                self.console.print(f"[green]✓ Found {len(files)} scoreboard files[/green]")
                for file in files:
                    self.console.print(f"  - {file.name}")
            else:
                self.console.print("[yellow]No scoreboard files found[/yellow]")
        else:
            self.console.print("[yellow]No scoreboards directory found - project not initialized[/yellow]")
    
    def run(self, args: Optional[argparse.Namespace] = None):
        """Main application entry point"""
        # Show startup banner
        self.show_startup_banner()
        
        # Handle command line arguments
        if args and args.quick_start:
            self.quick_start()
            return
        
        # Show main menu loop
        while True:
            try:
                choice = self.show_main_menu()
                
                if not choice:  # User pressed Ctrl+C
                    break
                    
                if choice.startswith("🚀 Quick Start"):
                    self.quick_start()
                elif choice.startswith("📝 Create Mission"):
                    self.create_mission_and_features()
                elif choice.startswith("⚙️  Configure"):
                    self.configure_settings()
                elif choice.startswith("📊 Set Complexity"):
                    self.set_complexity_thresholds()
                elif choice.startswith("🔧 Enable/Disable"):
                    self.toggle_features()
                elif choice.startswith("📋 View Current"):
                    self.view_status()
                elif choice.startswith("❌ Exit"):
                    break
                    
                # Pause before showing menu again
                if not choice.startswith("🚀 Quick Start"):
                    questionary.press_any_key_to_continue().ask()
                    
            except KeyboardInterrupt:
                break
        
        self.console.print("\n[bold cyan]Thank you for using WarpCode! 🚀[/bold cyan]")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="WarpCode - Warp through development cycles with automated BDD and Claude Coder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive menu
  %(prog)s --quick-start      # Run full automation immediately
  %(prog)s --version          # Show version info
        """
    )
    
    parser.add_argument(
        "--quick-start",
        action="store_true",
        help="Skip menu and run full automation immediately"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)"
    )
    
    return parser


def main():
    """Main entry point for the CLI application"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        orchestrator = WarpCode()
        orchestrator.project_dir = args.project_dir
        orchestrator.run(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()