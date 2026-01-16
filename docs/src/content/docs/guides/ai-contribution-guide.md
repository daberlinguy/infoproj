---
title: AI Documentation & Code Standards Guide
description: Guidelines for AI assistants to maintain documentation and code quality
---

# AI Documentation & Code Standards Guide

This document provides guidelines for AI assistants (like GitHub Copilot or other AI coding tools) on how to maintain and improve the Parkour Game documentation and codebase.

## Documentation Standards

### When to Update Docs

Update documentation whenever you:
- Add a new feature or class
- Modify existing functionality
- Add new utility functions or modules
- Create new API endpoints or methods
- Fix bugs that affect user-facing behavior

### Documentation Location

- **API Documentation**: `docs/src/content/docs/api/`
- **Guides**: `docs/src/content/docs/guides/`
- **Getting Started**: `docs/src/content/docs/getting-started/`
- **Reference**: `docs/src/content/docs/reference/`

### Documentation Format

All documentation uses Markdown with Astro/Starlight frontmatter:

```markdown
---
title: Feature Name
description: Brief description of what this covers
---

# Feature Name

Your content here...
```

### Doc Content Requirements

For each new feature or class, document:

1. **Overview** - What is it and why would someone use it?
2. **Usage Examples** - Show concrete code examples
3. **Parameters/Properties** - List and explain all parameters
4. **Return Values** - What does it return?
5. **Related Links** - Links to related documentation

## Code Standards

### Block Comments for Classes

**Every new class MUST have a block comment** explaining its purpose, key methods, and usage. Use this format:

```python
"""
ClassName
===========
Brief description of the class purpose.

This class handles/manages/implements [specific functionality].

Key Methods:
    - method_one(): Description
    - method_two(): Description

Attributes:
    attribute_name (type): Description
    
Example:
    >>> obj = ClassName()
    >>> obj.method_one()
    
See Also:
    Related classes or functions
"""
class ClassName:
    pass
```

### Block Comments for Functions

```python
"""
function_name(param1, param2) -> return_type
==============================================
Brief one-liner description.

Longer description explaining what the function does, 
why you'd use it, and any important details.

Args:
    param1 (type): Description
    param2 (type): Description
    
Returns:
    return_type: Description of return value
    
Raises:
    ExceptionType: When this exception is raised
    
Example:
    >>> result = function_name(arg1, arg2)
    >>> print(result)
    
Note:
    Any important notes or warnings
"""
def function_name(param1, param2):
    pass
```

### Inline Comments

Use inline comments to explain **why**, not what:

```python
# ✅ Good - explains the reasoning
# We multiply by 1.5 to account for the acceleration boost
velocity = velocity * 1.5

# ❌ Bad - just restates the code
# Multiply velocity by 1.5
velocity = velocity * 1.5
```

### Type Hints

Always use type hints for better code clarity:

```python
def move_player(player: Player, direction: str, speed: float) -> bool:
    """Move the player in a direction at given speed."""
    pass
```

## File Organization

### Python Module Structure

```
module_name/
    __init__.py          # Package initializer
    core.py              # Main classes/functions
    utils.py             # Utility functions
    constants.py         # Constants and enums
    __pycache__/         # (Auto-generated, ignore)
```

### Adding New Python Modules

When adding a new module:

1. Create the folder and `__init__.py`
2. Add block comments to all classes and functions
3. Create corresponding documentation in `docs/src/content/docs/api/`
4. Update the sidebar config in `docs/astro.config.mjs` if needed

## Workflow for AI Assistants

### When Adding a New Feature

1. **Write the code** with proper block comments and type hints
2. **Create/update the doc** in the appropriate docs folder
3. **Update the sidebar** in `docs/astro.config.mjs` if adding a new page
4. **Commit with clear message**: `"Add [feature]: [description]"`
5. **Push to master** (workflow will auto-deploy)

### When Modifying Existing Code

1. **Update block comments** if behavior changed
2. **Update corresponding docs** if API changed
3. **Maintain backwards compatibility** or document breaking changes
4. **Commit with message**: `"Update [module]: [description]"`

### Commit Message Format

```
[Type] [Module]: Brief description

- Additional detail if needed
- Another point if relevant
```

Types: `Add`, `Update`, `Fix`, `Refactor`, `Document`

Example:
```
Add Player: New dash ability with cooldown system

- Implements horizontal dash with 0.5s cooldown
- Adds dash velocity multiplier configuration
- Updates PlayerScreen to handle dash input
```

## Documentation Checklist

Before committing code changes, verify:

- [ ] All new classes have block comments
- [ ] All new functions have docstrings
- [ ] Type hints are included
- [ ] Inline comments explain the "why"
- [ ] Corresponding documentation exists
- [ ] Examples are provided where helpful
- [ ] Links in docs use correct paths
- [ ] Sidebar config updated if needed
- [ ] No broken internal links

## Common Documentation Mistakes to Avoid

❌ **Wrong:**
```python
# Get the player
player = get_player()
```

✅ **Right:**
```python
# Retrieve the active player from the current scene
player = get_player()
```

---

❌ **Wrong:**
- No documentation for new features
- Code comments that just repeat the code
- Incomplete API documentation

✅ **Right:**
- Document all public APIs
- Comments explain decisions and edge cases
- Examples show common usage patterns

## GitHub Pages Deployment

The documentation automatically deploys when you:
1. Push changes to `master` branch
2. Changes are in `docs/` folder or workflow files
3. Workflow completes successfully

Visit: https://daberlinguy.github.io/infoproj/

## Questions?

If you're unsure about:
- **Documentation structure**: Check existing docs in `docs/src/content/docs/`
- **Code style**: Review existing code in `src/code/`
- **API standards**: Look at `src/code/skeletons/` for class examples

---

**Remember:** Good documentation helps future developers (human and AI) understand and maintain the codebase! 📚
