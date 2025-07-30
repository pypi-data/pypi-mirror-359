"""
BDD Runner

Executes behave tests and parses results for the orchestration loop.
Provides simple pass/fail/undefined/skipped counts for Claude feedback.
"""

import re
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from rich.console import Console

from .environment_manager import EnvironmentManager
from .scoreboard_manager import ScoreboardManager, BDDStatus


@dataclass
class BDDResults:
    """BDD test execution results"""
    total_scenarios: int
    passed: int
    failed: int
    undefined: int
    skipped: int
    failed_scenarios: List[str]
    undefined_steps: List[str]
    current_feature: str
    completion_percentage: float
    raw_output: str
    success: bool


class BDDRunner:
    """Executes BDD tests and parses results"""
    
    def __init__(self, project_dir: Path, environment_manager: EnvironmentManager, 
                 scoreboard_manager: ScoreboardManager, console: Optional[Console] = None):
        self.project_dir = project_dir
        self.environment_manager = environment_manager
        self.scoreboard_manager = scoreboard_manager
        self.console = console or Console()
        self.features_dir = project_dir / "features"
    
    def run_behave_tests(self, use_progress_format: bool = False, specific_feature: str = None) -> BDDResults:
        """Run behave tests and return parsed results"""
        
        # Determine command format
        cmd = ["behave"]
        if use_progress_format:
            cmd.extend(["--format", "progress3"])
        
        # Add specific feature if provided
        if specific_feature:
            feature_path = self.features_dir / specific_feature
            if feature_path.exists():
                cmd.append(str(feature_path))
            else:
                cmd.append(str(self.features_dir))
        else:
            cmd.append(str(self.features_dir))
        
        try:
            # Run behave in virtual environment
            result = self.environment_manager.run_in_venv(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            parsed_results = self._parse_behave_output(result.stdout + result.stderr, result.returncode == 0)
            
            return parsed_results
            
        except subprocess.TimeoutExpired:
            self.console.print("[red]⚠ Behave execution timed out[/red]")
            return self._create_error_results("Behave execution timed out")
        except Exception as e:
            self.console.print(f"[red]⚠ Error running behave: {e}[/red]")
            return self._create_error_results(f"Error running behave: {e}")
    
    def _parse_behave_output(self, output: str, success: bool) -> BDDResults:
        """Parse behave output to extract test results"""
        
        # Initialize counters
        total_scenarios = 0
        passed = 0
        failed = 0
        undefined = 0
        skipped = 0
        failed_scenarios = []
        undefined_steps = []
        current_feature = ""
        
        # Parse summary line patterns
        # Examples:
        # "1 feature passed, 0 failed, 0 skipped"
        # "2 scenarios passed, 1 failed, 0 skipped"
        # "15 steps passed, 3 failed, 2 skipped, 1 undefined"
        
        lines = output.split('\n')
        
        # Extract current feature being processed
        for line in lines:
            feature_match = re.search(r'Feature:\s+(.+)', line)
            if feature_match:
                current_feature = feature_match.group(1).strip()
        
        # Find scenario summary line
        scenario_pattern = r'(\d+)\s+scenarios?\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?(?:,\s+(\d+)\s+undefined)?'
        for line in lines:
            match = re.search(scenario_pattern, line)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2) or 0)
                skipped = int(match.group(3) or 0)
                undefined = int(match.group(4) or 0)
                total_scenarios = passed + failed + skipped + undefined
                break
        
        # Alternative parsing for different output formats
        if total_scenarios == 0:
            # Try parsing individual result lines
            for line in lines:
                if 'scenarios passed' in line.lower():
                    numbers = re.findall(r'(\d+)', line)
                    if numbers:
                        passed = int(numbers[0])
                elif 'scenarios failed' in line.lower():
                    numbers = re.findall(r'(\d+)', line)
                    if numbers:
                        failed = int(numbers[0])
                elif 'scenarios skipped' in line.lower():
                    numbers = re.findall(r'(\d+)', line)
                    if numbers:
                        skipped = int(numbers[0])
                elif 'scenarios undefined' in line.lower():
                    numbers = re.findall(r'(\d+)', line)
                    if numbers:
                        undefined = int(numbers[0])
            
            total_scenarios = passed + failed + skipped + undefined
        
        # Cross-validation with actual behave JSON output
        json_validation_result = self._validate_with_behave_json()
        if json_validation_result:
            self.console.print(f"[dim]Cross-validation: WarpCode parsed {passed} passed, JSON shows {json_validation_result['passed']} passed[/dim]")
            
            # If there's a significant discrepancy, trust the JSON output
            if abs(passed - json_validation_result['passed']) > 1:
                self.console.print("[yellow]⚠️ Parsing discrepancy detected - using JSON validation results[/yellow]")
                passed = json_validation_result['passed']
                failed = json_validation_result['failed']
                total_scenarios = json_validation_result['total']
        
        # Extract failed scenario names
        failed_scenarios = self._extract_failed_scenarios(output)
        
        # Extract undefined step descriptions
        undefined_steps = self._extract_undefined_steps(output)
        
        # Calculate completion percentage
        if total_scenarios > 0:
            completion_percentage = (passed / total_scenarios) * 100
        else:
            completion_percentage = 0.0
        
        # If no scenarios found, try to count feature files as a fallback
        if total_scenarios == 0:
            feature_files = list(self.features_dir.glob("*.feature"))
            if feature_files:
                total_scenarios = len(feature_files)
                # Assume all failed if behave didn't run successfully
                if not success:
                    failed = total_scenarios
                else:
                    passed = total_scenarios
                completion_percentage = (passed / total_scenarios) * 100 if total_scenarios > 0 else 0
        
        return BDDResults(
            total_scenarios=total_scenarios,
            passed=passed,
            failed=failed,
            undefined=undefined,
            skipped=skipped,
            failed_scenarios=failed_scenarios,
            undefined_steps=undefined_steps,
            current_feature=current_feature,
            completion_percentage=completion_percentage,
            raw_output=output,
            success=success
        )
    
    def _extract_failed_scenarios(self, output: str) -> List[str]:
        """Extract failed scenario names from behave output"""
        failed_scenarios = []
        lines = output.split('\n')
        
        # Look for "FAIL" or "FAILED" lines with scenario names
        for line in lines:
            # Pattern: "Scenario: Scenario Name ... FAILED"
            if 'FAILED' in line and 'Scenario:' in line:
                scenario_match = re.search(r'Scenario:\s+(.+?)\s+\.\.\.\s+FAILED', line)
                if scenario_match:
                    failed_scenarios.append(scenario_match.group(1).strip())
            
            # Alternative pattern: "FAIL: Scenario Name"
            elif line.strip().startswith('FAIL:'):
                scenario_name = line.replace('FAIL:', '').strip()
                if scenario_name:
                    failed_scenarios.append(scenario_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_failed = []
        for scenario in failed_scenarios:
            if scenario not in seen:
                seen.add(scenario)
                unique_failed.append(scenario)
        
        return unique_failed[:10]  # Limit to first 10 failures
    
    def _extract_undefined_steps(self, output: str) -> List[str]:
        """Extract undefined step descriptions from behave output"""
        undefined_steps = []
        lines = output.split('\n')
        
        in_undefined_section = False
        for line in lines:
            # Look for undefined steps section
            if 'You can implement step definitions for undefined steps with these snippets:' in line:
                in_undefined_section = True
                continue
            
            if in_undefined_section:
                # Extract step definitions
                step_match = re.search(r'@(given|when|then)\([\'"](.+?)[\'"]\)', line)
                if step_match:
                    step_text = step_match.group(2)
                    undefined_steps.append(step_text)
                
                # Stop at empty line or start of next section
                if line.strip() == '' or line.startswith('==='):
                    break
        
        return undefined_steps[:10]  # Limit to first 10 undefined steps
    
    def _validate_with_behave_json(self) -> Optional[Dict]:
        """Cross-validate results by running behave with JSON output"""
        try:
            # Run behave with JSON formatter to get reliable results
            result = subprocess.run(
                ['behave', '--format=json', '--outfile=/dev/stdout'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                # Try to parse JSON output
                try:
                    import json
                    json_data = json.loads(result.stdout)
                    
                    # Count scenarios by status
                    passed = 0
                    failed = 0
                    skipped = 0
                    undefined = 0
                    
                    for feature in json_data:
                        if 'elements' in feature:
                            for element in feature['elements']:
                                if element.get('type') == 'scenario':
                                    status = element.get('status', 'unknown')
                                    if status == 'passed':
                                        passed += 1
                                    elif status == 'failed':
                                        failed += 1
                                    elif status == 'skipped':
                                        skipped += 1
                                    elif status == 'undefined':
                                        undefined += 1
                    
                    total = passed + failed + skipped + undefined
                    
                    return {
                        'passed': passed,
                        'failed': failed,
                        'skipped': skipped,
                        'undefined': undefined,
                        'total': total
                    }
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract from stderr
                    stderr_output = result.stderr
                    if stderr_output:
                        passed_match = re.search(r'(\d+)\s+scenarios?\s+passed', stderr_output)
                        failed_match = re.search(r'(\d+)\s+scenarios?\s+failed', stderr_output)
                        
                        if passed_match or failed_match:
                            passed = int(passed_match.group(1)) if passed_match else 0
                            failed = int(failed_match.group(1)) if failed_match else 0
                            return {
                                'passed': passed,
                                'failed': failed,
                                'skipped': 0,
                                'undefined': 0,
                                'total': passed + failed
                            }
                    
        except subprocess.TimeoutExpired:
            self.console.print("[dim]JSON validation timed out[/dim]")
        except Exception as e:
            self.console.print(f"[dim]JSON validation error: {e}[/dim]")
        
        return None
    
    def _create_error_results(self, error_message: str) -> BDDResults:
        """Create error results when behave execution fails"""
        return BDDResults(
            total_scenarios=0,
            passed=0,
            failed=1,  # Mark as failed
            undefined=0,
            skipped=0,
            failed_scenarios=[f"Execution Error: {error_message}"],
            undefined_steps=[],
            current_feature="",
            completion_percentage=0.0,
            raw_output=error_message,
            success=False
        )
    
    def update_scoreboard(self, results: BDDResults, iteration: int):
        """Update BDD scoreboard with latest results"""
        status = BDDStatus(
            timestamp=self.scoreboard_manager._get_timestamp(),
            iteration=iteration,
            total_scenarios=results.total_scenarios,
            passed=results.passed,
            failed=results.failed,
            undefined=results.undefined,
            skipped=results.skipped,
            failed_scenarios=results.failed_scenarios,
            undefined_steps=results.undefined_steps,
            current_feature=results.current_feature,
            completion_percentage=results.completion_percentage
        )
        
        self.scoreboard_manager.update_bdd_status(status)
    
    def get_behave_summary_for_claude(self, results: BDDResults) -> str:
        """Generate concise summary for Claude feedback"""
        if results.total_scenarios == 0:
            return "No BDD scenarios found. Please create feature files with scenarios."
        
        summary_parts = []
        
        # Basic counts
        summary_parts.append(f"BDD Status: {results.passed} passed, {results.failed} failed, {results.undefined} undefined, {results.skipped} skipped")
        
        # Failed scenarios (if any)
        if results.failed_scenarios:
            summary_parts.append(f"Failed scenarios: {', '.join(results.failed_scenarios)}")
        
        # Undefined steps (if any)
        if results.undefined_steps:
            summary_parts.append(f"Undefined steps: {', '.join(results.undefined_steps)}")
        
        # Current feature
        if results.current_feature:
            summary_parts.append(f"Current feature: {results.current_feature}")
        
        # Completion percentage
        summary_parts.append(f"Completion: {results.completion_percentage:.1f}%")
        
        return "\n".join(summary_parts)
    
    def check_if_all_tests_pass(self, results: BDDResults) -> bool:
        """Check if all BDD tests are passing"""
        return (
            results.success and 
            results.failed == 0 and 
            results.undefined == 0 and 
            results.total_scenarios > 0 and
            results.passed > 0
        )
    
    def run_quick_check(self) -> bool:
        """Run a quick check to see if tests are passing"""
        results = self.run_behave_tests(use_progress_format=False)
        return self.check_if_all_tests_pass(results)
    
    def run_detailed_analysis(self) -> BDDResults:
        """Run detailed test analysis with error reporting"""
        return self.run_behave_tests(use_progress_format=True)
    
    def get_feature_files(self) -> List[Path]:
        """Get list of all feature files"""
        if not self.features_dir.exists():
            return []
        
        return list(self.features_dir.glob("*.feature"))
    
    def validate_bdd_setup(self) -> Tuple[bool, List[str]]:
        """Validate BDD setup and return issues if any"""
        issues = []
        
        # Check if features directory exists
        if not self.features_dir.exists():
            issues.append("Features directory does not exist")
            return False, issues
        
        # Check for feature files
        feature_files = self.get_feature_files()
        if not feature_files:
            issues.append("No .feature files found in features directory")
        
        # Check for steps directory
        steps_dir = self.features_dir / "steps"
        if not steps_dir.exists():
            issues.append("Steps directory does not exist")
        else:
            # Check for step definition files
            step_files = list(steps_dir.glob("*.py"))
            if not step_files:
                issues.append("No step definition files found in steps directory")
        
        # Check for environment.py
        env_file = self.features_dir / "environment.py"
        if not env_file.exists():
            issues.append("environment.py file is missing")
        
        # Check for behave.ini
        behave_ini = self.project_dir / "behave.ini"
        if not behave_ini.exists():
            issues.append("behave.ini configuration file is missing")
        
        return len(issues) == 0, issues
    
    def _run_behave_with_monitoring(self, cmd: List[str]) -> Dict:
        """Run behave with real-time output monitoring and status updates"""
        
        # Start the process using the existing run_in_venv method but capture output
        try:
            result = self.environment_manager.run_in_venv(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse output for real-time updates
            output_lines = (result.stdout + result.stderr).split('\n')
            current_feature = ""
            current_scenario = ""
            
            for i, line in enumerate(output_lines):
                # Extract current feature/scenario for status updates
                if 'Feature:' in line:
                    current_feature = line.split('Feature:')[-1].strip()
                    self._update_bdd_status("running", f"Processing feature: {current_feature}")
                    
                elif 'Scenario:' in line:
                    current_scenario = line.split('Scenario:')[-1].strip()
                    self._update_bdd_status("running", f"Running scenario: {current_scenario}")
                    
                elif any(keyword in line for keyword in ['PASSED', 'FAILED', 'UNDEFINED']):
                    # Update status when scenario completes
                    if 'PASSED' in line:
                        self._update_bdd_status("running", f"✅ Passed: {current_scenario}")
                    elif 'FAILED' in line:
                        self._update_bdd_status("running", f"❌ Failed: {current_scenario}")
                    elif 'UNDEFINED' in line:
                        self._update_bdd_status("running", f"❓ Undefined: {current_scenario}")
                
                # Update status every 10 lines to show progress
                if i % 10 == 0 and i > 0:
                    self._update_bdd_status("running", f"Processing... ({i}/{len(output_lines)} lines)")
            
            return {
                'output': result.stdout + result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {
                'output': f'Error running behave: {e}',
                'success': False
            }
    
    def _update_bdd_status(self, status: str, activity: str):
        """Update BDD status in scoreboard during execution"""
        from .scoreboard_manager import BDDStatus
        
        # Create a status update
        status_update = BDDStatus(
            timestamp=datetime.now().isoformat(),
            iteration=1,  # Will be updated by orchestrator
            total_scenarios=0,  # Will be updated when complete
            passed=0,
            failed=0,
            undefined=0,
            skipped=0,
            failed_scenarios=[],
            undefined_steps=[],
            current_feature=activity,  # Use activity as current feature for now
            completion_percentage=0.0
        )
        
        # Update scoreboard
        self.scoreboard_manager.update_bdd_status(status_update)
        
        # Also log to console
        self.console.print(f"[blue]BDD: {activity}[/blue]")