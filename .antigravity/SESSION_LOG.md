# Session Log - PrintFlow v2

## Session: 2026-03-06
**Tasks Completed:**
- Orientation and primary rules review.
- Security/Architectural audit of `core/` and `users/` apps.
- Fixed hardcoded credentials in `core/settings.py`.
- Security/Architectural audit of `orders/` and `customers/` apps.
- Initialization of project tracking (`AUDIT_REPORT.md`, `SESSION_LOG.md`).

**Files Created/Modified:**
- `.antigravity/AUDIT_REPORT.md` (Modified)
- `.antigravity/SESSION_LOG.md` (Modified)
- `core/settings.py` (Modified)

**Next Pending Task:**
- Audit: `inventory/`, `products/`, `purchasing/`.

**Blockers/Open Questions:**
- 🔴 CRITICAL: User and Customer models require timestamps as per project rules.
- 🔴 HIGH: Unscoped querysets in `orders/` and `customers/` views allow unauthorized data access/modification.
- 🔴 HIGH: `CustomerDeleteView` allows permanent deletion, violating data retention rules.
- 🔴 MEDIUM: Race condition vulnerability in `WorkOrder.ot_number` generation.
