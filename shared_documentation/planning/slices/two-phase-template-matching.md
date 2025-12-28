# Future Requirement: Two-Phase Template Matching for Performance

**Status**: Future Enhancement  
**Priority**: Medium (becomes critical at 100+ templates)  
**Last Updated**: 2025-12-24

---

## Problem Statement

### Current Limitations

**Current Implementation:**
- **Brute Force Approach**: Compares document against ALL templates in database
- **Complexity**: O(n) where n = number of templates
- **Per-Comparison Cost**: 
  - Zone detection and classification
  - Zone-by-zone Euclidean distance calculations
  - Weighted score computation (zone count, area, positions)
- **Filtering**: Only by `calling_app_id` (may not always be available)

**Performance Characteristics:**
- **< 10 templates**: Negligible impact (~10-50ms)
- **10-50 templates**: Acceptable (~50-200ms)
- **50-100 templates**: Noticeable delay (~200-500ms)
- **100-1000 templates**: Significant performance degradation (~500ms-5s)
- **1000+ templates**: Unacceptable for production (~5s+)

### Future Requirements

1. **No `calling_app_id` Filter**: Many documents may not have associated calling app
   - Need to search across ALL templates (not just per-app)
   - Makes optimization even more critical

2. **Scale**: Template library will grow over time
   - Initial: 10-50 templates
   - Short-term: 100-500 templates
   - Long-term: 1000+ templates (multiple vendors, formats, document types)

3. **Real-Time Processing**: Documents need fast matching for good UX
   - Target: < 200ms for matching phase
   - Current approach won't scale

---

## Proposed Solution: Two-Phase Matching

### Phase 1: Coarse Fingerprint (Fast Filtering)

**Purpose**: Quickly narrow down to top N candidates (e.g., 10-20)

**Coarse Fingerprint Structure:**
```python
{
    'zone_count': int,              # Number of zones detected
    'total_content_area_ratio': float,  # Total content / image area
    'aspect_ratio': float,          # width / height
    'zone_type_distribution': {    # Count of each zone type
        'header': int,
        'table': int,
        'footer': int,
        'logo': int,
        'other': int
    }
}
```

**Comparison Method:**
- Simple distance calculation on 5-7 scalar values
- Fast: O(1) per template (vs. O(zones) for fine comparison)
- Can use database indexing or in-memory filtering

**Implementation Options:**

**Option A: Database Indexing**
- Store coarse fingerprint as separate JSON column
- Create indexes on key fields (zone_count, total_content_area_ratio)
- Query with range filters to get candidates
- **Pros**: Leverages database optimization
- **Cons**: Requires schema changes, more complex queries

**Option B: In-Memory Filtering**
- Load all templates into memory (or cache)
- Filter by coarse fingerprint similarity
- Return top N candidates
- **Pros**: Simple, no schema changes
- **Cons**: Memory usage, still loads all templates

**Option C: Hybrid Approach** (Recommended)
- Database indexes for initial filtering (zone_count range, area range)
- In-memory coarse comparison on filtered set
- Return top N for fine comparison
- **Pros**: Best of both worlds
- **Cons**: More complex implementation

### Phase 2: Fine Fingerprint (Detailed Comparison)

**Purpose**: Detailed comparison on top N candidates only

**Fine Fingerprint Structure:**
- Current full structural fingerprint (zone-by-zone ratios)
- All zone positions, sizes, types
- Full comparison algorithm (current implementation)

**Comparison Method:**
- Use existing `compare_fingerprints()` function
- Only run on top N candidates from Phase 1
- Returns best match with detailed score

---

## Performance Analysis

### Estimated Time Savings

**Assumptions:**
- Coarse comparison: ~0.1ms per template
- Fine comparison: ~2ms per template
- Database query: ~10-50ms (depends on size)

**Scenario 1: 100 Templates**
- **Current**: 100 × 2ms = 200ms
- **Two-Phase**: 100 × 0.1ms (coarse) + 10 × 2ms (fine) = 10ms + 20ms = 30ms
- **Savings**: ~85% faster (170ms saved)

**Scenario 2: 500 Templates**
- **Current**: 500 × 2ms = 1000ms (1 second)
- **Two-Phase**: 500 × 0.1ms (coarse) + 10 × 2ms (fine) = 50ms + 20ms = 70ms
- **Savings**: ~93% faster (930ms saved)

**Scenario 3: 1000 Templates**
- **Current**: 1000 × 2ms = 2000ms (2 seconds)
- **Two-Phase**: 1000 × 0.1ms (coarse) + 10 × 2ms (fine) = 100ms + 20ms = 120ms
- **Savings**: ~94% faster (1880ms saved)

**Note**: Actual times will vary based on:
- Image complexity (more zones = slower)
- Database query performance
- Hardware performance
- Network latency (if database is remote)

### When to Implement

**Recommended Thresholds:**

| Template Count | Priority | Implementation Timeline |
|----------------|----------|------------------------|
| < 50 | Low | Not needed yet |
| 50-100 | Medium | Plan for implementation |
| 100-500 | High | Should implement soon |
| 500+ | Critical | Must implement |

**Decision Point**: Implement when matching time exceeds 200ms or user complaints about slowness.

---

## Implementation Design

### Database Schema Changes

**Add Coarse Fingerprint Column:**
```python
class CachedTemplate(Base):
    ...
    structural_fingerprint = Column(JSON, nullable=True)  # Fine fingerprint (existing)
    coarse_fingerprint = Column(JSON, nullable=True)     # NEW: Coarse fingerprint
    zone_count = Column(Integer, nullable=True, index=True)  # NEW: Indexed for fast filtering
    total_content_area_ratio = Column(Float, nullable=True, index=True)  # NEW: Indexed
```

**Indexes:**
- `zone_count` (for range queries)
- `total_content_area_ratio` (for range queries)
- Composite index: `(zone_count, total_content_area_ratio)` (for combined filtering)

### Algorithm Flow

```python
def match_template_two_phase(image_path: str, queue_item_id: str, calling_app_id: Optional[str] = None):
    # Phase 1: Compute coarse fingerprint
    image_coarse = compute_coarse_fingerprint(image)
    
    # Phase 1: Filter templates (database query with indexes)
    candidates = session.query(CachedTemplate).filter(
        # Range filters on indexed fields
        CachedTemplate.zone_count.between(
            image_coarse['zone_count'] - 2,
            image_coarse['zone_count'] + 2
        ),
        CachedTemplate.total_content_area_ratio.between(
            image_coarse['total_content_area_ratio'] - 0.1,
            image_coarse['total_content_area_ratio'] + 0.1
        )
    )
    
    if calling_app_id:
        candidates = candidates.filter(CachedTemplate.calling_app_id == calling_app_id)
    
    # Phase 1: Coarse comparison on filtered set
    coarse_scores = []
    for template in candidates:
        score = compare_coarse_fingerprints(image_coarse, template.coarse_fingerprint)
        coarse_scores.append((template, score))
    
    # Sort and take top N
    coarse_scores.sort(key=lambda x: x[1], reverse=True)
    top_candidates = [t for t, s in coarse_scores[:10]]  # Top 10
    
    # Phase 2: Fine comparison on top candidates
    image_fine = compute_structural_fingerprint(image)  # Full fingerprint
    best_match = None
    best_score = 0.0
    
    for template in top_candidates:
        score = compare_fingerprints(image_fine, template.structural_fingerprint)
        if score > best_score:
            best_score = score
            best_match = template
    
    return {
        'matched_template_id': best_match.template_id if best_match else None,
        'match_score': best_score,
        ...
    }
```

### Coarse Fingerprint Computation

```python
def compute_coarse_fingerprint(image: np.ndarray) -> Dict[str, Any]:
    """
    Compute lightweight coarse fingerprint for fast filtering.
    
    Returns:
        {
            'zone_count': int,
            'total_content_area_ratio': float,
            'aspect_ratio': float,
            'zone_type_distribution': {
                'header': int,
                'table': int,
                'footer': int,
                'logo': int,
                'other': int
            }
        }
    """
    h, w = image.shape[:2]
    aspect_ratio = w / h
    
    # Quick zone detection (simplified, faster)
    # Could use downsampled image or simplified contour detection
    zones = detect_zones_fast(image)  # Simplified version
    
    zone_type_dist = {
        'header': 0,
        'table': 0,
        'footer': 0,
        'logo': 0,
        'other': 0
    }
    
    total_area = 0
    for zone in zones:
        zone_type_dist[zone['type']] += 1
        total_area += zone['area']
    
    total_content_area_ratio = total_area / (w * h)
    
    return {
        'zone_count': len(zones),
        'total_content_area_ratio': total_content_area_ratio,
        'aspect_ratio': aspect_ratio,
        'zone_type_distribution': zone_type_dist
    }

def compare_coarse_fingerprints(coarse1: Dict, coarse2: Dict) -> float:
    """
    Fast comparison of coarse fingerprints.
    
    Returns similarity score (0.0-1.0).
    """
    # Zone count similarity
    count_diff = abs(coarse1['zone_count'] - coarse2['zone_count'])
    max_count = max(coarse1['zone_count'], coarse2['zone_count'], 1)
    count_score = 1.0 - (count_diff / max_count)
    
    # Area ratio similarity
    area_diff = abs(coarse1['total_content_area_ratio'] - coarse2['total_content_area_ratio'])
    area_score = 1.0 - min(area_diff, 1.0)
    
    # Aspect ratio similarity
    aspect_diff = abs(coarse1['aspect_ratio'] - coarse2['aspect_ratio'])
    aspect_score = 1.0 - min(aspect_diff, 1.0)
    
    # Zone type distribution similarity
    dist1 = coarse1['zone_type_distribution']
    dist2 = coarse2['zone_type_distribution']
    type_scores = []
    for zone_type in ['header', 'table', 'footer', 'logo', 'other']:
        count1 = dist1.get(zone_type, 0)
        count2 = dist2.get(zone_type, 0)
        if count1 + count2 == 0:
            type_scores.append(1.0)  # Both zero = match
        else:
            type_scores.append(1.0 - abs(count1 - count2) / max(count1, count2, 1))
    type_score = np.mean(type_scores)
    
    # Weighted combination
    overall_score = (
        0.3 * count_score +
        0.3 * area_score +
        0.2 * aspect_score +
        0.2 * type_score
    )
    
    return float(np.clip(overall_score, 0.0, 1.0))
```

---

## Trade-offs and Considerations

### Advantages

1. **Performance**: 85-94% faster at scale (100+ templates)
2. **Scalability**: Handles 1000+ templates efficiently
3. **Flexibility**: Can adjust N (top candidates) based on performance needs
4. **Backward Compatible**: Can fall back to single-phase if needed
5. **Database Optimization**: Leverages indexes for fast filtering

### Disadvantages

1. **Complexity**: More complex implementation
2. **Schema Changes**: Requires database migration
3. **Storage**: Additional column for coarse fingerprints
4. **Maintenance**: Need to keep coarse fingerprints in sync
5. **Potential Misses**: If coarse filtering is too aggressive, might miss good matches

### Mitigation Strategies

1. **Configurable N**: Make top N candidates configurable (default 10, can increase if needed)
2. **Fallback**: If no good match in top N, expand search or use single-phase
3. **Tolerance Ranges**: Use wider ranges in Phase 1 to avoid missing matches
4. **Monitoring**: Track match quality to ensure coarse filtering isn't too aggressive

---

## Implementation Plan

### Phase 1: Research & Design (1-2 days)
- [ ] Benchmark current performance at various template counts
- [ ] Design coarse fingerprint structure
- [ ] Design database schema changes
- [ ] Create detailed implementation plan

### Phase 2: Database Schema (1 day)
- [ ] Add `coarse_fingerprint` column
- [ ] Add indexes (`zone_count`, `total_content_area_ratio`)
- [ ] Migration script for existing templates
- [ ] Backfill coarse fingerprints for existing templates

### Phase 3: Coarse Fingerprint Implementation (2-3 days)
- [ ] Implement `compute_coarse_fingerprint()`
- [ ] Implement `compare_coarse_fingerprints()`
- [ ] Optimize zone detection for speed
- [ ] Unit tests

### Phase 4: Two-Phase Matching (2-3 days)
- [ ] Implement `match_template_two_phase()`
- [ ] Database query optimization
- [ ] Integration with existing code
- [ ] Performance testing

### Phase 5: Testing & Tuning (2-3 days)
- [ ] Performance benchmarks
- [ ] Accuracy testing (ensure no matches missed)
- [ ] Tune N (top candidates) and tolerance ranges
- [ ] Load testing with large template sets

**Total Estimated Time**: 8-12 days

---

## Configuration

**Future Config** (`digidoc_config.yaml`):
```yaml
matching:
  # Two-phase matching settings
  two_phase_enabled: true
  coarse_candidates: 10  # Number of candidates for fine comparison
  coarse_tolerance:
    zone_count: 2  # ±2 zones
    area_ratio: 0.1  # ±0.1
    aspect_ratio: 0.2  # ±0.2
  
  # Fallback settings
  fallback_to_single_phase: true  # If no good match in top N
  min_coarse_score: 0.3  # Minimum coarse score to consider
```

---

## Related Documents

- **Current Implementation**: `apps/digidoc/ocr_service/tasks/matching_task.py`
- **Fingerprint Algorithm**: `apps/digidoc/ocr_service/matching/structural.py`
- **Template Search Logic**: `shared_documentation/architecture/TEMPLATE_SEARCH_LOGIC.md`
- **Architecture**: `shared_documentation/architecture/MASTER_ARCHITECTURE.md`

---

## Notes

- **Not Needed Yet**: Current template count is low (< 50), so optimization can wait
- **Future-Proofing**: Design should accommodate this enhancement
- **Performance Monitoring**: Track matching times to know when to implement
- **Alternative Approaches**: Could also consider:
  - Vector similarity search (e.g., using embeddings)
  - Machine learning-based matching
  - Caching frequently matched templates
  - Parallel processing for large template sets

