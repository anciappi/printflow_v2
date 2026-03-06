# PrintFlow v2 — Project Rules

## Project Overview
PrintFlow v2 is a print shop management system.
Always read these rules before taking any action on this codebase.

## Tech Stack
- **Backend:** Python 3 / Django
- **Frontend:** Tailwind CSS + Django Templates
- **Database:** PostgreSQL
- **Auth:** Django Auth (native)
- **Environment:** secrets via `.env` file (never hardcode credentials)

## App Structure
| App | Responsibility |
|-----|---------------|
| `core` | Base config, global utilities |
| `customers` | Customer management |
| `dashboard` | Control panel and metrics |
| `inventory` | Materials and stock |
| `orders` | Work orders lifecycle |
| `products` | Product and service catalog |
| `purchasing` | Purchases and suppliers |
| `users` | Auth and user profiles |

## Current Priorities
1. **Clean and refactor** existing code (DRY, readability, consistency)
2. **Security hardening** (permissions, auth, input validation)
3. Tests and documentation come after the above

## Non-Negotiable Rules

### Security
- Every view MUST have `@login_required` or `LoginRequiredMixin`
- Always filter objects by user/permission, not just by PK
- Never interpolate variables into raw SQL strings
- Always use Django Forms to process user input — never raw `request.POST`
- `{% csrf_token %}` is required in every HTML `<form>`
- Never commit secrets, API keys or passwords — use `.env`

### Code Quality
- Follow DRY: if logic repeats 2+ times, extract it
- One responsibility per function/class (SOLID)
- All models must define `__str__`, `Meta` with `ordering`, and timestamp fields
- Use `select_related` / `prefetch_related` to avoid N+1 queries
- Use `get_object_or_404` in views — never bare `.get()`

### Naming Conventions
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- All code, variables, functions, comments and commits: **written in English**

### Git Commit Format
```
feat(scope): short description
fix(scope): short description
refactor(scope): short description
security(scope): short description
test(scope): short description
```

### Templates Structure
```
templates/
├── base.html
├── components/   ← reusable includes
└── <app_name>/   ← one folder per app
```

## Human Approval Required Before
- Any changes to models or migrations
- Any changes to authentication or permissions logic
- Any deletion of existing data or files
- Any dependency added to requirements.txt
