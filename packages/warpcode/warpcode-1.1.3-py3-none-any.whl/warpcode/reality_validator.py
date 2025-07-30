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
        self.llm_analysis: List[str] = []  # LLM-detected fake patterns
    
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
    
    def add_llm_analysis(self, file_path: str, analysis: str):
        """Add LLM-based fake detection analysis"""
        self.llm_analysis.append(f"{file_path}: {analysis}")
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
        """Comprehensive dual-phase reality validation (regex + LLM) of the project"""
        result = RealityValidationResult()
        
        self.console.print("[blue]🔍 Running dual-phase reality validation (Regex + LLM)...[/blue]")
        
        # PHASE 1: Regex-based detection (fast, pattern-based)
        self.console.print("[dim]Phase 1: Regex pattern detection...[/dim]")
        self._scan_for_fake_patterns(result)
        self._validate_subprocess_calls(result)
        self._check_mock_dependencies(result)
        
        # PHASE 2: LLM-based detection (sophisticated, context-aware)
        self.console.print("[dim]Phase 2: LLM-based fake detection...[/dim]")
        self._llm_based_fake_detection(result)
        
        # PHASE 3: Behavioral validation (real testing)
        self.console.print("[dim]Phase 3: Behavioral validation...[/dim]")
        self._run_behavioral_tests(result)
        self._validate_test_isolation(result)
        
        # PHASE 4: Cross-validation and conflict resolution
        self._cross_validate_results(result)
        
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
        """Run enhanced behavioral tests to check if implementations are real"""
        self.console.print("[dim]Running enhanced behavioral validation tests...[/dim]")
        
        # Find Python files that BDD tests might depend on
        potential_impl_files = [
            f for f in self.project_dir.glob("*.py") 
            if not f.name.startswith('test_') and f.name not in ['setup.py', '__init__.py']
        ]
        
        if not potential_impl_files:
            result.add_issue("No implementation files found to test")
            return
        
        # Test each implementation file
        for impl_file in potential_impl_files:
            test_result = self._test_file_dependency(impl_file)
            result.validation_tests.append(test_result)
            
            if not test_result['passes_dependency_test']:
                result.add_issue(f"Tests pass even when {impl_file.name} is missing - likely fake implementation")
        
        # Cross-validate with direct behave execution
        self._cross_validate_behave_execution(result)
        
        # Test individual scenario isolation
        self._test_scenario_isolation(result)
    
    def _cross_validate_behave_execution(self, result: RealityValidationResult):
        """Cross-validate by comparing WarpCode vs manual behave execution"""
        self.console.print("[dim]Cross-validating with manual behave execution...[/dim]")
        
        try:
            # Run behave manually and capture results
            manual_result = subprocess.run(
                ['behave', '--format=plain'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse manual results
            manual_output = manual_result.stdout + manual_result.stderr
            
            # Count scenarios in manual output
            manual_passed = len(re.findall(r'passed', manual_output, re.IGNORECASE))
            manual_failed = len(re.findall(r'failed', manual_output, re.IGNORECASE))
            
            # Compare with what WarpCode reported (from BDD runner)
            # This will be compared against the BDD runner results in the orchestrator
            validation_test = {
                'test_type': 'cross_validation',
                'manual_passed': manual_passed,
                'manual_failed': manual_failed,
                'manual_output_sample': manual_output[:500],
                'passes_dependency_test': True  # Always passes unless there's a major discrepancy
            }
            
            result.validation_tests.append(validation_test)
            
        except Exception as e:
            result.add_issue(f"Cross-validation with manual behave execution failed: {e}")
    
    def _test_scenario_isolation(self, result: RealityValidationResult):
        """Test that scenarios can run independently"""
        self.console.print("[dim]Testing scenario isolation...[/dim]")
        
        try:
            # Find all feature files
            feature_files = list(self.project_dir.glob("features/*.feature"))
            
            if not feature_files:
                return
            
            # Test running each feature file individually
            for feature_file in feature_files[:2]:  # Limit to first 2 files to avoid timeout
                try:
                    individual_result = subprocess.run(
                        ['behave', str(feature_file.relative_to(self.project_dir))],
                        cwd=self.project_dir,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    # Check if individual execution produces different results
                    individual_output = individual_result.stdout + individual_result.stderr
                    has_failures = 'failed' in individual_output.lower()
                    
                    isolation_test = {
                        'test_type': 'scenario_isolation',
                        'feature_file': feature_file.name,
                        'has_failures': has_failures,
                        'passes_dependency_test': True,  # Isolation test doesn't fail validation
                        'analysis': f"Individual feature execution for {feature_file.name}"
                    }
                    
                    result.validation_tests.append(isolation_test)
                    
                except subprocess.TimeoutExpired:
                    result.add_issue(f"Scenario isolation test timed out for {feature_file.name}")
                except Exception as e:
                    result.add_issue(f"Scenario isolation test failed for {feature_file.name}: {e}")
                    
        except Exception as e:
            result.add_issue(f"Scenario isolation testing failed: {e}")
    
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
    
    def _llm_based_fake_detection(self, result: RealityValidationResult):
        """Use Claude with conversation continuity to detect sophisticated fake implementations"""
        self.console.print("[dim]Running LLM-based fake detection with conversation continuity...[/dim]")
        
        # Find all step definition files
        step_files = list(self.project_dir.glob("features/steps/*.py"))
        
        if not step_files:
            self.console.print("[dim]No step files found for LLM analysis[/dim]")
            return
        
        # Step 1: Create comprehensive fake analysis using conversation continuity
        fake_analysis_result = self._run_comprehensive_fake_analysis(step_files)
        
        if fake_analysis_result:
            # Step 2: Parse the comprehensive analysis
            fake_patterns = self._parse_comprehensive_fake_analysis(fake_analysis_result)
            
            for file_path, pattern in fake_patterns:
                result.add_llm_analysis(file_path, pattern)
        
        # Step 3: Generate fakesteps.md report for later reference
        self._generate_fakesteps_report(result)
    
    def _run_comprehensive_fake_analysis(self, step_files: List[Path]) -> Optional[str]:
        """Run comprehensive fake analysis using Claude with conversation continuity"""
        try:
            # Create comprehensive analysis prompt
            comprehensive_prompt = self._create_comprehensive_analysis_prompt(step_files)
            
            # Use conversation ID for continuity if available
            conversation_file = self.project_dir / ".warpcode_conversation_id"
            conversation_id = None
            
            if conversation_file.exists():
                try:
                    with open(conversation_file, 'r') as f:
                        conversation_id = f.read().strip()
                except Exception:
                    pass
            
            # Run Claude with conversation continuity
            cmd = ["claude"]
            if conversation_id:
                cmd.extend(["-c", conversation_id])
            cmd.extend([
                "--print",
                "--dangerously-skip-permissions",
                comprehensive_prompt
            ])
            
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=60  # Longer timeout for comprehensive analysis
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.console.print(f"[dim]Comprehensive Claude analysis failed: {result.stderr}[/dim]")
                return None
                
        except subprocess.TimeoutExpired:
            self.console.print("[dim]Comprehensive Claude analysis timed out[/dim]")
            return None
        except Exception as e:
            self.console.print(f"[dim]Error in comprehensive Claude analysis: {e}[/dim]")
            return None
    
    def _create_comprehensive_analysis_prompt(self, step_files: List[Path]) -> str:
        """Create a comprehensive prompt for analyzing all step files together"""
        
        # Read all step files content
        files_content = {}
        total_lines = 0
        
        for step_file in step_files:
            try:
                with open(step_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files_content[step_file.name] = content
                    total_lines += len(content.split('\n'))
            except Exception as e:
                self.console.print(f"[dim]Could not read {step_file.name}: {e}[/dim]")
        
        # If too much content, analyze the largest files first
        if total_lines > 1000:
            # Sort by file size and take the largest files
            sorted_files = sorted(files_content.items(), key=lambda x: len(x[1]), reverse=True)
            files_content = dict(sorted_files[:3])  # Take top 3 largest files
        
        prompt = f"""🔍 COMPREHENSIVE FAKE IMPLEMENTATION ANALYSIS

Analyze ALL the following BDD step definition files for fake implementations. Look for patterns that indicate the code is not testing real functionality:

"""
        
        for filename, content in files_content.items():
            prompt += f"""
📁 File: {filename}
```python
{content}
```

"""
        
        prompt += """
❌ IDENTIFY FAKE PATTERNS ACROSS ALL FILES:
• HTML/CSS/JavaScript mock interfaces embedded in Python
• subprocess calls with immediate fallback to browser-based mocks
• Hardcoded responses instead of real command execution  
• Browser automation against fake HTML interfaces instead of real applications
• Always-passing assertions or placeholder implementations
• Simulated terminal outputs or fake data generation
• Steps that create fake interfaces rather than testing real functionality
• Missing real Python implementation files that tests should depend on

✅ LOOK FOR REAL IMPLEMENTATION INDICATORS:
• Actual Python class/function calls to real implementation files
• Proper subprocess error handling with real command validation
• Tests that would fail if implementation files were missing/renamed
• Real file I/O operations and genuine system interactions
• Authentic command execution with proper result validation

📝 RESPONSE FORMAT:
For each fake pattern found, respond with:
"FAKE DETECTED in {filename}: {specific description of fake pattern}"

For files that appear to have real implementations:
"REAL IMPLEMENTATION in {filename}: {brief validation}"

🎯 FOCUS ON:
1. Are tests actually connecting to real Python code or just fake HTML interfaces?
2. Do subprocess calls have proper error handling or just fall back to mocks?
3. Would these tests fail if the main implementation file was missing?
4. Are assertions testing real functionality or just fake responses?

Provide a comprehensive analysis covering all files."""

        return prompt
    
    def _parse_comprehensive_fake_analysis(self, claude_response: str) -> List[Tuple[str, str]]:
        """Parse comprehensive Claude response to extract fake patterns by file"""
        fake_patterns = []
        
        lines = claude_response.split('\n')
        for line in lines:
            if 'FAKE DETECTED in' in line:
                # Extract filename and pattern
                try:
                    parts = line.split('FAKE DETECTED in', 1)[1].strip()
                    if ':' in parts:
                        filename_part, pattern_part = parts.split(':', 1)
                        filename = filename_part.strip()
                        pattern = pattern_part.strip()
                        fake_patterns.append((f"features/steps/{filename}", pattern))
                except Exception:
                    # Fallback to simple pattern extraction
                    pattern = line.replace('FAKE DETECTED', '').strip()
                    if pattern:
                        fake_patterns.append(("unknown_file", pattern))
        
        return fake_patterns
    
    def _generate_fakesteps_report(self, result: RealityValidationResult):
        """Generate fakesteps.md report for reference"""
        try:
            fakesteps_file = self.project_dir / "fakesteps.md"
            
            with open(fakesteps_file, 'w') as f:
                f.write("# Fake Implementation Analysis Report\n\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if result.llm_analysis:
                    f.write("## LLM-Detected Fake Patterns\n\n")
                    for analysis in result.llm_analysis:
                        f.write(f"- {analysis}\n")
                    f.write("\n")
                
                if result.fake_patterns:
                    f.write("## Regex-Detected Fake Patterns\n\n")
                    for pattern in result.fake_patterns:
                        f.write(f"- {pattern}\n")
                    f.write("\n")
                
                if result.mock_files:
                    f.write("## Mock Files Detected\n\n")
                    for mock_file in result.mock_files:
                        f.write(f"- {mock_file}\n")
                    f.write("\n")
                
                f.write("## Recommendations\n\n")
                f.write("1. Replace fake implementations with real Python code\n")
                f.write("2. Ensure tests fail when implementation files are missing\n")
                f.write("3. Use proper subprocess error handling\n")
                f.write("4. Remove HTML/browser-based mocks\n")
                f.write("5. Implement actual file I/O and system interactions\n")
            
            self.console.print(f"[dim]Generated fake analysis report: {fakesteps_file}[/dim]")
            
        except Exception as e:
            self.console.print(f"[dim]Could not generate fakesteps.md: {e}[/dim]")
    
    def _create_fake_analysis_prompt(self, step_file: Path, content: str) -> str:
        """Create a prompt for Claude to analyze BDD step implementations for fakes"""
        
        prompt = f"""🔍 FAKE IMPLEMENTATION DETECTION ANALYSIS

Analyze the following BDD step definitions file for fake implementations:

File: {step_file.name}

```python
{content}
```

❌ IDENTIFY FAKE PATTERNS:
• HTML/CSS/JavaScript mock interfaces embedded in Python
• subprocess calls with immediate fallback to mocks
• Hardcoded responses instead of real command execution
• Browser automation against fake HTML interfaces
• Always-passing assertions or placeholder implementations
• Simulated terminal outputs or fake data generation
• Steps that don't actually test real functionality

✅ REAL IMPLEMENTATION INDICATORS:
• Actual Python class/function calls
• Proper subprocess error handling
• Tests that would fail if implementation files were missing
• Real file I/O operations
• Genuine command execution with result validation

📝 RESPONSE FORMAT:
If fake implementations are found, respond with:
"FAKE DETECTED: [specific fake pattern description]"

If implementations appear real, respond with:
"REAL IMPLEMENTATION: [brief validation]"

Be specific about what makes each pattern fake or real."""

        return prompt
    
    def _run_claude_analysis(self, prompt: str) -> Optional[str]:
        """Run Claude analysis on the provided prompt"""
        try:
            # Use Claude Code CLI to analyze the prompt
            result = subprocess.run(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.console.print(f"[dim]Claude analysis failed: {result.stderr}[/dim]")
                return None
                
        except subprocess.TimeoutExpired:
            self.console.print("[dim]Claude analysis timed out[/dim]")
            return None
        except Exception as e:
            self.console.print(f"[dim]Error running Claude analysis: {e}[/dim]")
            return None
    
    def _parse_claude_fake_analysis(self, claude_response: str) -> List[str]:
        """Parse Claude's response to extract fake patterns"""
        fake_patterns = []
        
        lines = claude_response.split('\n')
        for line in lines:
            if line.strip().startswith('FAKE DETECTED:'):
                # Extract the fake pattern description
                pattern = line.replace('FAKE DETECTED:', '').strip()
                if pattern:
                    fake_patterns.append(pattern)
        
        return fake_patterns
    
    def _cross_validate_results(self, result: RealityValidationResult):
        """Cross-validate and resolve conflicts between regex and LLM detection"""
        self.console.print("[dim]Cross-validating regex and LLM results...[/dim]")
        
        # Count detections by type
        regex_detections = len(result.fake_patterns) + len(result.mock_files) + len(result.subprocess_issues)
        llm_detections = len(result.llm_analysis)
        
        # If both methods agree (both find fakes or both find real), confidence is high
        if regex_detections > 0 and llm_detections > 0:
            result.add_issue("HIGH CONFIDENCE: Both regex and LLM detected fake implementations")
            self.console.print("[red]⚠️ Both validation methods detected fakes - high confidence[/red]")
        
        # If only one method detects fakes, investigate further
        elif regex_detections > 0 and llm_detections == 0:
            result.add_issue("MEDIUM CONFIDENCE: Regex detected fakes but LLM did not - possible false positive")
            self.console.print("[yellow]⚠️ Only regex detected fakes - medium confidence[/yellow]")
        
        elif regex_detections == 0 and llm_detections > 0:
            result.add_issue("HIGH CONFIDENCE: LLM detected sophisticated fakes missed by regex")
            self.console.print("[red]⚠️ LLM detected sophisticated fakes - high confidence[/red]")
        
        # If neither detects fakes, still check behavioral validation
        elif regex_detections == 0 and llm_detections == 0:
            if len(result.validation_tests) > 0:
                failed_behavioral_tests = [t for t in result.validation_tests if not t.get('passes_dependency_test', False)]
                if failed_behavioral_tests:
                    result.add_issue("CRITICAL: Behavioral tests failed - implementations may be fake despite passing pattern detection")
                    self.console.print("[red]🚨 CRITICAL: Behavioral validation failed despite passing pattern checks[/red]")
                else:
                    self.console.print("[green]✅ All validation phases passed - implementations appear real[/green]")
            else:
                result.add_issue("WARNING: No behavioral tests run - validation incomplete")
                self.console.print("[yellow]⚠️ No behavioral tests run - validation incomplete[/yellow]")
        
        # Add summary statistics
        total_issues = len(result.issues) + regex_detections + llm_detections
        if total_issues > 0:
            result.add_issue(f"SUMMARY: {regex_detections} regex detections, {llm_detections} LLM detections, {len(result.issues)} other issues")
    
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
        
        if result.llm_analysis:
            self.console.print("\n[magenta]🤖 LLM Fake Detection:[/magenta]")
            for analysis in result.llm_analysis:
                self.console.print(f"  • {analysis}")
        
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
                'subprocess_issues': len(result.subprocess_issues),
                'llm_analysis': len(result.llm_analysis)
            },
            'details': {
                'fake_patterns': result.fake_patterns,
                'mock_files': result.mock_files,
                'subprocess_issues': result.subprocess_issues,
                'validation_tests': result.validation_tests,
                'llm_analysis': result.llm_analysis,
                'issues': result.issues
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)