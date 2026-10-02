## Cyber Security Archive

A public knowledge base and living proof-of-work tracking my hands-on journey through web application security, API testing, and reverse engineering. Designed as both personal documentation and a resource for fellow learners.

<br>

### Current Focus

- **PortSwigger Web Security Academy:** Primary focus right now. Systematically working through labs across vulnerability classes, with structured notes and writeups documenting exploit mechanics, methodology, and remediation strategies for each lab.
- **OWASP Juice Shop (Live-Target Practice):** Applying concepts learned in PortSwigger labs against a live, unguided target. This work emphasizes independent reconnaissance, hypothesis-driven testing, and adopting a professional documentation workflow (recon maps, structured reports, writeups) rather than following challenge solutions directly.
- **Notes & Concepts:** Core technical foundations, attack vectors, testing methodologies, and protocol behavior documented as they're encountered, independent of any single lab or platform.

<br>

### Future Roadmap

- Transitioning tactical research into active **Bug Bounty** hunting, building on methodology developed through PortSwigger and Juice Shop practice.
- Expanding practical documentation into reverse engineering, binary analysis, and lower-level system concepts.

<br>

### Repository Layout

- **`writeups/web-security/portswigger-academy/`** — Structured lab writeups and exploit breakdowns, organized by vulnerability category (authentication, API testing, etc.).
- **`writeups/reverse-engineering/`** — Crackme solutions and binary analysis writeups.
- **`target-practice/owasp-juice-shop/`** — Live-target practice against Juice Shop, organized into `recon/` (endpoint maps, feature maps, tech stack notes), `writeups/` (narrative writeups per vulnerability area), and `reports/` (formal report-style documentation).
- **`bug-bounty/`** — Early-stage bug bounty preparation: `methodology/` (testing checklists), `practice-reports/` (practice writeups in report format), and `public-report-studies/` (analysis of publicly disclosed bug bounty reports).
- **`notes/`** — Core conceptual breakdowns, pentesting methodology references, and platform-specific notes (e.g. PortSwigger Academy conceptual notes) independent of individual lab writeups.
- **`scripts/`** — Reusable tooling developed during testing (e.g. JS bundle endpoint extraction).

<br>

### Documentation Style

Each lab or target directory generally follows a consistent structure:
- `README.md` — overview and summary of the work
- `notes.md` — raw/working notes taken during testing
- `images/` — supporting screenshots
- `scripts/` and `words_list/` — any custom tooling or wordlists used, where applicable

This structure is intended to make each piece of work self-contained and easy to navigate independently of the rest of the repo.
