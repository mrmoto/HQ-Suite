# Planning Session Agenda: Ecosystem Architecture

**Date**: 2025-12-24  
**Purpose**: Identify topics and questions needed to complete ecosystem architecture section

---

## Overview

This planning session addresses topics that need clarification before completing the ecosystem architecture section in MASTER_ARCHITECTURE.md. Some content can be created now with placeholders, but these topics require user input for accurate documentation.

---

## Topic 1: Multi-Suite Vision

### Questions

1. **Suite Structure**:
   - What is the web_scheduler suite? What apps will it contain?
   - How do suites relate to each other? (if at all)
   - Are there suite-level shared resources?

2. **Suite Organization**:
   - Will each suite have its own ecosystem architecture doc?
   - Or will there be a master ecosystem doc covering all suites?
   - How are suites organized in the file system?

### Current Knowledge
- Construction_Suite/ contains DigiDoc, HQ, Watcher
- Future suites mentioned: web_scheduler, future_suite_3
- Suite structure from workspace_organization_plan.md (now archived)

### Needed For
- Ecosystem Overview section
- App Layer Architecture section (future suites context)

---

## Topic 2: HQ Architecture Details

### Questions

1. **Architecture**:
   - What is HQ's detailed architecture? (beyond "Laravel dashboard")
   - What are HQ's main modules/features?
   - How does HQ handle tenant-aware data?

2. **Database Structure**:
   - What databases does HQ use?
   - How is tenant data organized?
   - What is the relationship between HQ databases and DigiDoc?

3. **Integration Points**:
   - How does HQ receive data from DigiDoc?
   - How does HQ provide templates to DigiDoc?
   - Are there other integration points?

### Current Knowledge
- HQ is Laravel PHP application
- Receives extracted data from DigiDoc
- Provides template storage and sync
- Tenant-aware architecture

### Needed For
- App Layer Architecture section (HQ description)
- App Relationships section (data flow)
- Integration Contracts section (HQ side of contracts)

---

## Topic 3: Future Callers of DigiDoc

### Questions

1. **What Applications**:
   - What applications will call DigiDoc in the future?
   - What are their purposes?
   - When will they be developed?

2. **Integration Pattern**:
   - Will they use the same integration contract as HQ?
   - Will they need different integration patterns?
   - How will `calling_app_id` be managed?

3. **Data Flow**:
   - Will they receive extracted data from DigiDoc?
   - Or will they use DigiDoc differently?

### Current Knowledge
- DigiDoc supports multiple calling applications via `calling_app_id`
- Integration contract designed for multiple callers
- Currently only HQ is a caller

### Needed For
- App Layer Architecture section (future callers)
- Integration Contracts section (multi-caller support)

---

## Topic 4: Data Ownership and Database Relationships

### Questions

1. **Data Ownership**:
   - Which app owns which data?
   - Are there shared databases?
   - How is data synchronized?

2. **Database Relationships**:
   - Does DigiDoc access HQ databases directly? (assumed: no)
   - Does Watcher access any databases? (assumed: no)
   - Are there any shared data stores?

3. **Template Storage**:
   - HQ is primary storage for templates
   - DigiDoc caches templates locally
   - Is this the correct ownership model?

### Current Knowledge
- HQ owns: Template definitions (primary), extracted document data
- DigiDoc owns: Template cache (local), queue items, processing metadata
- Watcher owns: Configuration, logs
- No direct database access between apps (assumed)

### Needed For
- App Relationships section (data ownership)
- Integration Contracts section (data ownership subsection)

---

## Topic 5: Communication Patterns and Protocols

### Questions

1. **Synchronous vs Asynchronous**:
   - Which integrations are synchronous? (Watcher → DigiDoc, DigiDoc → HQ)
   - Which are asynchronous? (DigiDoc queue processing)
   - Are there other async patterns?

2. **Error Handling**:
   - What happens if DigiDoc is unavailable when Watcher calls?
   - What happens if HQ is unavailable when DigiDoc calls?
   - Retry strategies?

3. **Protocols**:
   - All HTTP APIs? (assumed: yes)
   - Any other protocols? (WebSockets, gRPC, etc.)

### Current Knowledge
- Watcher → DigiDoc: HTTP API (synchronous)
- DigiDoc → HQ: HTTP API (synchronous)
- DigiDoc internal: Queue-based (asynchronous)
- Error handling: Watcher sends notifications if DigiDoc unavailable

### Needed For
- Integration Contracts section (communication patterns)
- App Relationships section (integration patterns)

---

## Topic 6: Workspace Structure Clarification

### Questions

1. **Architectural vs Planning**:
   - Is workspace directory structure an architectural decision?
   - Or is it just a development environment detail?
   - Should it be in MASTER_ARCHITECTURE.md?

2. **File Organization**:
   - Does workspace structure affect how apps are deployed?
   - Does it affect runtime behavior?
   - Or is it purely for development?

### Current Knowledge
- Workspace structure from workspace_organization_plan.md
- Multi-suite vision with individual workspace files
- User asked: "should 'Future Structure Vision' data be in MA?"

### Needed For
- Ecosystem Overview section (if architectural)
- Or exclude if planning-only

---

## Priority Classification

### High Priority (Blocking Ecosystem Architecture Section)

1. **HQ Architecture Details** - Needed for App Layer Architecture section
2. **Data Ownership** - Needed for App Relationships section
3. **Communication Patterns** - Needed for Integration Contracts section

### Medium Priority (Can Use Placeholders)

4. **Multi-Suite Vision** - Can document current suite, note future expansion
5. **Future Callers** - Can document pattern, note future applications

### Low Priority (Can Defer)

6. **Workspace Structure** - Can clarify during execution if needed

---

## Recommended Approach

### Option A: Proceed with Placeholders
- Create ecosystem architecture section with current knowledge
- Use placeholders/TBD for topics needing clarification
- Update after planning session

**Pros**: Can proceed with restructuring now  
**Cons**: Incomplete documentation

### Option B: Planning Session First
- Conduct planning session to resolve all topics
- Then create complete ecosystem architecture section

**Pros**: Complete documentation from start  
**Cons**: Delays restructuring

### Option C: Hybrid
- Proceed with high-confidence content
- Use placeholders for topics needing clarification
- Conduct planning session for remaining topics
- Update documentation after session

**Pros**: Balance between progress and completeness  
**Cons**: Requires follow-up updates

**Recommendation**: **Option C (Hybrid)**

---

## Planning Session Format

### Suggested Structure

1. **Review Current Understanding** (5 min)
   - Present current knowledge for each topic
   - Confirm accuracy

2. **Topic-by-Topic Discussion** (30-45 min)
   - Go through each topic
   - Ask specific questions
   - Document decisions

3. **Content Review** (10 min)
   - Review ecosystem architecture section draft
   - Identify gaps
   - Plan updates

### Questions Format

For each topic:
- What do we know? (current understanding)
- What do we need to know? (specific questions)
- What are the options? (if multiple approaches)
- What's the decision? (user decision)

---

## Next Steps

1. ✅ Planning session agenda created
2. ⏭️ User reviews agenda and schedules session (or provides answers)
3. ⏭️ Execute restructuring with current knowledge + placeholders (Task 6)
4. ⏭️ Update ecosystem architecture section after planning session

---

## Notes

- Some content can be created now based on current knowledge
- Planning session can happen in parallel with restructuring
- Documentation can be updated incrementally as decisions are made
- Focus on high-priority topics first

