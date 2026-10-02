# Authentication Reconnaissance: OWASP Juice Shop

## 1. Overview & Objective
The goal of this phase was to conduct systematic reconnaissance against the authentication mechanisms of OWASP Juice Shop. Rather than jumping directly into payload delivery or automated vulnerability scanners, the focus was on establishing baseline application behavior, mapping authentication workflows, and identifying hidden or unlinked endpoints within client-side assets.

---

## 2. Dynamic Workflow Mapping

The initial mapping was conducted using Burp Suite's embedded browser routed through the local HTTP proxy. All HTTP request/response history and target site tree structures were tracked across both unauthenticated and authenticated states.

![Burp Suite Browser and Site Map View](./images/1.png)

### Key Actions Performed:
* **Failure Cases:** Navigated to the login interface and submitted intentionally invalid credential pairs (non-existent emails, wrong passwords, malformed inputs) to capture baseline error codes and response structures.
* **Account Recovery:** Tested the "Forgot Password" workflow using both valid and invalid identifiers to evaluate whether the application reveals user existence (enumeration).
* **Legitimate Account Flow:** Registered a valid test account (`POST /api/Users/`), configured the security question (`POST /api/SecurityAnswers/`), and executed a successful login to capture valid session tokens and headers.
* **Post-Authentication Surface:** Navigated through user profile settings, security configurations, and password modification features while authenticated, logging all state transitions and session handling behaviors.

The intercepted routes and request behaviors were documented in [`endpoint_map.md`](../../../recon/endpoint_map.md), alongside notes in [`feature_map.md`](../../../recon/feature_map.md) and [`tech_stack.md`](../../../recon/tech_stack.md).

---

## 3. Static Client-Side Analysis

After establishing the dynamic baseline, static inspection was conducted on JavaScript bundles loaded by the browser (such as `main.js`, `polyfills.js`, and vendor files) to uncover endpoints, API routes, and hidden application logic not directly exposed through the UI.

### Custom Automation
To parse large minified bundles without relying on manual searches, a custom Python extraction utility—located at [`scripts/js_endpoints_crawler.py`](../../../../scripts/js_endpoints_crawler.py)—was developed. The script:
1. Accepts either a local file path or an application URL (automatically fetching remote assets).
2. Extracts API namespaces (`/rest/`, `/api/`) and Angular routing paths using regex rules tailored for ES6 template literals (backticks) and string concatenations.
3. Formats and organizes discovered endpoints into a structured report.

The output revealed multiple administrative, 2FA, and password management endpoints that were not visibly linked during standard browsing (such as `/rest/user/change-password`, `/rest/2fa/verify`, and `/rest/user/authentication-details/`). These additional routes were merged into [`endpoint_map.md`](../../../recon/endpoint_map.md).

### Noise Filtering & Triage
Auditing other included files highlighted the need to differentiate proprietary application logic from vendor and framework runtimes:
* Files like `polyfills.js` or `zone.js` handle asynchronous execution and browser compatibility, containing zero custom business logic.
* UI bundles like BeerCSS (`beer.min.js`) handle client-side rendering, styling tokens, and DOM manipulation rather than server data flow.

The rules and indicators used to triage these files have been documented in the testing methodology reference at [`js_file_testing_methodology.md`](../../../../../notes/web-security/pentesting_methodology/js_file_testing_methodology.md).

---

## 4. Observations & Next Steps

All non-blocking insights, unusual parameter conventions (such as credentials passed via `GET` query parameters), and potential user enumeration vectors were cataloged in [`parked_observations.md`](../../../recon/parked_observations.md). 

With the attack surface mapped and the baseline behavior established, the next phase will transition from passive reconnaissance to focused vulnerability assessments across the identified authentication workflows.

## 5. Email Address Enumeration via Product Reviews

During manual review of the product catalog, it was observed that user-submitted reviews display the reviewer's email address in the `author` field rather than a username or display name. This constitutes an information disclosure vulnerability, as it exposes valid account identifiers that can subsequently be leveraged for credential-stuffing or password-spraying attacks against the authentication endpoint.

Based on account ID sequencing (the test account created during registration was assigned ID 25, with the following registration receiving ID 26), it can be inferred that 24 accounts existed prior to the test account. This figure represents the upper bound of registered users at the time of testing, not necessarily the number of users who authored reviews.

### Methodology

Reviews are retrieved on a per-product basis via `GET /rest/products/{id}/reviews`, returning a JSON payload containing an array of review objects, each including an `author` field. With 46 products in the catalog, enumerating all reviews requires iterating across product IDs 1 through 46.

To avoid the overhead and fragility of regex-based extraction against raw response text, the JSON response was parsed directly using Python's `requests` library, indexing into the structured `data` field of each response. This approach is both more reliable and less error-prone than pattern matching, since the API returns well-formed JSON rather than embedding emails in unstructured HTML.

A custom script was written to iterate across all product IDs, extract the `author` field from each review, and deduplicate results into a single list of unique email addresses:

```python
import requests

base_URL = 'http://localhost:3000'
emails = []

def get_reviews(n):
	response = requests.get(f"{base_URL}/rest/products/{n}/reviews")
	return response


for i in range(1, 47):
	resp = get_reviews(i)
	data = resp.json()
	reviews = data['data']

	for review in reviews:
		if review['author'] not in emails:
			emails.append(review['author'])

print(f"[+] Total unique email addresses found: {len(emails)}")
print(emails)
```

### Results

The script returned 12 unique email addresses:

```text
[+] Total unique email addresses found: 12
['admin@juice-sh.op', 'basil@juice-sh.op', 'uvogin@juice-sh.op', 'bender@juice-sh.op', 'mc.safesearch@juice-sh.op', 'jim@juice-sh.op', 'morty@juice-sh.op', 'bjoern@owasp.org', 'stan@juice-sh.op', 'accountant@juice-sh.op', 'wurstbrot@juice-sh.op', 'J12934@juice-sh.op']
```

This figure is lower than the inferred total of 24 pre-existing accounts, which is expected: the review-based enumeration method only surfaces accounts belonging to users who have authored at least one product review, and therefore represents a subset of all valid accounts rather than an exhaustive list. Accounts that never left a review remain undiscovered through this vector and would require a separate enumeration technique (e.g., abusing the login or password-reset endpoints for user-existence signals).

### Next Steps

These 12 confirmed-valid email addresses will be used as a target list for password enumeration via `ffuf`, fuzzing against the login endpoint with a common password wordlist to identify weak or default credentials.

