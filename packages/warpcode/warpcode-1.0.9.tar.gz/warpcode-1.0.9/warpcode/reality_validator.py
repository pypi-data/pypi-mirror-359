"""
Reality Validator

Validates that BDD implementations are real and not fake/mock implementations.
Prevents false confidence from tests that pass against HTML mocks or hardcoded responses.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

from rich.console import Console

from .bdd_runner import BDDRunner


class RealityValidationResult:
    """Result of reality validation check"""
    
    def __init__(self):
        self.is_real = True
        self.issues: List[str] = []
        self.fake_patterns: List[str] = []
        self.mock_files: List[str] = []
        self.subprocess_issues: List[str] = []
        self.validation_tests: List[Dict] = []
    
    def add_issue(self, issue: str):
        """Add validation issue"""
        self.issues.append(issue)
        self.is_real = False
    
    def add_fake_pattern(self, file_path: str, pattern: str, line: str):
        """Add detected fake pattern"""
        self.fake_patterns.append(f"{file_path}: {pattern} - {line.strip()}")
        self.is_real = False
    
    def add_mock_file(self, file_path: str, reason: str):
        """Add mock file detection"""
        self.mock_files.append(f"{file_path}: {reason}")
        self.is_real = False
    
    def add_subprocess_issue(self, file_path: str, issue: str):
        """Add subprocess validation issue"""
        self.subprocess_issues.append(f"{file_path}: {issue}")
        self.is_real = False


class RealityValidator:
    """Validates that BDD implementations are real, not fake"""
    
    def __init__(self, project_dir: Path, console: Optional[Console] = None):
        self.project_dir = project_dir
        self.console = console or Console()
        
        # Patterns that indicate fake implementations
        self.fake_patterns = [
            # HTML/JS mock patterns
            (r'create_test_interface', 'HTML mock interface creation'),
            (r'<html>|<div>|<script>', 'HTML content in Python files'),
            (r'document\.getElementById|innerHTML', 'JavaScript DOM manipulation'),
            (r'addTerminalOutput.*fake|hardcoded', 'Hardcoded terminal output'),
            
            # Hardcoded responses
            (r'return\s+["\'].*\s+-\s+[ABC]\s+\(', 'Hardcoded radon responses'),
            (r'complexity.*low|medium|high.*complexity', 'Fake complexity data'),
            (r'\.py\s+-\s+[ABC].*complexity', 'Hardcoded file complexity'),
            
            # Subprocess without error checking
            (r'subprocess\.Popen.*\n.*time\.sleep.*\n.*create_test', 'Subprocess with fallback mock'),
            (r'subprocess\.Popen.*(?!.*returncode|poll|wait)', 'Subprocess without error checking'),
            
            # Always-pass patterns
            (r'context\..*=.*True.*always', 'Always-true context variables'),
            (r'assert.*True.*#.*always', 'Always-passing assertions'),
            (r'pass.*#.*mock|fake|placeholder', 'Placeholder implementations'),
            
            # Simulation patterns  
            (r'simulate|simulated|simulation', 'Simulation instead of real implementation'),
            (r'fake_|mock_|dummy_', 'Fake/mock/dummy functions'),
        ]
    
    def validate_project(self) -> RealityValidationResult:
        """Comprehensive reality validation of the project"""
        result = RealityValidationResult()
        
        self.console.print("[blue]🔍 Running comprehensive reality validation...[/blue]")
        
        # 1. Scan for fake patterns in code
        self._scan_for_fake_patterns(result)
        
        # 2. Validate subprocess calls
        self._validate_subprocess_calls(result)
        
        # 3. Run behavioral validation tests
        self._run_behavioral_tests(result)
        
        # 4. Check for mock file dependencies
        self._check_mock_dependencies(result)
        
        # 5. Validate test isolation
        self._validate_test_isolation(result)
        
        return result
    
    def _scan_for_fake_patterns(self, result: RealityValidationResult):
        """Scan all Python files for fake implementation patterns"""
        self.console.print("[dim]Scanning for fake patterns...[/dim]")
        
        for py_file in self.project_dir.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'venv', '.venv']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern, description in self.fake_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            result.add_fake_pattern(
                                str(py_file.relative_to(self.project_dir)),
                                description,
                                f"Line {i}: {line}"
                            )
                            
            except Exception as e:
                result.add_issue(f"Could not scan {py_file}: {e}")
    
    def _validate_subprocess_calls(self, result: RealityValidationResult):
        """Validate that subprocess calls are properly handled"""
        self.console.print("[dim]Validating subprocess implementations...[/dim]")
        
        step_files = list(self.project_dir.glob("features/steps/*.py"))
        
        for step_file in step_files:
            try:
                with open(step_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find subprocess.Popen calls
                popen_matches = re.finditer(r'subprocess\.Popen\([^)]+\)', content, re.MULTILINE | re.DOTALL)
                
                for match in popen_matches:
                    popen_call = match.group(0)
                    
                    # Check if there's error handling nearby
                    start_pos = max(0, match.start() - 500)
                    end_pos = min(len(content), match.end() + 500)
                    surrounding_code = content[start_pos:end_pos]
                    
                    has_error_check = any(pattern in surrounding_code for pattern in [
                        'returncode', 'poll()', 'wait()', 'try:', 'except:', 'if.*process'
                    ])
                    
                    # Check for fallback mocks
                    has_fallback_mock = any(pattern in surrounding_code for pattern in [
                        'create_test_interface', 'create_mock', 'fallback', '<html>'
                    ])
                    
                    if not has_error_check:
                        result.add_subprocess_issue(
                            str(step_file.relative_to(self.project_dir)),
                            "subprocess.Popen call without error checking"
                        )
                    
                    if has_fallback_mock:
                        result.add_subprocess_issue(
                            str(step_file.relative_to(self.project_dir)), 
                            "subprocess.Popen with fallback mock interface"
                        )
                        
            except Exception as e:
                result.add_issue(f"Could not validate {step_file}: {e}")
    
    def _run_behavioral_tests(self, result: RealityValidationResult):
        """Run behavioral tests to check if implementations are real"""
        self.console.print("[dim]Running behavioral validation tests...[/dim]")
        
        # Find Python files that BDD tests might depend on
        potential_impl_files = [
            f for f in self.project_dir.glob("*.py") 
            if not f.name.startswith('test_') and f.name not in ['setup.py', '__init__.py']
        ]
        
        if not potential_impl_files:
            result.add_issue("No implementation files found to test")
            return
        
        for impl_file in potential_impl_files:
            test_result = self._test_file_dependency(impl_file)
            result.validation_tests.append(test_result)
            
            if not test_result['passes_dependency_test']:
                result.add_issue(f"Tests pass even when {impl_file.name} is missing - likely fake implementation")
    
    def _test_file_dependency(self, impl_file: Path) -> Dict:
        """Test if BDD tests actually depend on an implementation file"""
        backup_file = impl_file.with_suffix('.validation_backup')
        
        try:
            # Run tests normally first
            initial_result = self._run_bdd_tests_quietly()
            
            # Move implementation file away
            shutil.move(str(impl_file), str(backup_file))
            
            # Run tests again - they should fail now
            without_file_result = self._run_bdd_tests_quietly()
            
            # Restore file
            shutil.move(str(backup_file), str(impl_file))
            
            # Run tests again - they should pass now
            restored_result = self._run_bdd_tests_quietly()
            
            # Analyze results
            passes_dependency_test = (
                initial_result['passed'] > 0 and
                without_file_result['passed'] < initial_result['passed'] and
                restored_result['passed'] >= initial_result['passed']
            )
            
            return {
                'file': impl_file.name,
                'passes_dependency_test': passes_dependency_test,
                'initial_passed': initial_result['passed'],
                'without_file_passed': without_file_result['passed'],
                'restored_passed': restored_result['passed'],
                'analysis': f"Tests {'depend on' if passes_dependency_test else 'do not depend on'} {impl_file.name}"
            }
            
        except Exception as e:
            # Ensure file is restored even on error
            if backup_file.exists():
                shutil.move(str(backup_file), str(impl_file))
            
            return {
                'file': impl_file.name,
                'passes_dependency_test': False,
                'error': str(e),
                'analysis': f"Error testing dependency on {impl_file.name}"
            }
    
    def _run_bdd_tests_quietly(self) -> Dict:
        """Run BDD tests quietly and return basic results"""
        try:
            result = subprocess.run(
                ['behave', '--no-color', '--format=plain'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse basic results from output
            output = result.stdout + result.stderr
            
            passed = len(re.findall(r'passed', output, re.IGNORECASE))
            failed = len(re.findall(r'failed', output, re.IGNORECASE))
            
            return {
                'passed': passed,
                'failed': failed,
                'output': output[:500]  # First 500 chars for debugging
            }
            
        except subprocess.TimeoutExpired:
            return {'passed': 0, 'failed': 0, 'error': 'timeout'}
        except Exception as e:
            return {'passed': 0, 'failed': 0, 'error': str(e)}
    
    def _check_mock_dependencies(self, result: RealityValidationResult):
        """Check for files that look like they contain mock implementations"""
        self.console.print("[dim]Checking for mock dependencies...[/dim]")
        
        for py_file in self.project_dir.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'venv']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check file size vs. HTML content ratio
                html_content = len(re.findall(r'<[^>]+>', content))
                total_lines = len(content.split('\n'))
                
                if html_content > 10 and total_lines > 50:
                    result.add_mock_file(
                        str(py_file.relative_to(self.project_dir)),
                        f"Contains {html_content} HTML tags in {total_lines} lines - likely mock interface"
                    )
                
                # Check for large amounts of hardcoded strings
                string_matches = re.findall(r'["\'][^"\']{20,}["\']', content)
                if len(string_matches) > 20:
                    result.add_mock_file(
                        str(py_file.relative_to(self.project_dir)),
                        f"Contains {len(string_matches)} long hardcoded strings - likely fake data"
                    )
                    
            except Exception:
                pass  # Skip files that can't be read
    
    def _validate_test_isolation(self, result: RealityValidationResult):
        """Validate that tests are properly isolated and not interdependent"""
        self.console.print("[dim]Validating test isolation...[/dim]")
        
        # This is a placeholder for more sophisticated isolation testing
        # Could include running scenarios individually vs. together
        pass
    
    def print_validation_report(self, result: RealityValidationResult):
        """Print a comprehensive validation report"""
        if result.is_real:
            self.console.print("[green]✅ VALIDATION PASSED: Implementations appear to be real[/green]")
        else:
            self.console.print("[red]❌ VALIDATION FAILED: Fake implementations detected[/red]")
        
        if result.fake_patterns:
            self.console.print("\n[red]🚨 Fake Patterns Detected:[/red]")
            for pattern in result.fake_patterns:
                self.console.print(f"  • {pattern}")
        
        if result.mock_files:
            self.console.print("\n[yellow]📄 Mock Files Detected:[/yellow]")
            for mock_file in result.mock_files:
                self.console.print(f"  • {mock_file}")
        
        if result.subprocess_issues:
            self.console.print("\n[orange]⚠️ Subprocess Issues:[/orange]")
            for issue in result.subprocess_issues:
                self.console.print(f"  • {issue}")
        
        if result.validation_tests:
            self.console.print("\n[blue]🧪 Behavioral Test Results:[/blue]")
            for test in result.validation_tests:
                status = "✅" if test['passes_dependency_test'] else "❌"
                self.console.print(f"  {status} {test['analysis']}")
        
        if result.issues:
            self.console.print("\n[red]❗ Other Issues:[/red]")
            for issue in result.issues:
                self.console.print(f"  • {issue}")
    
    def save_validation_report(self, result: RealityValidationResult, output_file: Path):
        """Save validation report to JSON file"""
        report_data = {
            'timestamp': time.time(),
            'is_real': result.is_real,
            'summary': {
                'total_issues': len(result.issues),
                'fake_patterns': len(result.fake_patterns),
                'mock_files': len(result.mock_files),
                'subprocess_issues': len(result.subprocess_issues)
            },
            'details': {
                'fake_patterns': result.fake_patterns,
                'mock_files': result.mock_files,
                'subprocess_issues': result.subprocess_issues,
                'validation_tests': result.validation_tests,
                'issues': result.issues
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)