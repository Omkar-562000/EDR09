# Contributing to Automated EDR

Thank you for your interest in contributing to the Automated EDR system! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Coding Standards](#coding-standards)
8. [Documentation](#documentation)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and professional in all interactions
- Welcome diverse perspectives and experiences
- Provide constructive feedback
- Focus on what is best for the community
- Report concerns to project maintainers

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** (for frontend development)
- **Git**
- **Docker & Docker Compose** (optional, for containerized development)

### Fork and Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/automated-edr.git
cd automated-edr

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/automated-edr.git

# Verify remotes
git remote -v
# origin    https://github.com/YOUR_USERNAME/automated-edr.git (fetch)
# origin    https://github.com/YOUR_USERNAME/automated-edr.git (push)
# upstream  https://github.com/ORIGINAL_OWNER/automated-edr.git (fetch)
# upstream  https://github.com/ORIGINAL_OWNER/automated-edr.git (push)
```

---

## Development Setup

### Backend Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black ruff

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Using Docker Compose

```bash
docker-compose up -d
docker-compose logs -f
```

---

## Making Changes

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature

# Or for bug fixes
git checkout -b fix/my-bug-fix
```

### Branch Naming Conventions

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions

### Commit Messages

Write clear, descriptive commit messages:

```
# Good
git commit -m "Add rule reloading endpoint to detection engine"
git commit -m "Fix: Prevent null pointer in event normalization"

# Bad
git commit -m "update"
git commit -m "fixed stuff"
```

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/updates
- `chore`: Maintenance

---

## Testing

### Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/test_edr_flow.py

# Run with verbose output
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend.edr --cov-report=html
```

### Writing Tests

Create test files in `backend/tests/` using pytest:

```python
import pytest
from backend.edr.models import Event, EventType
from backend.edr.detection.engine import DetectionEngine

@pytest.fixture
def detection_engine():
    return DetectionEngine()

def test_process_detection(detection_engine):
    """Test process event detection."""
    event = Event(
        source="test",
        event_type=EventType.PROCESS,
        title="process_observed",
        payload={
            "process_name": "malware.exe",
            "pid": 1234,
            "cmdline": "malware.exe -install",
            "username": "admin",
        }
    )
    
    detections = detection_engine.evaluate(event)
    
    assert isinstance(detections, list)
```

### Test Coverage Requirements

- Aim for >80% code coverage
- All new features must have tests
- All bug fixes should have regression tests
- Test edge cases and error conditions

---

## Submitting Changes

### Before Submitting

1. **Code Quality**
   ```bash
   # Format code
   black backend/
   
   # Lint code
   ruff check backend/
   
   # Run tests
   pytest backend/tests/
   ```

2. **Update Documentation**
   - Update README if behavior changed
   - Add docstrings to new functions
   - Update relevant guides in `docs/`

3. **Commit Best Practices**
   - Keep commits focused and logical
   - Use clear commit messages
   - Reference issues in commits: `Fix #123`

### Pull Request Process

1. **Push to your fork**
   ```bash
   git push origin feature/my-feature
   ```

2. **Create Pull Request**
   - Go to GitHub and create PR from your fork
   - Use clear title: "Add feature X" or "Fix issue #123"
   - Fill out PR template completely
   - Link related issues: "Fixes #123"

3. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Breaking change
   
   ## Related Issues
   Fixes #123
   
   ## Testing
   Describe testing performed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

4. **Code Review**
   - Address reviewer feedback promptly
   - Discuss concerns respectfully
   - Update code as needed

5. **Merge**
   - Maintainers will merge when approved
   - Uses squash merge for clean history

---

## Coding Standards

### Python Style

Follow PEP 8 with these tools:

```bash
# Format with black
black backend/

# Lint with ruff
ruff check backend/ --fix
```

### Code Style Guidelines

```python
# Use type hints
def process_event(event: Event) -> list[Detection]:
    """Process event and return detections."""
    pass

# Use descriptive names
detection_engine = DetectionEngine()  # Good
de = DetectionEngine()  # Avoid

# Keep functions focused
def validate_rule(rule: Rule) -> bool:
    """Validate rule structure."""
    return rule.rule_id and rule.name and rule.condition

# Use docstrings
def evaluate(self, event: Event) -> list[Detection]:
    """
    Evaluate event against all loaded rules.
    
    Args:
        event: Event to evaluate
        
    Returns:
        List of matching detections
    """
    pass

# Handle errors appropriately
try:
    result = operation()
except SpecificException as e:
    logger.error(f"Failed to process: {e}")
    raise
```

### JavaScript/React Style

```javascript
// Use camelCase for variables
const currentUser = getUser();

// Use PascalCase for components
function DashboardPage() {
  return <div>Dashboard</div>;
}

// Use descriptive names
const [detections, setDetections] = useState([]);

// Add JSDoc comments
/**
 * Fetch recent detections from API
 * @returns {Promise<Array>} List of detections
 */
async function fetchDetections() {
  // ...
}
```

---

## Documentation

### Adding Documentation

1. **Code Comments**
   - Explain *why*, not *what*
   - Comment complex logic
   - Keep comments up-to-date

2. **Docstrings**
   - All public functions/classes
   - Include parameters, returns, exceptions
   - Use Google-style docstrings

3. **Documentation Files**
   - Update relevant guides in `docs/`
   - Add examples for new features
   - Update README if needed

### Documentation Standards

```python
def create_detection(
    rule_id: str,
    event: Event,
    severity: Severity,
) -> Detection:
    """
    Create a detection from a matched rule.
    
    This function instantiates a Detection object when a rule
    matches an event, capturing the context and metadata for
    later analysis and response.
    
    Args:
        rule_id: Unique rule identifier that matched
        event: The event that triggered detection
        severity: Severity level of detection
        
    Returns:
        Detection object with full context
        
    Raises:
        ValueError: If rule_id is invalid or empty
        TypeError: If event is not an Event instance
        
    Examples:
        >>> event = Event(...)
        >>> detection = create_detection("PROC-001", event, Severity.HIGH)
        >>> print(detection.detection_id)
    """
    pass
```

---

## Common Contribution Areas

### Bug Fixes
1. Verify the bug with a test case
2. Fix the issue
3. Add regression test
4. Document the fix

### New Features
1. Discuss feature in an issue first
2. Design and document feature
3. Implement with tests
4. Update user documentation
5. Add to changelog

### Documentation
1. Fix typos and clarity issues
2. Add missing documentation
3. Improve examples
4. Translate documentation

### Testing
1. Add tests for uncovered code
2. Improve test quality
3. Add integration tests
4. Create performance benchmarks

### Rule Development
1. Create new detection rules
2. Improve existing rules
3. Reduce false positives
4. Add rule documentation

---

## Development Workflow Example

```bash
# 1. Update main branch
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/add-new-collector

# 3. Make changes
vim backend/edr/agent/collectors.py

# 4. Add tests
vim backend/tests/test_new_collector.py

# 5. Format and lint
black backend/
ruff check backend/ --fix

# 6. Run tests
pytest backend/tests/

# 7. Commit changes
git commit -m "feat: Add CustomCollector for monitoring custom data"

# 8. Push to fork
git push origin feature/add-new-collector

# 9. Create PR on GitHub
# Go to https://github.com/YOUR_USERNAME/automated-edr and click "New Pull Request"

# 10. Address feedback and update PR
git commit -m "Address review feedback: improve error handling"
git push origin feature/add-new-collector

# 11. Squash commits after approval (if needed)
git rebase -i upstream/main

# 12. PR merged by maintainer
```

---

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with reproduction steps
- **Features**: Discuss in an issue before coding
- **Slack/Discord**: Join community chat (if available)

---

## Recognition

Contributors are recognized in:
- GitHub contributor list
- `CONTRIBUTORS.md` file
- Release notes

Thank you for contributing to make EDR better! 🎉
