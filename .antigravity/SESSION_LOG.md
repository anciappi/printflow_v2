# Session Log - PrintFlow v2

## Session: 2026-03-06
**Tasks Completed:**
- Orientation and primary rules review.
- Security/Architectural audit of ALL apps: `core`, `users`, `orders`, `customers`, `inventory`, `products`, `purchasing`.
- Fixed hardcoded credentials in `core/settings.py`.
- Initialization of project tracking (`AUDIT_REPORT.md`, `SESSION_LOG.md`).

**Files Created/Modified:**
- `.antigravity/AUDIT_REPORT.md` (Modified)
- `.antigravity/SESSION_LOG.md` (Modified)
- `core/settings.py` (Modified)

**Next Pending Task:**
- Refactor models to include missing timestamps and Meta classes.
- Implement queryset scoping in views for all apps.
- Consolidation of `inventory` and `purchasing` logic to remove duplication.

**Blockers/Open Questions:**
- 🔴 CRITICAL: Missing timestamps and Meta classes across almost all models.
- 🔴 HIGH: Massive duplication between `inventory` and `purchasing` apps.
- 🔴 HIGH: Unscoped querysets across all apps allow unauthorized data access/modification.
- 🔴 MEDIUM: Performance bottlenecks due to Python-side sorting and on-the-fly dashboard annotations.
