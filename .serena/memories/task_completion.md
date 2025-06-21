# HisaabFlow - Task Completion Checklist

## When a Task is Completed

### Code Quality Checks
1. **File size validation**
   - Check CODEBASE_MAP.md for current file sizes
   - Ensure no files exceed 200 lines
   - Split large files if necessary

2. **Functionality verification**
   - Test with running application (./start_app.sh)
   - Verify both frontend and backend work together
   - Check API endpoints respond correctly

3. **Code cleanliness**
   - Remove unnecessary console.log/print statements
   - Ensure proper error handling
   - Verify imports are correct

### Documentation Updates
1. **Update CURRENT_STATE.md**
   - Document progress made
   - List next logical steps
   - Note any blockers or decisions needed

2. **Update CODEBASE_MAP.md**
   - Add new files created
   - Update line counts for modified files
   - Mark files as compliant or needing attention

### Final Validation
1. **Manual testing**
   - Upload a sample CSV file
   - Verify parsing works correctly
   - Check export functionality
   - Test error handling

2. **Integration testing**
   - Ensure frontend communicates with backend
   - Verify API responses are correct
   - Check file upload/download works

### No Automated Tools Required
- **No linting tools** configured (inline style checking only)
- **No formatting tools** required (manual code style)
- **No test runners** (inline debugging approach)
- **No build verification** beyond manual testing

### Session Handoff
- **Document decisions made** in CURRENT_STATE.md
- **List remaining work** for next session
- **Note any architectural choices** for future reference