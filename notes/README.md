## Notes

This directory holds conceptual material and testing methodology that exists independently of any single lab or target — the underlying knowledge built up while working through PortSwigger Academy and live-target practice, organized by vulnerability class rather than by where it was learned.

It serves two distinct purposes:

<br>

### 1. Testing Methodology (`web-security/pentesting_methodology/`)

Practical, checklist-style references for testing an application — the specific things to check for a given vulnerability class when assessing a target (e.g. `auth_testing_methodology.md`, `api_testing_methodology.md`, `js_file_testing_methodology.md`). These are built for direct use during testing, not just as background reading: a condensed list of what to look for and how, distilled from labs and hands-on experience rather than theory alone.

### 2. Conceptual Notes (`web-security/portswigger-academy/`)

Background material and explanations for concepts encountered while working through PortSwigger Academy, organized by topic (e.g. `authentication/`, `api_testing/`). These capture the "why" and "how it works" behind a vulnerability class — distinct from the lab writeups themselves (which live under `writeups/web-security/portswigger-academy/`), and serve as a standing reference independent of any specific lab.

<br>

### Additional Files

- **`learning-log.md`** — A running log tracking progress and learning over time.

<br>

The distinction between the two: **methodology** answers "what to check and how to check it," while **conceptual notes** answer "what the vulnerability is and why it happens." Lab-specific or target-specific writeups — the actual exploitation walkthroughs — live outside this directory, under `writeups/` and `target-practice/`.
