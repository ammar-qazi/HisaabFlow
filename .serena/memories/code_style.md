# HisaabFlow - Code Style & Conventions

## Python Conventions

### File Structure
- **File naming**: snake_case.py
- **Class naming**: PascalCase
- **Function naming**: snake_case
- **Constants**: UPPER_SNAKE_CASE

### Import Order
1. Standard library imports
2. Third-party packages (pandas, fastapi, etc.)
3. Local modules (relative imports)

### Code Style
- **Type hints**: Use pydantic models for API validation
- **Docstrings**: Minimal documentation, focus on inline comments
- **Error handling**: Use FastAPI exception handling patterns
- **Configuration**: External .conf files, not hardcoded values

## Frontend Conventions

### File Structure
- **Components**: PascalCase.js (e.g., ModernFileUploadStep.js)
- **Utilities**: camelCase.js
- **Constants**: UPPER_SNAKE_CASE

### Component Structure
1. Imports
2. Component function
3. Default export

### Code Style
- **Modern React**: Function components with hooks
- **State management**: useState for local state
- **API calls**: axios with proper error handling
- **Styling**: Inline styles and CSS classes

## General Conventions
- **Modular design**: Single responsibility principle
- **Configuration-driven**: External config files for bank rules
- **Error handling**: Graceful degradation with user feedback
- **File size limit**: Keep files under 200 lines, split if larger
- **No test files**: Use inline debugging (console.log, print statements)