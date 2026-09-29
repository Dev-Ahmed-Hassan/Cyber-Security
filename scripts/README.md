# Custom Recon & Testing Utilities

This directory contains standalone automation scripts developed during assessment and testing phases.

---

### [js_endpoints_crawler.py](./js_endpoints_crawler.py)
Automates static string and route extraction from minified client-side JavaScript bundles (supports both local files and remote URLs).

* **Purpose:** Uncovers unlinked API routes, Angular client-side paths, and sensitive key patterns without manually parsing minified code. Handles modern ES6 template literals (backticks) and split URL base concatenations.
* **Requirements:** Python 3.8+ (standard library only, no external dependencies).
* **Output:** Generates a structured summary and categorized route report in `js_endpoints_crawler.txt`.

#### Usage

```bash
# Analyze a remote bundle (downloads automatically to the current directory)
python js_endpoints_crawler.py http://localhost:3000/main.js

# Analyze a local file
python js_endpoints_crawler.py ./main.js
