# HisaabFlow - Simplified Product Requirements

## Project Scope (Simplified)
**Desktop-local bank data consolidation app for personal budgeting and accounting**

### Core Requirements
1. **Local-only processing** - All data stays on user's machine
2. **Multi-bank support** - Import CSV statements from different banks
3. **Data consolidation** - Standardize transaction formats
4. **Transfer detection** - Match transfers between accounts
5. **Export functionality** - Clean data for budgeting tools

### Explicitly OUT of Scope
- ❌ Cloud processing or storage
- ❌ AI/ML features  
- ❌ Error log collection
- ❌ User analytics or telemetry
- ❌ Multi-user support
- ❌ Real-time bank API integration

### Success Metrics
- User can import statements from 3+ different banks
- Transfer detection accuracy >90%
- Clean export ready for budgeting apps
- Desktop app runs entirely offline

### Target User
Individual users who:
- Use multiple banks/accounts
- Want to consolidate transactions for budgeting
- Prefer local/private data processing
- Export to tools like YNAB, Mint alternatives, or spreadsheets

### Technical Constraints
- Desktop application (Electron + React frontend)
- Python backend for processing
- No external API calls required
- Cross-platform compatibility (Windows, macOS, Linux)