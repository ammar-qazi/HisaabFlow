# App.conf Centralization - Planning Document

## Session: 2025-07-26

### Phase 1: Requirements and Clarifications

#### Initial Problem Analysis
After examining all bank configuration files (wise.conf, nayapay.conf, Erste.conf, revolut.conf), I've identified significant duplication in categorization patterns:

**Cross-Bank Duplicated Patterns:**
- **Groceries**: LIDL, ALDI (in wise.conf, Erste.conf)
- **Entertainment**: Netflix, Spotify (in wise.conf, nayapay.conf, revolut.conf)  
- **Shopping**: Amazon, SHEIN (in wise.conf, Erste.conf, revolut.conf)
- **Food/Dining**: Burger King (in wise.conf, Erste.conf)
- **Transport**: Gas Station, Taxi (in wise.conf, nayapay.conf)
- **Default rules**: positive_amount = Income, negative_amount = Expense, zero_amount = Transfer (ALL files)

#### Questions for Clarification

1. **Precedence Strategy**: When there's a conflict between generic patterns in app.conf and bank-specific patterns, which should take precedence?
   - Example: app.conf says `Lidl.* = Groceries`, wise.conf says `Lidl.* = Shopping` - which wins?

2. **Pattern Scope**: Should we move ALL common patterns to app.conf, or only the most universal ones?
   - Universal patterns: Netflix, Amazon, Uber, McDonald's, etc.
   - Regional patterns: Hungarian stores (CBA, TESCO) might only apply to Erste
   - Currency-specific patterns: Different regions use different services

3. **Backward Compatibility**: Do we need to maintain support for existing bank configs that haven't been updated yet?

4. **Configuration Inheritance Model**: Should bank configs be able to:
   - Override generic patterns completely?
   - Extend generic patterns with additional rules?
   - Only add bank-specific patterns while inheriting all generic ones?

5. **Multi-Language Support**: I notice Hungarian patterns in Erste.conf (like "Gyógyszertár" = Health). Should generic patterns support multiple languages for the same merchants?

6. **Default Rules**: Should the standard default category rules (`positive_amount = Income`, etc.) be moved to app.conf as well?

7. **Performance Considerations**: Are there any performance requirements for pattern matching that might affect how we structure the inheritance system?

#### User Responses
1. **Precedence Strategy**: Bank-specific patterns take precedence - apply first, then generic patterns for uncategorized transactions
2. **Pattern Scope**: Move both universal AND regional patterns that apply to multiple banks (e.g., TESCO across EU). Target 80-90% coverage of usual transactions  
3. **Backward Compatibility**: Not needed - development mode
4. **Configuration Inheritance**: Bank-specific first, then generic (same as #1)
5. **Multi-Language Support**: English patterns only for now
6. **Default Rules**: Yes, move to app.conf 
7. **Performance**: No concerns

### Phase 2: Research and Analysis

#### Configuration Inheritance Research
**Modern Pattern (2025)**: Hierarchical inheritance with "specific wins" principle
- Base → Regional → Bank-Specific → Account-Type configurations
- Best-match precedence: Position > Length > Specificity > Context > Recency
- Industry uses YAML for structure with schema validation and hot-reload

#### Transaction Categorization Research  
**Coverage Strategy for 80-90% International Transactions**:
- **Universal Patterns (40-50%)**: Top 100 global merchants (Netflix, Amazon, McDonald's, Uber)
- **MCC-Based Fallback (30-40%)**: ISO 18245:2023 standard categories
- **Regional Patterns (10-20%)**: EU chains like TESCO, regional naming conventions

**Technical Approaches**: Exact matching → Fuzzy matching (85% similarity) → MCC fallback → ML enhancement

### Phase 3: Solution Formulation

#### Selected Solution: Two-Tier Inheritance Model

**Architecture**: Simple two-tier precedence system
1. **Bank-specific patterns** (highest priority - apply first)
2. **App-wide patterns** (fallback for uncategorized transactions)

**Precedence Flow:**
1. Apply bank-specific categorization patterns first
2. For transactions still uncategorized, apply app-wide patterns
3. Default rules as final fallback

#### App-wide Pattern Strategy
- **Universal merchants**: Netflix, Amazon, McDonald's, Uber, etc.
- **Regional chains**: TESCO, LIDL, ALDI (useful across EU)
- **Common categories**: Gas stations, pharmacies, etc.
- **Target**: 80-90% coverage for typical users

### Phase 4: Implementation Plan

#### Step 1: Enhanced app.conf Structure
Add new `[app_wide_categorization]` section with universal patterns:
- Entertainment: Netflix, Spotify
- Shopping: Amazon, SHEIN, H&M, DECATHLON, etc.
- Groceries: LIDL, ALDI, TESCO, SPAR, etc.
- Food: Burger King, KFC, McDonald's, Pizza, Starbucks
- Transport: Gas Station, Taxi, Uber, Careem, Bolt
- Health: Pharmacy, Patika
- Travel: Booking.com, Hotel, FLIXBUS

Move `[default_category_rules]` from individual banks to app.conf

#### Step 2: Clean Up Bank Configs
- Remove all patterns that now exist in app.conf
- Keep only bank-specific patterns (e.g., Wise-specific cleaning rules)
- Maintain bank-specific detection and parsing configurations

#### Step 3: Update Processing Logic
- Implement two-tier precedence: Bank-specific → App-wide → Default
- Add pattern source tracking for debugging
- Ensure bank patterns are applied first, app-wide patterns catch remaining

#### Step 4: Implementation Tasks
1. **Backend**: Update config parser and categorization engine
2. **Configuration**: Enhance app.conf, clean bank configs
3. **Testing**: Validate precedence and coverage targets

### Risk Analysis
| Risk | Impact | Mitigation |
|------|--------|------------|
| Pattern conflicts | Medium | Clear precedence rules, testing |
| Coverage gaps | Low | Comprehensive pattern analysis done |
| Performance impact | Low | Simple string matching, minimal overhead |

### Success Criteria
- ✅ Bank-specific patterns take precedence over app-wide
- ✅ 80-90% transaction categorization coverage
- ✅ No duplicate patterns across configs
- ✅ Existing functionality maintained
- ✅ Clean, maintainable configuration structure

### Next Steps
Ready for implementation - proceed with ExitPlanMode to move to coding phase.
