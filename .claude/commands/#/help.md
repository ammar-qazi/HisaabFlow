# /#:help Command

This command activates the help mode for your AI assistant.

Usage: /#:help $ARGUMENTS

---

# Hash Prompts Help System

You are a helpful guide for the Hash Prompts collection. When invoked, provide a comprehensive overview of all available commands, their purposes, and how to use them effectively.

## Output Format

When the user types `/#:help`, provide the following information in a clear, organized manner:

```markdown
# 🚀 Hash Prompts - AI-Powered Development Pipeline

Hash Prompts is a comprehensive collection of AI prompts that guide you through the entire software development lifecycle, from ideation to deployment.

## 📋 Available Commands

### 🎯 Core Development Commands

**/#:pipeline start** - Initialize a new project pipeline
- Creates project structure and directories
- Checks for existing PRD documents
- Initializes research cache and shared research
- Sets up pipeline status tracking
- Guides you through the entire development lifecycle

**/#:brainstorm** - Transform your raw idea into a validated concept
- Performs parallel market research (8 searches simultaneously)
- Identifies potential pivots and improvements  
- Applies SLC (Simple, Lovable, Complete) validation
- Prevents feature creep with 80/20 rule analysis
- Creates a junior-friendly PRD draft
- Saves output to: `docs/#/brainstorm.md`

**/#:prd** - Create a comprehensive Product Requirements Document
- Conducts parallel research (6 searches simultaneously)
- Applies SLC framework validation to all features
- Prioritizes core features using anti-over-engineering principles
- Asks clarifying questions to fill gaps
- Generates domain-specific agents
- Saves output to: `docs/#/prd.md`

**/#:architect** - Design robust system architecture  
- Executes 15-20 parallel research searches
- Applies simplicity-first architecture principles
- Uses SLC-weighted technology selection criteria
- Validates against over-engineering with complexity checks
- Generates tech stack agents in `.claude/agents/`
- Saves output to: `docs/#/architect.md`

**/#:tasks** - Break down project into actionable tasks
- Parallel research for implementation details (6 searches)
- Creates atomic, well-defined tasks with SLC validation
- Applies YAGNI principles to task necessity
- Filters out over-engineering and speculative tasks
- Generates quality assurance agents
- Saves output to: `docs/#/tasks.md`

**/#:plan** - Create detailed implementation plan
- Validates all solutions against SLC principles
- Applies YAGNI enforcement to prevent over-engineering
- Develops sprint structure with anti-complexity checks
- Assigns priorities and timelines
- Identifies risks and mitigation strategies
- Saves output to: `docs/#/plan.md`

**/#:code** - Implement features with best practices
- Applies SLC coding principles (Simple, Lovable, Complete)
- Uses anti-over-engineering checklist before implementation
- Follows YAGNI to avoid premature optimization
- Writes clean, maintainable code
- Includes tests and documentation
- Updates task status in `tasks/active_context.md`

**/#:feature** - Add new features to existing project
- Integrates seamlessly with current codebase
- Updates relevant documentation
- Maintains backward compatibility
- Saves plans to: `docs/#/feature.md`

**/#:test** - Create comprehensive test strategies
- Designs unit, integration, and e2e tests
- Ensures adequate code coverage
- Validates edge cases
- Saves strategies to: `docs/#/test.md`

**/#:deploy** - Handle deployment and DevOps
- Creates CI/CD pipelines
- Configures infrastructure
- Sets up monitoring and logging
- Saves configs to: `docs/#/deploy.md`

### 🔄 Pipeline Orchestration

**/#:pipeline** - Orchestrate the entire workflow
- `/#:pipeline start` - Begin a new project with unique ID
- `/#:pipeline status` - Check current progress
- `/#:pipeline resume` - Continue from last stage
- `/#:pipeline validate` - Verify stage prerequisites
- `/#:pipeline reset` - Archive and start fresh
- `/#:pipeline agents` - List all project agents
- `/#:pipeline agents clean` - Remove outdated agents
- `/#:pipeline agents validate` - Check agent consistency
- `/#:pipeline suggest` - Get agent recommendations

### ℹ️ Information Commands

**/#:help** - Display this help message
- Shows all available commands
- Explains typical workflows
- Provides usage examples

## 🚀 Key Features

### Parallel Research Execution
- All modes execute searches simultaneously using Task agents
- Research time reduced by 60-80% (from minutes to seconds)
- Automatic caching prevents duplicate searches (24-hour cache)
- Shared research document builds knowledge across pipeline

### Agent Generation
- Automatic creation of specialized AI agents based on your project
- Domain experts, tech stack specialists, and quality assurance agents
- Agents persist across sessions and understand your project context

## 🔄 Typical Workflows

### 1️⃣ Full Project Development (Recommended)
```bash
/#:pipeline start                    # Initialize project tracking
/#:brainstorm "Your idea here"       # Validate and refine concept
/#:prd                              # Create detailed requirements
/#:architect                        # Design system architecture
/#:tasks                           # Break down into tasks
/#:plan                            # Create sprint plan
/#:code                            # Implement features
/#:test                            # Develop test suite
/#:deploy                          # Deploy to production
```

### 2️⃣ Quick Prototype
```bash
/#:brainstorm "Your idea"           # Quick validation
/#:prd                             # Simplified requirements
/#:code                            # Direct implementation
```

### 3️⃣ Adding Features
```bash
/#:feature "New feature description" # Plan feature addition
/#:code                             # Implement feature
/#:test                            # Test new functionality
```

### 4️⃣ Resuming Work
```bash
/#:pipeline status                  # Check where you left off
/#:pipeline resume                  # Get next steps
/#:[appropriate-command]            # Continue from last stage
```

## 🤖 Generated Agents

As you progress through the pipeline, specialized AI agents are automatically created:

### Domain Agents (from PRD stage)
- `[domain]-expert` - Industry-specific expertise
- `product-manager` - Product strategy and prioritization
- `compliance-officer` - Regulatory requirements (if applicable)
- `ux-designer` - User experience design (if UI-focused)

### Tech Stack Agents (from Architect stage)
- `[framework]-developer` - Frontend framework expertise
- `[language]-backend-developer` - Backend development
- `[database]-specialist` - Database optimization
- `devops-engineer` - Infrastructure and deployment

### Quality Agents (from Tasks stage)
- `code-reviewer` - Code quality and standards
- `test-engineer` - Testing strategies
- `documentation-writer` - Technical documentation
- `security-engineer` - Security best practices
- `performance-optimizer` - Performance tuning (if needed)

## 💾 File Organization

All outputs are saved for cross-session continuity:
```
docs/#/
├── brainstorm.md      # Concept validation
├── prd.md            # Requirements document
├── architect.md      # System design
├── tasks.md          # Task breakdown
├── plan.md           # Sprint planning
├── feature.md        # Feature additions
├── test.md           # Test strategies
├── deploy.md         # Deployment configs
└── pipeline.md       # Pipeline status

.claude/agents/       # Project-specific AI agents
tasks/               # Active development tracking
```

## 🎯 Best Practices

1. **Start with Pipeline**: Use `/#:pipeline start` to track your project
2. **Save Everything**: All modes auto-save outputs for continuity
3. **Follow the Flow**: Each stage builds on the previous one
4. **Use Generated Agents**: Leverage specialized agents for expertise
5. **Validate Progress**: Use `/#:pipeline validate` to check prerequisites
6. **Resume Anytime**: Your work persists across sessions

## 🆘 Need More Help?

- Check the pipeline status: `/#:pipeline status`
- Get agent suggestions: `/#:pipeline suggest`
- Review saved outputs in `docs/#/` directory
- Each mode provides detailed guidance when invoked

Ready to start? Try `/#:pipeline start` to begin your project! 🚀
```

## Additional Help Topics

When users ask for specific help (e.g., `/#:help brainstorm`), provide detailed information about that specific command, including:

1. **Purpose**: What the command does
2. **When to Use**: Appropriate scenarios
3. **Prerequisites**: What should be done first
4. **Process**: Step-by-step workflow
5. **Outputs**: What files are created/updated
6. **Next Steps**: What typically comes after
7. **Examples**: Sample usage

## Integration with Pipeline

If the user hasn't started a project yet, suggest:
```
💡 Tip: Start with `/#:pipeline start` to initialize project tracking and enable agent generation!
```

If they have an active project, show relevant context:
```
📊 Current Project Status:
- Active Stage: [Current stage from pipeline.md]
- Completed: [List completed stages]
- Next Step: [Recommended command]

Use `/#:pipeline status` for detailed progress.
```

Remember: The help system should be friendly, informative, and guide users toward successful project completion.