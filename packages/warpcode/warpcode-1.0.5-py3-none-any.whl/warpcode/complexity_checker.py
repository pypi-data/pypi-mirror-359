"""
Complexity Checker

Integrates Radon for code complexity analysis and provides feedback
for automated refactoring through Claude.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from rich.console import Console

from .environment_manager import EnvironmentManager
from .scoreboard_manager import ScoreboardManager, ComplexityStatus


@dataclass
class ComplexityResult:
    """Single function complexity result"""
    function_name: str
    file_path: str
    complexity: int
    grade: str
    line_number: int


class ComplexityChecker:
    """Analyzes code complexity using Radon"""
    
    def __init__(self, project_dir: Path, environment_manager: EnvironmentManager,
                 scoreboard_manager: ScoreboardManager, console: Optional[Console] = None):
        self.project_dir = project_dir
        self.environment_manager = environment_manager
        self.scoreboard_manager = scoreboard_manager
        self.console = console or Console()
        
        # Complexity thresholds
        self.warning_grade = "C"  # Warn at C-level complexity
        self.fail_grade = "F"     # Fail at F-level complexity
        self.max_complexity = 10  # Maximum acceptable complexity score
    
    def check_complexity(self) -> ComplexityStatus:
        """Run complexity analysis and return results"""
        try:
            # Run radon cc (cyclomatic complexity) analysis
            results = self._run_radon_analysis()
            
            # Process results
            complexity_status = self._process_results(results)
            
            return complexity_status
            
        except Exception as e:
            self.console.print(f"[red]Error running complexity analysis: {e}[/red]")
            return self._create_error_status()
    
    def _run_radon_analysis(self) -> Dict:
        """Run radon complexity analysis"""
        # Focus on Python files in project
        python_files = []
        for pattern in ["**/*.py", "features/**/*.py"]:
            python_files.extend(self.project_dir.glob(pattern))
        
        if not python_files:
            return {}
        
        # Run radon with JSON output
        cmd = ["radon", "cc", "--json", "--show-complexity", str(self.project_dir)]
        
        try:
            result = self.environment_manager.run_in_venv(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            else:
                self.console.print(f"[yellow]Radon analysis returned no results[/yellow]")
                return {}
                
        except subprocess.TimeoutExpired:
            self.console.print("[red]Radon analysis timed out[/red]")
            return {}
        except json.JSONDecodeError:
            self.console.print("[red]Failed to parse radon output[/red]")
            return {}
        except Exception as e:
            self.console.print(f"[red]Error running radon: {e}[/red]")
            return {}
    
    def _process_results(self, radon_results: Dict) -> ComplexityStatus:
        """Process radon results into complexity status"""
        all_functions = []
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
        total_complexity = 0
        worst_offenders = []
        
        # Process each file's results
        for file_path, functions in radon_results.items():
            if not functions:
                continue
                
            for func_data in functions:
                complexity_result = ComplexityResult(
                    function_name=func_data.get("name", "unknown"),
                    file_path=file_path,
                    complexity=func_data.get("complexity", 0),
                    grade=func_data.get("rank", "A"),
                    line_number=func_data.get("lineno", 0)
                )
                
                all_functions.append(complexity_result)
                
                # Count grades
                grade = complexity_result.grade
                if grade in grade_counts:
                    grade_counts[grade] += 1
                
                total_complexity += complexity_result.complexity
                
                # Track worst offenders (C grade or worse)
                if grade in ["C", "D", "E", "F"]:
                    worst_offenders.append({
                        "function": complexity_result.function_name,
                        "file": complexity_result.file_path,
                        "complexity": complexity_result.complexity,
                        "grade": grade
                    })
        
        # Sort worst offenders by complexity
        worst_offenders.sort(key=lambda x: x["complexity"], reverse=True)
        worst_offenders = worst_offenders[:10]  # Keep top 10
        
        # Calculate average complexity
        avg_complexity = total_complexity / len(all_functions) if all_functions else 0.0
        
        # Determine if refactoring is needed
        needs_refactoring = (
            grade_counts.get("F", 0) > 0 or  # Any F-grade functions
            grade_counts.get("E", 0) > 2 or  # More than 2 E-grade functions
            grade_counts.get("D", 0) > 5     # More than 5 D-grade functions
        )
        
        return ComplexityStatus(
            timestamp=self.scoreboard_manager._get_timestamp(),
            iteration=1,  # Will be updated by caller
            total_functions=len(all_functions),
            complexity_grades=grade_counts,
            worst_offenders=worst_offenders,
            average_complexity=avg_complexity,
            needs_refactoring=needs_refactoring
        )
    
    def _create_error_status(self) -> ComplexityStatus:
        """Create error status when analysis fails"""
        return ComplexityStatus(
            timestamp=self.scoreboard_manager._get_timestamp(),
            iteration=1,
            total_functions=0,
            complexity_grades={"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0},
            worst_offenders=[],
            average_complexity=0.0,
            needs_refactoring=False
        )
    
    def update_scoreboard(self, status: ComplexityStatus, iteration: int):
        """Update complexity scoreboard"""
        status.iteration = iteration
        self.scoreboard_manager.update_complexity_status(status)
    
    def get_complexity_issues_for_claude(self, status: ComplexityStatus) -> List[str]:
        """Generate complexity issues list for Claude feedback"""
        issues = []
        
        if not status.worst_offenders:
            return issues
        
        # Add worst offenders
        for offender in status.worst_offenders[:5]:  # Top 5 worst
            issues.append(
                f"Function '{offender['function']}' in {offender['file']} "
                f"has complexity {offender['complexity']} (grade {offender['grade']})"
            )
        
        # Add summary if many issues
        if status.needs_refactoring:
            f_count = status.complexity_grades.get("F", 0)
            e_count = status.complexity_grades.get("E", 0)
            d_count = status.complexity_grades.get("D", 0)
            
            if f_count > 0:
                issues.append(f"{f_count} functions have F-grade complexity (very high)")
            if e_count > 0:
                issues.append(f"{e_count} functions have E-grade complexity (high)")
            if d_count > 5:
                issues.append(f"{d_count} functions have D-grade complexity (moderate)")
        
        return issues
    
    def is_complexity_acceptable(self, status: ComplexityStatus) -> bool:
        """Check if complexity is at acceptable levels"""
        return not status.needs_refactoring
    
    def get_complexity_summary(self, status: ComplexityStatus) -> str:
        """Get human-readable complexity summary"""
        if status.total_functions == 0:
            return "No functions analyzed"
        
        avg_grade = self.scoreboard_manager._calculate_average_grade(status.complexity_grades)
        
        summary_parts = [
            f"Complexity: {status.total_functions} functions analyzed",
            f"Average grade: {avg_grade}",
            f"Average complexity: {status.average_complexity:.1f}"
        ]
        
        if status.needs_refactoring:
            summary_parts.append("⚠ Refactoring needed")
        else:
            summary_parts.append("✓ Acceptable")
        
        return " | ".join(summary_parts)