# Template Search Logic: How Templates Are Found and What Happens When None Exist

**Purpose**: Detailed explanation of template matching search behavior, "no template found" criteria, and current vs. future handling.

**Last Updated**: 2025-12-24

---

## 1. How Does It Search?

### Search Process Flow

The template search happens in `match_template()` function (`apps/digidoc/ocr_service/tasks/matching_task.py`):

```python
# Step 1: Compute structural fingerprint of the document image
image_fingerprint = compute_structural_fingerprint(image)

# Step 2: Query database for templates
templates = session.query(CachedTemplate).filter(
    CachedTemplate.calling_app_id == calling_app_id,
    CachedTemplate.structural_fingerprint.isnot(None)
).all()

# Step 3: Compare fingerprints
for template in templates:
    score = compare_fingerprints(image_fingerprint, template.structural_fingerprint)
    if score > best_score:
        best_score = score
        best_match = template
```

### Search Criteria

**Database Query Filters:**
1. **`calling_app_id`**: Must match the calling application (e.g., "hq", "test_app")
   - **Purpose**: Templates are scoped to applications
   - **Example**: Templates from "hq" won't match documents from "test_app"

2. **`structural_fingerprint.isnot(None)`**: Template must have a computed fingerprint
   - **Purpose**: Only templates with fingerprints can be matched
   - **Note**: Templates without fingerprints are excluded from search

**No Additional Filters Currently:**
- ❌ **Document type** (receipt, contract, etc.) - NOT filtered
- ❌ **Vendor name** - NOT filtered
- ❌ **Format name** - NOT filtered
- ❌ **Active status** - NOT filtered

**Future Enhancement**: These filters may be added for performance optimization, but currently all templates for the calling app are compared.

### Comparison Algorithm

**Structural Fingerprint Matching** (`matching/structural.py`):

1. **Zone Detection**: Detects contours and classifies zones (header, table, footer, logo, other)
2. **Ratio Calculation**: Converts absolute pixel positions to ratios (0.0-1.0) relative to image dimensions
   - Makes matching DPI/scale invariant
3. **Score Calculation**: Compares fingerprints using:
   - Zone count similarity (30% weight)
   - Total content area ratio (20% weight)
   - Zone position/size ratios (50% weight)
4. **Result**: Returns score between 0.0 (no match) and 1.0 (perfect match)

**All Templates Compared**: The system compares the document against **every** template in the database (for the calling app) and returns the **best match** (highest score).

---

## 2. Criteria for "No Template Found"

There are **three distinct scenarios** that result in "no template found":

### Scenario A: No Templates in Database

**Criteria:**
- Database query returns zero templates
- `len(templates) == 0`

**Detection:**
```python
if len(templates) == 0:
    return {
        'matched_template_id': None,
        'match_score': 0.0,
        'template_name': None,
        ...
    }
```

**Causes:**
- Database is empty (new installation)
- No templates synced from calling application yet
- All templates deleted
- Wrong `calling_app_id` (no templates for that app)

### Scenario B: Templates Exist But None Have Fingerprints

**Criteria:**
- Templates exist in database for `calling_app_id`
- But all have `structural_fingerprint = NULL`

**Detection:**
- Query filters out templates without fingerprints: `.filter(CachedTemplate.structural_fingerprint.isnot(None))`
- Results in same behavior as Scenario A (empty result set)

**Causes:**
- Templates synced but fingerprints not computed yet
- Template sync process didn't generate fingerprints
- Fingerprint computation failed for all templates

### Scenario C: Templates Exist But No Good Match

**Criteria:**
- Templates exist with fingerprints
- All comparison scores are very low (e.g., < 0.10)
- `best_match` is `None` or `best_score` is effectively 0.0

**Detection:**
```python
best_match = None
best_score = 0.0

for template in templates:
    score = compare_fingerprints(...)
    if score > best_score:
        best_score = score
        best_match = template

# If best_score is still 0.0, no good match found
```

**Causes:**
- Document structure is completely different from all templates
- Document is corrupted or unreadable
- Document type mismatch (e.g., receipt vs. contract template)
- Templates are outdated (vendor changed format)

**Note**: Currently, even a very low score (e.g., 0.05) will still return a "match" with that template. Future enhancement may add a minimum threshold.

---

## 3. Current Behavior vs. Future Behavior

### Current Behavior (Phase 1 Skeleton)

#### When No Templates Found (Scenarios A or B)

**In `match_template()`:**
```python
if len(templates) == 0:
    return {
        'matched_template_id': None,
        'match_score': 0.0,  # Explicit 0.0
        'template_name': None,
        'visualization_path': None,
        'fingerprint': image_fingerprint
    }
```

**In `process_receipt_task()`:**
```python
match_result = match_template(...)
best_score = match_result.get('match_score', 0.0)  # Gets 0.0

if best_score == 0.0:
    # No templates exist in database
    best_score = fallback_confidence  # Uses 0.85 from skeleton.yaml
    print(f"No templates found in database, using fallback confidence: {fallback_confidence}")
```

**Result:**
- ✅ **Status**: Uses `fallback_confidence` (default 0.85) from `skeleton.yaml`
- ✅ **Decision**: If `fallback_confidence >= auto_match_threshold`, goes to `'completed'` status
- ✅ **Template**: Uses mock template name from `skeleton.yaml`
- ⚠️ **Issue**: May auto-complete even though no real match exists

**Current Flow:**
```
No Templates → match_score = 0.0 → fallback_confidence (0.85) → 
  → If 0.85 >= threshold → 'completed' status
  → If 0.85 < threshold → 'review' status
```

#### When Templates Exist But No Good Match (Scenario C)

**In `match_template()`:**
```python
# Returns best match even if score is very low
result = {
    'matched_template_id': best_match.template_id if best_match else None,
    'match_score': float(best_score),  # Could be 0.05, 0.10, etc.
    ...
}
```

**In `process_receipt_task()`:**
```python
best_score = match_result.get('match_score', 0.0)  # Gets actual low score

# Decision logic uses actual score
if best_score >= auto_match_threshold:  # e.g., >= 0.85
    status = 'completed'
else:
    status = 'review'
```

**Result:**
- ✅ **Status**: Uses actual match score
- ✅ **Decision**: Low scores (< 0.85) go to `'review'` status
- ✅ **Template**: Returns matched template (even if low confidence)
- ⚠️ **Issue**: Very low scores (e.g., 0.05) still return a template match

---

### Future Behavior (Production)

#### When No Templates Found (Scenarios A or B)

**Planned Changes:**

1. **Explicit "No Templates" Status**:
   ```python
   if len(templates) == 0:
       return {
           'status': 'no_templates',
           'matched_template_id': None,
           'match_score': 0.0,
           'message': 'No templates available for matching',
           ...
       }
   ```

2. **Always Route to Review**:
   - No templates → Always `'review'` status
   - Never auto-complete when no templates exist
   - User must manually create/select template

3. **Notification/Alert**:
   - Log warning: "No templates found for calling_app_id: {id}"
   - GUI shows: "No templates available - please sync templates from calling application"
   - Admin notification (email/Slack) if templates expected but missing

4. **Template Sync Trigger**:
   - Automatically trigger template sync from calling application
   - Retry matching after sync completes

**Future Flow:**
```
No Templates → status = 'no_templates' → Always 'review' status → 
  → GUI shows "No templates available" → 
  → User triggers template sync → Retry matching
```

#### When Templates Exist But No Good Match (Scenario C)

**Planned Changes:**

1. **Minimum Match Threshold**:
   ```python
   MIN_MATCH_THRESHOLD = 0.20  # Configurable
   
   if best_score < MIN_MATCH_THRESHOLD:
       return {
           'status': 'no_match',
           'matched_template_id': None,
           'match_score': best_score,
           'message': f'No templates match (best score: {best_score:.2f})',
           'suggestions': top_3_templates  # For GUI display
       }
   ```

2. **Tiered Suggestions**:
   - Return top 3-5 templates even if below threshold
   - GUI shows: "No strong match found, but these templates are similar:"
   - User can manually select from suggestions

3. **Template Drift Detection**:
   - If score is 0.60-0.85: Flag as "partial match" or "template variant"
   - Suggest creating new template variant
   - GUI: "This might be a variant of {template_name}"

4. **Enhanced Matching**:
   - Add feature detection (ORB keypoints) - 20% weight
   - Add text fallback matching - 10% weight
   - Combined score: `(0.7 × structural) + (0.2 × feature) + (0.1 × text)`

**Future Flow:**
```
Low Score (< 0.20) → status = 'no_match' → 'review' status → 
  → GUI shows tiered suggestions → 
  → User selects template or creates new one
```

---

## Summary Table

| Scenario | Current Behavior | Future Behavior |
|----------|------------------|-----------------|
| **No templates in DB** | Uses `fallback_confidence` (0.85), may auto-complete | Always `'review'`, triggers template sync, shows alert |
| **Templates but no fingerprints** | Same as no templates | Computes fingerprints automatically, retries matching |
| **Templates but no good match** | Returns best match (even if 0.05), uses actual score | Returns `'no_match'` if < threshold, shows tiered suggestions |
| **Low match (0.60-0.85)** | Goes to `'review'` | Flags as "variant", suggests creating new template |
| **Good match (>0.85)** | Auto-completes | Auto-completes (same) |

---

## Configuration

**Current Config** (`development/skeleton.yaml`):
```yaml
template_matching:
  fallback_confidence: 0.85  # Used when no templates exist
  use_mock_matching: false   # Real matching is default
```

**Future Config** (`digidoc_config.yaml`):
```yaml
matching:
  min_match_threshold: 0.20      # Minimum score to consider a match
  auto_match_threshold: 0.85    # Score for auto-completion
  partial_match_threshold: 0.60  # Score for tiered suggestions
  no_templates_behavior: "review"  # Always review if no templates
  trigger_sync_on_no_templates: true
```

---

## Related Files

- **Search Logic**: `apps/digidoc/ocr_service/tasks/matching_task.py`
- **Task Integration**: `apps/digidoc/ocr_service/tasks/receipt_tasks.py` (lines 219-245)
- **Fingerprint Algorithm**: `apps/digidoc/ocr_service/matching/structural.py`
- **Database Model**: `apps/digidoc/ocr_service/database/models.py` (CachedTemplate)
- **Architecture**: `shared_documentation/architecture/MASTER_ARCHITECTURE.md` (sections on matching)

---

## Notes

- **Current implementation is MVP/skeleton**: Designed to work even with empty database
- **Future enhancements**: Will add better handling, notifications, and user guidance
- **Template sync**: Will be implemented to automatically populate templates from calling application
- **GUI integration**: Streamlit GUI will show appropriate messages for each scenario

