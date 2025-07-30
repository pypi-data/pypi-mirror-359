# BDD Claude Orchestrator

🤖 **Automated BDD development with Claude Coder orchestration** 🤖

A Python CLI tool that continuously runs Claude Coder until all BDD tests pass, with real-time monitoring, dependency management, and zero human intervention required.

## ✨ Features

- **🔄 Fully Automated BDD Development** - Zero human intervention once started
- **📊 Real-time Scoreboards** - JSON files with live progress tracking  
- **🤖 Claude Integration** - Automated Claude Coder execution with activity monitoring
- **🧪 BDD Test Management** - Behave integration with pass/fail parsing
- **📈 Complexity Monitoring** - Radon integration for code quality assurance
- **🎯 Reality Enforcement** - Screenshot capture and mock detection
- **🔗 Dependency Management** - Smart feature ordering and dependency tracking
- **🎨 Beautiful CLI** - Rich console output with ASCII art and progress indicators

## 🚀 Quick Start

1. **Run the orchestrator:**
   ```bash
   python3 run_orchestrator.py
   ```

2. **Choose "Quick Start" from the menu** - The tool will:
   - Create a Python 3.10 virtual environment
   - Set up BDD project structure (`/features`, `/features/steps`)
   - Install all dependencies automatically
   - Run Claude Coder in a loop until all tests pass

3. **Monitor progress** via:
   - Beautiful CLI dashboard with live updates
   - Real-time scoreboard files in `./scoreboards/`
   - Screenshots of UI tests in `./scoreboards/screenshots/`

## 📁 Project Structure

After initialization, your project will have:

```
your-project/
├── features/                    # BDD feature files
│   ├── environment.py          # Behave configuration
│   ├── steps/                  # Step definitions
│   └── *.feature              # Gherkin feature files
├── scoreboards/                # Real-time status files
│   ├── master_status.json     # Overall progress
│   ├── bdd_status.json        # Test results
│   ├── claude_status.json     # Claude activity
│   ├── complexity_status.json # Code quality metrics
│   └── screenshots/           # UI test verification
├── venv/                      # Virtual environment
├── behave.ini                 # Behave configuration
└── dependency.md              # Feature dependencies
```

## 📊 Scoreboards

The orchestrator maintains real-time JSON files that you can tail or consume:

```bash
# Monitor overall progress
tail -f scoreboards/master_status.json

# Watch BDD test results
tail -f scoreboards/bdd_status.json

# Track Claude activity
tail -f scoreboards/claude_status.json

# Monitor code complexity
tail -f scoreboards/complexity_status.json
```

## 🎛️ CLI Options

```bash
# Interactive menu (default)
python3 run_orchestrator.py

# Skip menu and run immediately  
python3 run_orchestrator.py --quick-start

# Show version
python3 run_orchestrator.py --version

# Help
python3 run_orchestrator.py --help
```

## ⚙️ Configuration

The orchestrator can be configured through:

1. **Interactive Menu** - Configure settings through the CLI
2. **Command Line Arguments** - Pass options directly
3. **Environment Variables** - Set `ANTHROPIC_API_KEY` for Claude
4. **Configuration Files** - `behave.ini` for BDD settings

## 🔄 How It Works

1. **Environment Setup** - Creates venv, installs dependencies, sets up BDD structure
2. **Initial Validation** - Checks Python version, Claude availability, BDD setup
3. **Orchestration Loop**:
   - Run BDD tests with behave
   - Parse results (pass/fail/undefined/skipped counts)
   - If not all passing → send results to Claude
   - Monitor Claude execution in real-time
   - Update scoreboards continuously
   - Repeat until success or max iterations

## 📋 Requirements

- **Python 3.10+** (automatically checked)
- **Claude Code CLI** (must be installed and authenticated)
- **Git** (for project management)

## 🛠️ Development

Install in development mode:

```bash
pip install -e .
```

Run with development dependencies:

```bash
pip install -r requirements.txt
python3 run_orchestrator.py
```

## 📝 Example Output

```bash
🚀 BDD Claude Orchestrator v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Iter 1] 🔄 Setup complete → Starting authentication.feature
[Iter 1] 📊 BDD: 0/12 tests | Complexity: - | Claude: Analyzing requirements
[Iter 2] 📊 BDD: 3/12 ✓ | Complexity: B | Claude: auth_steps.py → login logic  
[Iter 3] 📊 BDD: 8/12 ✓ | Complexity: B | Claude: models.py → user validation
[Iter 4] ❌ 2 failed: password-reset, profile-update | Claude: debugging flows
[Iter 5] 📊 BDD: 12/12 ✓ | Complexity: A | Claude: Final verification ✨

🎉 ALL TESTS PASSING! Total time: 23m 45s
```

## 🎯 Reality Enforcement

The orchestrator ensures authentic implementations:

- **No Mocks Allowed** - Detects and prevents placeholder implementations
- **UI Screenshot Verification** - Captures real browser interactions
- **Database Connections** - Requires real data persistence
- **API Integration** - Tests against actual endpoints
- **Fast-Fail Design** - Stops execution if tests are unrealistic

## 🔗 Dependency Management

Features can specify dependencies in `dependency.md`:

```markdown
# Feature Dependencies

user_registration.feature -> (no dependencies)
user_authentication.feature -> user_registration.feature  
user_profile.feature -> user_authentication.feature
```

Claude automatically maintains this file and executes features in dependency order.

## 🚧 Future Features

- **Web UI Dashboard** consuming scoreboard files
- **Multi-project Support** with workspace management  
- **CI/CD Integration** for automated PR validation
- **Advanced Analytics** and performance tracking
- **Plugin System** for custom analyzers

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Documentation**: See `prodspec.md` for detailed technical specifications
- **Scoreboards**: Monitor `./scoreboards/` directory for real-time status

---

**Built with ❤️ by Claude Code**

*Zero human intervention. Maximum test coverage. Real implementations only.*