## OWASP Juice Shop

Live-target practice against OWASP Juice Shop, treating it as an unguided application rather than working through its built-in challenge list directly. The focus is on building independent testing methodology: mapping the attack surface, forming hypotheses per endpoint, and documenting findings in a professional, report-style format.

<br>

### Structure

- **`recon/`** — Baseline reconnaissance of the application: `endpoint_map.md` (catalogued API/application routes), `feature_map.md` (application functionality by area), `tech_stack.md` (identified technologies), and `parked_observations.md` (noted anomalies or leads not yet investigated).
- **`writeups/`** — Hypothesis-driven testing narratives, organized by vulnerability category (e.g. `authentication/`). A writeup documents the process of testing for a specific vulnerability class, regardless of outcome — the vulnerability tested for may or may not turn out to exist. Each writeup folder typically contains a `notes.md` (working notes) alongside the formal writeup, plus `images/` where relevant.
- **`reports/`** — Professional, bug-bounty-style reports for confirmed vulnerabilities only, organized the same way as `writeups/` by vulnerability category. `template.md` defines the standard report structure used across all reports in this directory.
