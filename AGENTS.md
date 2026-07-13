# Inventory Command Center — Engineering Contract

## Product source of truth
Read `/opt/data/AI_Context/projects/inventory-analyst-learning-system-design.md` before changing code.

## Required stack
- Frontend: React, TypeScript, Vite, Tailwind CSS, Framer Motion, React Router, ECharts/Recharts.
- Backend: FastAPI, SQLAlchemy/SQLModel, SQLite, Pydantic.
- Testing: Vitest + React Testing Library, pytest, Playwright.
- Local-first; no paid APIs and no external authentication.

## Required application screens
1. Command Center
2. Learning Map
3. Mission Workspace
4. Simulation Room
5. Analytics Lab
6. Competency Matrix
7. Portfolio Vault
8. Rewards Center
9. Manager's Office

## Product requirements
- Every navigation item must open a functional screen, not a placeholder.
- Build a distinctive futuristic-industrial control-tower visual system.
- Include purposeful Framer Motion transitions and a lightweight CSS/SVG 3D warehouse/network scene. Spline must be optional because no scene URL is currently supplied.
- Include reduced-motion behavior and static fallback.
- Seed realistic Week 1 inventory lessons, missions, competencies, rewards, portfolio example, manager case, and inventory datasets.
- Provide API-backed progress, submissions, XP, streak, mission completion, competencies, rewards, and portfolio records.
- Responsive at mobile, tablet, and desktop sizes.
- Accessible keyboard navigation, visible focus, semantic labels, and sufficient contrast.
- No hardcoded secrets.

## Verification rules
- Use TDD for business logic and API behavior.
- Run frontend unit tests, backend tests, typecheck/lint, production build, and Playwright E2E.
- E2E must visit every required screen and exercise at least one key interaction per screen.
- Provide README commands for Raspberry Pi local startup.
- Do not claim completion unless all verification commands pass.
