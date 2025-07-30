"""
Environment Manager

Handles Python virtual environment creation, BDD project structure setup,
and template file deployment for automated BDD development.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import tempfile

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


class EnvironmentManager:
    """Manages Python virtual environments and BDD project setup"""
    
    def __init__(self, project_dir: Path, console: Optional[Console] = None):
        self.project_dir = project_dir
        self.console = console or Console()
        self.venv_dir = self._detect_or_set_venv_dir()
        self.features_dir = project_dir / "features"
        self.steps_dir = self.features_dir / "steps"
    
    def _detect_or_set_venv_dir(self) -> Path:
        """Detect existing virtual environment or set default location"""
        # Common virtual environment directory names to check
        venv_candidates = [
            self.project_dir / "venv",
            self.project_dir / ".venv", 
            self.project_dir / "virtualenv",
            self.project_dir / ".virtualenv",
            self.project_dir / "env",
            self.project_dir / ".env"
        ]
        
        for venv_path in venv_candidates:
            if self._is_valid_venv(venv_path):
                self.console.print(f"[green]✓ Found existing virtual environment: {venv_path.name}[/green]")
                return venv_path
        
        # No existing venv found, default to 'venv'
        return self.project_dir / "venv"
    
    def _is_valid_venv(self, venv_path: Path) -> bool:
        """Check if a directory is a valid Python virtual environment"""
        if not venv_path.exists() or not venv_path.is_dir():
            return False
        
        # Check for virtual environment indicators
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        if pyvenv_cfg.exists():
            return True
        
        # Check for Python executable in expected locations
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_path / "bin" / "python"
        
        return python_exe.exists()
    
    def get_venv_python_version(self) -> Optional[str]:
        """Get the Python version of the detected virtual environment"""
        if not self._is_valid_venv(self.venv_dir):
            return None
        
        try:
            python_exe = self.get_python_executable()
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
        
    def check_python_version(self) -> bool:
        """Check if Python 3.10+ is available"""
        try:
            # Try python3.10 first
            result = subprocess.run(
                ["python3.10", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_str = result.stdout.strip()
            self.console.print(f"[green]✓ Found {version_str}[/green]")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # Fall back to python3
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_str = result.stdout.strip()
            # Check if it's 3.10+
            version_parts = version_str.split()
            if len(version_parts) >= 2:
                version_num = version_parts[1]
                major, minor = map(int, version_num.split('.')[:2])
                if major == 3 and minor >= 10:
                    self.console.print(f"[green]✓ Found {version_str}[/green]")
                    return True
                else:
                    self.console.print(f"[yellow]⚠ Found {version_str} but need Python 3.10+[/yellow]")
                    return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        self.console.print("[red]✗ Python 3.10+ not found[/red]")
        return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment or use existing one"""
        if self._is_valid_venv(self.venv_dir):
            venv_version = self.get_venv_python_version()
            if venv_version:
                self.console.print(f"[green]✓ Using existing virtual environment: {self.venv_dir.name} ({venv_version})[/green]")
            else:
                self.console.print(f"[green]✓ Using existing virtual environment: {self.venv_dir.name}[/green]")
            return True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Creating virtual environment...", total=None)
            
            try:
                # Try python3.10 first, fall back to python3
                python_cmd = "python3.10"
                try:
                    subprocess.run([python_cmd, "--version"], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    python_cmd = "python3"
                
                # Create venv
                subprocess.run(
                    [python_cmd, "-m", "venv", str(self.venv_dir)],
                    check=True,
                    capture_output=True
                )
                
                progress.update(task, description="Virtual environment created successfully")
                self.console.print(f"[green]✓ Virtual environment created at {self.venv_dir}[/green]")
                return True
                
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]✗ Failed to create virtual environment: {e}[/red]")
                return False
    
    def get_python_executable(self) -> Path:
        """Get the Python executable path for the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            return self.venv_dir / "bin" / "python"
    
    def get_pip_executable(self) -> Path:
        """Get the pip executable path for the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            return self.venv_dir / "bin" / "pip"
    
    def activate_environment_commands(self) -> List[str]:
        """Get commands to activate the virtual environment"""
        if os.name == 'nt':  # Windows
            return [str(self.venv_dir / "Scripts" / "activate.bat")]
        else:  # Unix/Linux/macOS
            return ["source", str(self.venv_dir / "bin" / "activate")]
    
    def install_dependencies(self) -> bool:
        """Install required dependencies in virtual environment"""
        requirements = [
            "behave>=1.2.6",
            "questionary>=1.10.0",
            "radon>=4.1.0",
            "anthropic>=0.25.0",
            "rich>=13.0",
            "click>=8.0",
            "PyYAML>=6.0",
            "pexpect>=4.8.0",
            "pillow>=9.0.0",
            "selenium>=4.0.0",  # For web UI testing
            "webdriver-manager>=3.8.0"  # For automatic webdriver management
        ]
        
        pip_cmd = self.get_pip_executable()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            total_deps = len(requirements)
            task = progress.add_task("Installing dependencies...", total=total_deps)
            
            for i, requirement in enumerate(requirements):
                progress.update(task, description=f"Installing {requirement.split('>=')[0]}...")
                
                try:
                    subprocess.run(
                        [str(pip_cmd), "install", requirement],
                        check=True,
                        capture_output=True
                    )
                    progress.advance(task)
                except subprocess.CalledProcessError as e:
                    self.console.print(f"[red]✗ Failed to install {requirement}: {e}[/red]")
                    return False
        
        self.console.print("[green]✓ All dependencies installed successfully[/green]")
        return True
    
    def create_bdd_structure(self) -> bool:
        """Create BDD project directory structure"""
        try:
            # Create main directories
            self.features_dir.mkdir(exist_ok=True)
            self.steps_dir.mkdir(exist_ok=True)
            
            self.console.print(f"[green]✓ Created {self.features_dir}[/green]")
            self.console.print(f"[green]✓ Created {self.steps_dir}[/green]")
            
            return True
        except Exception as e:
            self.console.print(f"[red]✗ Failed to create BDD structure: {e}[/red]")
            return False
    
    def deploy_template_files(self) -> bool:
        """Deploy template files for BDD setup"""
        try:
            # Create environment.py
            environment_py_content = '''"""
Behave environment configuration for BDD Claude Orchestrator
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from behave import fixture, use_fixture
import os


@fixture
def browser_chrome(context):
    """Setup Chrome browser for UI testing"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    context.browser = webdriver.Chrome(service=service, options=chrome_options)
    context.browser.implicitly_wait(10)
    
    yield context.browser
    
    # Cleanup
    context.browser.quit()


def before_all(context):
    """Setup before all tests"""
    context.config.setup_logging()


def before_feature(context, feature):
    """Setup before each feature"""
    # Setup browser if feature has @browser tag
    if "browser" in feature.tags:
        use_fixture(browser_chrome, context)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Take screenshot directory setup
    if hasattr(context, 'browser'):
        screenshots_dir = os.path.join("scoreboards", "screenshots", f"iteration_{getattr(context, 'iteration', 1)}")
        os.makedirs(screenshots_dir, exist_ok=True)
        context.screenshots_dir = screenshots_dir


def after_step(context, step):
    """Cleanup after each step"""
    # Take screenshot on failure for UI tests
    if step.status == "failed" and hasattr(context, 'browser'):
        screenshot_path = os.path.join(
            context.screenshots_dir, 
            f"{step.name.replace(' ', '_')}_failed.png"
        )
        try:
            context.browser.save_screenshot(screenshot_path)
        except Exception:
            pass  # Ignore screenshot errors


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Take success screenshot for UI tests  
    if scenario.status == "passed" and hasattr(context, 'browser'):
        screenshot_path = os.path.join(
            context.screenshots_dir,
            f"{scenario.name.replace(' ', '_')}_success.png"
        )
        try:
            context.browser.save_screenshot(screenshot_path)
        except Exception:
            pass  # Ignore screenshot errors
'''
            
            environment_file = self.features_dir / "environment.py"
            environment_file.write_text(environment_py_content)
            self.console.print(f"[green]✓ Created {environment_file}[/green]")
            
            # Create behave.ini
            behave_ini_content = '''[behave]
format = progress
show_skipped = true
show_timings = true
logging_level = INFO
logging_format = %(levelname)s:%(name)s:%(message)s
logging_clear_handlers = yes

[behave.userdata]
runner.continue_after_failed_step = false
'''
            
            behave_ini_file = self.project_dir / "behave.ini"
            behave_ini_file.write_text(behave_ini_content)
            self.console.print(f"[green]✓ Created {behave_ini_file}[/green]")
            
            # Create example feature file
            example_feature_content = '''Feature: Example BDD Feature
  As a user of the BDD Claude Orchestrator
  I want to see an example feature file
  So that I understand the expected structure

  Scenario: Basic example scenario
    Given I have a working BDD setup
    When I run the example scenario
    Then I should see it pass

  @browser
  Scenario: Example UI scenario
    Given I open a web browser
    When I navigate to a test page
    Then I should see the page content
'''
            
            example_feature_file = self.features_dir / "example.feature"
            example_feature_file.write_text(example_feature_content)
            self.console.print(f"[green]✓ Created {example_feature_file}[/green]")
            
            # Create example step definitions
            example_steps_content = '''"""
Example step definitions for BDD Claude Orchestrator
"""

from behave import given, when, then
import time


@given('I have a working BDD setup')
def step_working_bdd_setup(context):
    """Verify BDD setup is working"""
    assert True, "BDD setup is working"


@when('I run the example scenario')
def step_run_example_scenario(context):
    """Run example scenario"""
    context.scenario_ran = True


@then('I should see it pass')
def step_see_it_pass(context):
    """Verify scenario passes"""
    assert context.scenario_ran, "Scenario should have run"


@given('I open a web browser')
def step_open_browser(context):
    """Open web browser (browser fixture handles this)"""
    assert hasattr(context, 'browser'), "Browser should be available"


@when('I navigate to a test page')
def step_navigate_to_page(context):
    """Navigate to a test page"""
    # Navigate to a simple test page
    context.browser.get("data:text/html,<html><body><h1>Test Page</h1><p>Hello World!</p></body></html>")
    time.sleep(1)  # Wait for page load


@then('I should see the page content')
def step_see_page_content(context):
    """Verify page content is visible"""
    page_title = context.browser.find_element("tag name", "h1").text
    assert page_title == "Test Page", f"Expected 'Test Page', got '{page_title}'"
'''
            
            example_steps_file = self.steps_dir / "example_steps.py"
            example_steps_file.write_text(example_steps_content)
            self.console.print(f"[green]✓ Created {example_steps_file}[/green]")
            
            # Create dependency.md template
            dependency_md_content = '''# Feature Dependencies

This file tracks dependencies between BDD features to ensure proper execution order.

## Dependency Format

```
Feature A -> Feature B (A must be completed before B)
```

## Current Dependencies

```
example.feature -> (no dependencies)
```

## Execution Order

1. example.feature

## Notes

- Features without dependencies can run first
- Features with dependencies should wait for their prerequisites
- Claude will automatically update this file as new features are added
'''
            
            dependency_file = self.project_dir / "dependency.md"
            dependency_file.write_text(dependency_md_content)
            self.console.print(f"[green]✓ Created {dependency_file}[/green]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]✗ Failed to deploy template files: {e}[/red]")
            return False
    
    def setup_complete_environment(self) -> bool:
        """Complete environment setup process"""
        self.console.print("\n[bold blue]🔧 Setting up BDD development environment...[/bold blue]\n")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create BDD structure
        if not self.create_bdd_structure():
            return False
        
        # Deploy template files
        if not self.deploy_template_files():
            return False
        
        self.console.print("\n[bold green]🎉 Environment setup complete![/bold green]")
        self.console.print(f"[green]✓ Virtual environment: {self.venv_dir}[/green]")
        self.console.print(f"[green]✓ Features directory: {self.features_dir}[/green]")
        self.console.print(f"[green]✓ Steps directory: {self.steps_dir}[/green]")
        
        return True
    
    def is_environment_ready(self) -> bool:
        """Check if environment is already set up and ready"""
        return (
            self._is_valid_venv(self.venv_dir) and
            self.features_dir.exists() and
            self.steps_dir.exists() and
            (self.features_dir / "environment.py").exists() and
            (self.project_dir / "behave.ini").exists()
        )
    
    def get_environment_status(self) -> Dict[str, bool]:
        """Get detailed status of environment components"""
        return {
            "venv_exists": self._is_valid_venv(self.venv_dir),
            "venv_path": str(self.venv_dir),
            "venv_python_version": self.get_venv_python_version(),
            "features_dir_exists": self.features_dir.exists(),
            "steps_dir_exists": self.steps_dir.exists(),
            "environment_py_exists": (self.features_dir / "environment.py").exists(),
            "behave_ini_exists": (self.project_dir / "behave.ini").exists(),
            "python_executable_exists": self.get_python_executable().exists(),
            "pip_executable_exists": self.get_pip_executable().exists(),
        }
    
    def run_in_venv(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command in the virtual environment"""
        python_exe = self.get_python_executable()
        
        if command[0] == "python":
            command[0] = str(python_exe)
        elif command[0] == "pip":
            command[0] = str(self.get_pip_executable())
        elif command[0] == "behave":
            # Run behave through python -m behave to ensure correct environment
            command = [str(python_exe), "-m", "behave"] + command[1:]
        
        return subprocess.run(command, **kwargs)