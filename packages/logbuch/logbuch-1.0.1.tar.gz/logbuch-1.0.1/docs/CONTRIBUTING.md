# 🤝 Contributing to Logbuch

Thank you for your interest in contributing to Logbuch! This document provides guidelines and information for contributors.

## 🌟 **Ways to Contribute**

- 🐛 **Bug Reports** - Help us identify and fix issues
- 💡 **Feature Requests** - Suggest new features and improvements
- 🔧 **Code Contributions** - Submit pull requests
- 📖 **Documentation** - Improve our documentation
- 🌍 **Translations** - Help translate Logbuch
- 🎨 **Design** - Improve UI/UX and visual elements
- 🧪 **Testing** - Help test new features and releases

## 🚀 **Getting Started**

### **1. Fork and Clone**
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/logbuch.git
cd logbuch

# Add the original repository as upstream
git remote add upstream https://github.com/originalowner/logbuch.git
```

### **2. Set Up Development Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### **3. Run Tests**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=logbuch

# Run specific test file
python -m pytest tests/test_tasks.py
```

## 📝 **Development Guidelines**

### **Code Style**
- Follow **PEP 8** Python style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: **88 characters**
- Use **type hints** where possible

```bash
# Format code
black logbuch/
isort logbuch/

# Check style
flake8 logbuch/
mypy logbuch/
```

### **Commit Messages**
Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(tasks): add bulk task operations
fix(coach): resolve AI coaching memory leak
docs(readme): update installation instructions
```

### **Branch Naming**
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation
- `refactor/code-improvement` - Refactoring

## 🐛 **Bug Reports**

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the bug
3. **Expected behavior** vs actual behavior
4. **Environment information**:
   - OS and version
   - Python version
   - Logbuch version
5. **Error messages** or logs
6. **Screenshots** if applicable

**Use our bug report template:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.7]
- Logbuch: [e.g., 1.0.0]

## Additional Context
Any other relevant information
```

## 💡 **Feature Requests**

For feature requests, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with details
4. **Consider alternatives** you've thought of
5. **Provide use cases** and examples

**Use our feature request template:**
```markdown
## Problem Statement
What problem does this feature solve?

## Proposed Solution
Detailed description of the proposed feature

## Alternatives Considered
Other solutions you've considered

## Use Cases
Real-world scenarios where this would be useful

## Implementation Ideas
Technical suggestions (optional)
```

## 🔧 **Code Contributions**

### **Pull Request Process**

1. **Create a branch** from `main`
2. **Make your changes** following our guidelines
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run tests** and ensure they pass
6. **Submit pull request** with clear description

### **Pull Request Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### **Code Review Process**

1. **Automated checks** must pass
2. **At least one maintainer** review required
3. **Address feedback** promptly
4. **Squash commits** before merge (if requested)

## 🧪 **Testing Guidelines**

### **Test Structure**
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data
└── conftest.py     # Pytest configuration
```

### **Writing Tests**
```python
import pytest
from logbuch.core.tasks import TaskManager

def test_task_creation():
    """Test basic task creation functionality."""
    manager = TaskManager()
    task = manager.create_task("Test task")
    
    assert task.title == "Test task"
    assert task.status == "pending"
    assert task.id is not None

@pytest.fixture
def sample_task():
    """Fixture providing a sample task."""
    return {"title": "Sample task", "priority": "medium"}
```

### **Test Coverage**
- Aim for **90%+ coverage**
- Test **happy paths** and **edge cases**
- Include **error conditions**
- Test **user interactions**

## 📖 **Documentation**

### **Documentation Types**
- **User documentation** - How to use features
- **Developer documentation** - How code works
- **API documentation** - Function/class references
- **Tutorials** - Step-by-step guides

### **Documentation Standards**
- Use **clear, concise language**
- Include **code examples**
- Add **screenshots** where helpful
- Keep **up-to-date** with code changes

### **Docstring Format**
```python
def create_task(title: str, priority: str = "medium") -> Task:
    """Create a new task with the given title and priority.
    
    Args:
        title: The task title
        priority: Task priority (low, medium, high)
        
    Returns:
        Task: The created task object
        
    Raises:
        ValueError: If title is empty or priority is invalid
        
    Example:
        >>> task = create_task("Finish project", "high")
        >>> print(task.title)
        Finish project
    """
```

## 🌍 **Internationalization**

Help translate Logbuch to other languages:

1. **Check existing translations** in `logbuch/i18n/`
2. **Create new language file** (e.g., `de.json` for German)
3. **Translate strings** maintaining placeholders
4. **Test translations** in your language
5. **Submit pull request**

## 🏗️ **Architecture Overview**

### **Project Structure**
```
logbuch/
├── core/           # Core functionality
├── commands/       # CLI commands
├── features/       # Feature modules
├── integrations/   # External integrations
├── utils/          # Utility functions
└── cli.py          # Main CLI entry point
```

### **Key Components**
- **Storage Layer** - Data persistence
- **Command Layer** - CLI command handling
- **Feature Layer** - Business logic
- **Integration Layer** - External services

## 🎯 **Development Priorities**

### **High Priority**
- Bug fixes and stability improvements
- Performance optimizations
- User experience enhancements
- Documentation improvements

### **Medium Priority**
- New features and integrations
- Code refactoring and cleanup
- Test coverage improvements
- Accessibility features

### **Low Priority**
- Experimental features
- Nice-to-have improvements
- Code style updates
- Minor optimizations

## 🚀 **Release Process**

### **Version Numbering**
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### **Release Checklist**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] GitHub release created

## 🏆 **Recognition**

Contributors are recognized in:
- **CONTRIBUTORS.md** file
- **GitHub contributors** page
- **Release notes** mentions
- **Special thanks** in documentation

## 📞 **Getting Help**

Need help contributing? Reach out:

- **GitHub Discussions** - General questions
- **GitHub Issues** - Specific problems
- **Discord** - Real-time chat
- **Email** - Direct contact

## 📋 **Contributor Checklist**

Before submitting your contribution:

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Pull request template filled
- [ ] No merge conflicts
- [ ] Ready for review

## 🙏 **Thank You**

Every contribution, no matter how small, makes Logbuch better. Thank you for being part of our community!

---

**Happy Contributing! 🚀**
