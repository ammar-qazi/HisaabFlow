# Main.py Size Control Guide

## [SUCCESS] Problem Solved: Main.py Under 300 Lines

We successfully reduced main.py from **651 lines → 94 lines** (85% reduction) using modular architecture.

## 🏗️ New Architecture

### Current Structure:
```
backend/
├── main.py (94 lines) ← CLEAN MODULAR VERSION
├── main_legacy.py (651 lines) ← LEGACY, DON'T USE
└── api/
    ├── config_endpoints.py (156 lines)
    ├── file_endpoints.py (51 lines)
    ├── parse_endpoints.py (220 lines)
    ├── transform_endpoints.py (209 lines)
    └── middleware.py (14 lines)
```

### Key Changes:
- **main.py**: Only app setup, CORS, router inclusion (CLEAN VERSION)
- **main_legacy.py**: Old bloated version (DO NOT USE)
- **Endpoints**: Moved to specialized router modules
- **Business Logic**: Delegated to service classes
- **Monitoring**: Automated size checking

## 🚫 Rules to Prevent Growth

### 1. NEVER Add Endpoints to Main File
```python
# ❌ DON'T DO THIS IN main.py
@app.post("/some-endpoint")
async def some_function():
    # Complex logic here
    pass

# [SUCCESS] DO THIS INSTEAD - Create in appropriate api/ module
# Add to api/new_endpoints.py, then include router
```

### 2. Use Router Pattern
```python
# In api/your_endpoints.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/your-endpoint")
async def your_function():
    pass

# In main.py
from api.your_endpoints import router as your_router
app.include_router(your_router, tags=["your-feature"])
```

### 3. Delegate Business Logic
```python
# ❌ DON'T implement complex logic in endpoints
@router.post("/complex-operation")
async def complex_operation():
    # 50+ lines of complex logic here
    pass

# [SUCCESS] DO delegate to service classes
@router.post("/complex-operation")
async def complex_operation():
    service = ComplexOperationService()
    return service.process()
```

## 📏 Monitoring Strategy

### 1. Run Size Check Regularly
```bash
cd backend
python3 check_file_sizes.py
```

### 2. Size Limits:
- **main.py**: 300 lines max (clean modular version)
- **API modules**: 300 lines max each
- **Service classes**: 300 lines max each

### 3. Refactoring Triggers:
- File reaches 250 lines → Plan refactoring
- File reaches 300 lines → Immediate refactoring required

## 🔧 When Files Get Too Large

### For API Modules (> 300 lines):
1. **Split by functionality**: Create sub-routers
2. **Extract services**: Move logic to service classes
3. **Create utilities**: Move helper functions to utils/

### For Service Classes (> 300 lines):
1. **Single Responsibility**: Split into focused classes
2. **Composition**: Use multiple smaller classes
3. **Strategy Pattern**: Extract algorithms to strategies

### Example Refactoring:
```python
# Before: Large API module (400+ lines)
# api/large_endpoints.py

# After: Split into focused modules
# api/user_endpoints.py (150 lines)
# api/admin_endpoints.py (180 lines)
# services/user_service.py (200 lines)
# services/admin_service.py (220 lines)
```

## Best Practices

### 1. Start New Features Right
- Create new router in api/
- Create service class if needed
- Include router in main.py
- Keep main.py unchanged otherwise

### 2. Regular Maintenance
- Run file size check weekly
- Refactor before limits are hit
- Document refactoring decisions

### 3. Code Review Focus
- Check file sizes in every PR
- Reject PRs that bloat main.py
- Suggest modular alternatives

## [START] Current Status
- [SUCCESS] **main.py**: 94/300 lines (healthy, clean modular version)
- [SUCCESS] **All API modules**: Under 300 lines
- [SUCCESS] **Monitoring**: Automated with check_file_sizes.py
- [SUCCESS] **Start script**: Updated to use main.py
- [SUCCESS] **Legacy**: main_legacy.py (651 lines) preserved but unused

## 📞 Emergency Procedure
If main.py exceeds 300 lines:

1. **Stop adding to it immediately**
2. **Run**: `python3 check_file_sizes.py`
3. **Identify**: What was added recently
4. **Extract**: Move new code to appropriate api/ module
5. **Test**: Ensure functionality still works
6. **Document**: Update this guide if needed

---
**Remember**: The goal is maintainable, focused modules. A 100-line main file is better than a 200-line main file!
