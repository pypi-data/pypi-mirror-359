"""
Scoreboard Manager

Manages real-time JSON status files that track BDD progress, Claude activity,
complexity metrics, and overall orchestration status.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import fcntl


@dataclass
class BDDStatus:
    """BDD test execution status"""
    timestamp: str
    iteration: int
    total_scenarios: int
    passed: int
    failed: int
    undefined: int
    skipped: int
    failed_scenarios: List[str]
    undefined_steps: List[str]
    current_feature: str
    completion_percentage: float


@dataclass
class ComplexityStatus:
    """Code complexity analysis status"""
    timestamp: str
    iteration: int
    total_functions: int
    complexity_grades: Dict[str, int]
    worst_offenders: List[Dict[str, Any]]
    average_complexity: float
    needs_refactoring: bool


@dataclass
class ClaudeStatus:
    """Claude activity and progress status"""
    timestamp: str
    iteration: int
    status: str  # working, idle, error, complete
    current_feature: str
    current_file: str
    current_action: str
    progress_log: List[str]
    estimated_completion: Optional[str]


@dataclass
class MasterStatus:
    """Aggregated overall status"""
    timestamp: str
    iteration: int
    overall_status: str  # initializing, in_progress, complete, error
    bdd: Dict[str, Any]
    complexity: Dict[str, Any]
    claude: Dict[str, Any]
    next_actions: List[str]


class ScoreboardManager:
    """Manages real-time scoreboard files for all orchestration metrics"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.scoreboards_dir = project_dir / "scoreboards"
        self.screenshots_dir = self.scoreboards_dir / "screenshots"
        
        # File locks for atomic writes
        self._file_locks = {}
        self._lock = threading.Lock()
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create scoreboard directories if they don't exist"""
        self.scoreboards_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    def _atomic_write_json(self, file_path: Path, data: Dict[str, Any]):
        """Atomically write JSON data to file with file locking"""
        file_str = str(file_path)
        
        with self._lock:
            if file_str not in self._file_locks:
                self._file_locks[file_str] = threading.Lock()
        
        with self._file_locks[file_str]:
            # Write to temporary file first
            temp_path = file_path.with_suffix('.tmp')
            
            try:
                with open(temp_path, 'w') as f:
                    # Use file locking for extra safety
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    json.dump(data, f, indent=2, default=str)
                    f.flush()
                
                # Atomic rename
                temp_path.rename(file_path)
                
            except Exception as e:
                # Clean up temp file on error
                if temp_path.exists():
                    temp_path.unlink()
                raise e
    
    def update_bdd_status(self, status: BDDStatus):
        """Update BDD status scoreboard"""
        file_path = self.scoreboards_dir / "bdd_status.json"
        self._atomic_write_json(file_path, asdict(status))
    
    def update_complexity_status(self, status: ComplexityStatus):
        """Update complexity status scoreboard"""
        file_path = self.scoreboards_dir / "complexity_status.json"
        self._atomic_write_json(file_path, asdict(status))
    
    def update_claude_status(self, status: ClaudeStatus):
        """Update Claude status scoreboard"""
        file_path = self.scoreboards_dir / "claude_status.json"
        self._atomic_write_json(file_path, asdict(status))
    
    def update_master_status(self, status: MasterStatus):
        """Update master aggregated status scoreboard"""
        file_path = self.scoreboards_dir / "master_status.json"
        self._atomic_write_json(file_path, asdict(status))
    
    def get_bdd_status(self) -> Optional[BDDStatus]:
        """Get current BDD status"""
        file_path = self.scoreboards_dir / "bdd_status.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path) as f:
                data = json.load(f)
                return BDDStatus(**data)
        except Exception:
            return None
    
    def get_complexity_status(self) -> Optional[ComplexityStatus]:
        """Get current complexity status"""
        file_path = self.scoreboards_dir / "complexity_status.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path) as f:
                data = json.load(f)
                return ComplexityStatus(**data)
        except Exception:
            return None
    
    def get_claude_status(self) -> Optional[ClaudeStatus]:
        """Get current Claude status"""
        file_path = self.scoreboards_dir / "claude_status.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path) as f:
                data = json.load(f)
                return ClaudeStatus(**data)
        except Exception:
            return None
    
    def get_master_status(self) -> Optional[MasterStatus]:
        """Get current master status"""
        file_path = self.scoreboards_dir / "master_status.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path) as f:
                data = json.load(f)
                return MasterStatus(**data)
        except Exception:
            return None
    
    def create_iteration_screenshot_dir(self, iteration: int) -> Path:
        """Create screenshot directory for specific iteration"""
        iteration_dir = self.screenshots_dir / f"iteration_{iteration}"
        iteration_dir.mkdir(exist_ok=True)
        return iteration_dir
    
    def update_dependencies(self, dependency_map: Dict[str, List[str]], 
                          execution_order: List[str], 
                          current_focus: str,
                          blocked_features: List[str] = None):
        """Update feature dependency information"""
        if blocked_features is None:
            blocked_features = []
        
        data = {
            "timestamp": self._get_timestamp(),
            "dependency_map": dependency_map,
            "execution_order": execution_order,
            "current_focus": current_focus,
            "blocked_features": blocked_features
        }
        
        file_path = self.scoreboards_dir / "dependencies.json"
        self._atomic_write_json(file_path, data)
    
    def aggregate_master_status(self, iteration: int, overall_status: str = "in_progress") -> MasterStatus:
        """Aggregate all status information into master status"""
        bdd_status = self.get_bdd_status()
        complexity_status = self.get_complexity_status()
        claude_status = self.get_claude_status()
        
        # Create simplified summaries
        bdd_summary = {}
        if bdd_status:
            bdd_summary = {
                "completion_percentage": bdd_status.completion_percentage,
                "tests_passing": bdd_status.failed == 0 and bdd_status.undefined == 0,
                "critical_failures": bdd_status.failed
            }
        
        complexity_summary = {}
        if complexity_status:
            complexity_summary = {
                "acceptable": not complexity_status.needs_refactoring,
                "average_grade": self._calculate_average_grade(complexity_status.complexity_grades),
                "refactoring_needed": complexity_status.needs_refactoring
            }
        
        claude_summary = {}
        if claude_status:
            claude_summary = {
                "status": claude_status.status,
                "current_feature": claude_status.current_feature,
                "eta_completion": claude_status.estimated_completion
            }
        
        # Determine next actions
        next_actions = []
        if bdd_status and bdd_status.failed_scenarios:
            next_actions.extend([f"Fix {scenario}" for scenario in bdd_status.failed_scenarios[:3]])
        if complexity_status and complexity_status.needs_refactoring:
            next_actions.append("Refactor high complexity functions")
        
        master_status = MasterStatus(
            timestamp=self._get_timestamp(),
            iteration=iteration,
            overall_status=overall_status,
            bdd=bdd_summary,
            complexity=complexity_summary,
            claude=claude_summary,
            next_actions=next_actions
        )
        
        self.update_master_status(master_status)
        return master_status
    
    def _calculate_average_grade(self, grades: Dict[str, int]) -> str:
        """Calculate average complexity grade from grade distribution"""
        grade_values = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}
        value_grades = {v: k for k, v in grade_values.items()}
        
        total_weight = 0
        total_functions = 0
        
        for grade, count in grades.items():
            if grade in grade_values and count > 0:
                total_weight += grade_values[grade] * count
                total_functions += count
        
        if total_functions == 0:
            return "A"
        
        avg_value = total_weight / total_functions
        # Round to nearest grade
        nearest_value = round(avg_value)
        return value_grades.get(nearest_value, "C")
    
    def create_initial_scoreboards(self, iteration: int = 1):
        """Create initial scoreboard files with default values"""
        timestamp = self._get_timestamp()
        
        # Initial BDD status
        initial_bdd = BDDStatus(
            timestamp=timestamp,
            iteration=iteration,
            total_scenarios=0,
            passed=0,
            failed=0,
            undefined=0,
            skipped=0,
            failed_scenarios=[],
            undefined_steps=[],
            current_feature="",
            completion_percentage=0.0
        )
        self.update_bdd_status(initial_bdd)
        
        # Initial complexity status
        initial_complexity = ComplexityStatus(
            timestamp=timestamp,
            iteration=iteration,
            total_functions=0,
            complexity_grades={"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0},
            worst_offenders=[],
            average_complexity=0.0,
            needs_refactoring=False
        )
        self.update_complexity_status(initial_complexity)
        
        # Initial Claude status
        initial_claude = ClaudeStatus(
            timestamp=timestamp,
            iteration=iteration,
            status="initializing",
            current_feature="",
            current_file="",
            current_action="Setting up environment",
            progress_log=[f"{datetime.now().strftime('%H:%M:%S')} - Orchestrator started"],
            estimated_completion=None
        )
        self.update_claude_status(initial_claude)
        
        # Create master status
        self.aggregate_master_status(iteration, "initializing")
    
    def list_scoreboard_files(self) -> List[Path]:
        """List all existing scoreboard files"""
        if not self.scoreboards_dir.exists():
            return []
        
        return list(self.scoreboards_dir.glob("*.json"))
    
    def cleanup_old_iterations(self, keep_iterations: int = 5):
        """Clean up old iteration screenshot directories"""
        if not self.screenshots_dir.exists():
            return
        
        iteration_dirs = [d for d in self.screenshots_dir.iterdir() 
                         if d.is_dir() and d.name.startswith("iteration_")]
        
        # Sort by iteration number and keep only the most recent
        iteration_dirs.sort(key=lambda d: int(d.name.split("_")[1]) if d.name.split("_")[1].isdigit() else 0)
        
        for old_dir in iteration_dirs[:-keep_iterations]:
            try:
                import shutil
                shutil.rmtree(old_dir)
            except Exception:
                pass  # Ignore cleanup errors