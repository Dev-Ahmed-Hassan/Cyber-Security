# API Testing & Security Guide

---

## 1. API Reconnaissance & Discovery

To test an API effectively, you must identify its endpoints and understand how to construct valid HTTP requests. This requires discovering input schemas (compulsory and optional parameters), supported HTTP methods, media formats, rate limits, and authentication workflows (session cookies, API keys, Bearer tokens, or OAuth headers).

### Documented Endpoints
APIs often provide human-readable (interactive consoles) or machine-readable (JSON/YAML) definitions. Frameworks such as FastAPI can automatically generate interactive documentation (Swagger UI) that may remain exposed in production.
*   **Discovery Paths:** Probe common documentation paths, such as `/docs`, `/api`, `/api.json`, `/swagger`, `/swagger/index.html`, `/openapi.json`, `/swagger.json`, or `/api-docs`.
*   **Base Path Traversal:** When a resource endpoint like `/api/v1/users/123` is found, step back through parent directories (`/api/v1/users`, `/api/v1`, `/api`) to find documentation indices or parent routing definitions.
*   **Tooling:**
    *   *Burp Scanner:* Automatically crawls and audits OpenAPI, JSON, or YAML specs.
    *   *OpenAPI Parser BApp:* Parses OpenAPI definitions to populate the site map.
    *   *Postman / SoapUI:* Imports documentation schemas directly for rapid endpoint querying.

### Web Routes vs. API Endpoints
Web application routes and backend API endpoints serve distinct purposes and have different attack surfaces:
*   **Web Route:** Visiting `GET /app/users` in a browser returns an HTML shell and frontend JavaScript bundles.
*   **API Endpoint:** The loaded JavaScript asynchronously makes a background request (e.g., `GET /app/api/v1/users`) to retrieve raw JSON or XML data from the database.
*   **JavaScript Analysis:** Inspect client-side scripts for hardcoded backend endpoints, parameters, or hidden flags that are not triggered directly via the visible UI. Use extensions like the **JS Link Finder BApp** to automate route extraction from bundled `.js` assets.

---

## 2. Interacting & Method Enumeration

Once endpoints are identified, interaction begins by probing accepted methods, content types, and error behaviors using Burp Repeater or Intruder.

### HTTP Method Enumeration
Never assume an endpoint only supports `GET` or `POST`. Check for alternate state-changing methods (`PUT`, `PATCH`, `DELETE`):
*   **Probing via OPTIONS:** Send an `OPTIONS` request to inspect the `Allow` header.
    ```http
    OPTIONS /api/products/1/price HTTP/1.1
    Host: target.com
    ```
    *Response indicating unused attack surface:*
    ```http
    HTTP/1.1 200 OK
    Allow: GET, PATCH
    ```
*   **Probing Verbs Directly:** If `OPTIONS` is disabled or ambiguous, test alternative methods manually or use Burp Intruder loaded with standard HTTP verbs. Target non-critical or test objects to prevent unintended data loss.

### Content-Type Switching
APIs often handle different data serialization formats using separate backend parsers. An endpoint secure against JSON injection might use a vulnerable XML library when parsing XML payloads:
*   Modify the `Content-Type` header (e.g., changing `application/json` to `application/xml`).
*   Convert payloads automatically using Burp extensions like **Content Type Converter BApp**.
*   Verbose server responses can leak parser expectations:
    ```json
    {"error": "Only 'application/json' Content-Type is supported"}
    ```

### High-Speed Endpoint & Parameter Fuzzing
Burp Suite Community Edition throttles Intruder requests. For high-speed directory, endpoint, and parameter discovery, use **ffuf** (Fuzz Faster U Fool) alongside **SecLists**.

*   **Fuzzing Hidden Endpoints:**
    ```bash
    ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
         -u [https://target.com/api/user/FUZZ](https://target.com/api/user/FUZZ) \
         -X POST -H "Cookie: session=YOUR_SESSION" -mc 200,401,403
    ```
*   **Fuzzing Hidden JSON Parameters:**
    ```bash
    ffuf -w /usr/share/seclists/Discovery/Variables/secret-keywords.txt \
         -u [https://target.com/api/checkout](https://target.com/api/checkout) \
         -X POST \
         -H "Content-Type: application/json" \
         -H "Cookie: session=YOUR_SESSION" \
         -d '{"FUZZ": "test"}' \
         -fc 400 -t 50
    ```

---

## 3. Parameter Reconnaissance & Mass Assignment

Hidden parameters can exist on both GET query strings (e.g., `?id=1023&isAdmin=1`) and JSON request bodies. 

### Error-Based Parameter Discovery
Send an empty JSON object (`{}`) or malformed field values to provoke informative errors from strict backend schema validators:
*   *Request:* `PATCH /api/products/1/price` with body `{}`
*   *Response:* `{"error": "price parameter is missing"}`
*   *Exploitation:* Add the requested parameter: `{"price": 0}`.

### Data Leakage via Method Mismatch (Mass Assignment Recon)
Frameworks often use unified Data Transfer Objects (DTOs) or ORM models for both reading and writing database records. A `GET` request on an endpoint may expose parameters that can be supplied in a `POST`, `PUT`, or `PATCH` request.

*   **Step 1:** Observe read response structure via `GET /api/checkout`:
    ```json
    {
      "chosen_discount": {"percentage": 0},
      "chosen_products": []
    }
    ```
*   **Step 2:** Standard checkout requests only submit products:
    ```json
    {
      "chosen_products": [{"product_id": "1", "quantity": 1}]
    }
    ```
*   **Step 3:** Exploit mass assignment by binding the leaked internal property directly into the state-changing request:
    ```json
    {
      "chosen_discount": {"percentage": 100},
      "chosen_products": [{"product_id": "1", "quantity": 1}]
    }
    ```

---

## 4. Server-Side Parameter Pollution (SSPP)

SSPP occurs when user-supplied input is directly embedded or concatenated into backend API requests without proper sanitization, escaping, or encoding.

### Query String Injection & Truncation
When a frontend request takes a single value and communicates with an internal backend API over query strings:

*   **Internal Backend Architecture:**
    *   *Frontend Request:* `POST /forgot-password` with body `username=carlos`
    *   *Internal API Query:* `https://internal.backend/api/users?username=carlos&field=email`
*   **Truncation Testing:** Inject a URL-encoded hash (`%23` -> `#`) to cut off the rest of the internal backend query string:
    ```http
    username=carlos%23
    ```
    *Resulting Internal Query:* `https://internal.backend/api/users?username=carlos#&field=email`  
    *Server Reaction:* The server drops `field=email` and returns: `{"error": "Field not specified."}`. This confirms query concatenation.
*   **Parameter Injection:** Inject a URL-encoded ampersand (`%26` -> `&`) to inject new parameters into the server-side call:
    ```http
    username=carlos%26field=reset_token
    ```
    *Resulting Internal Query:* `https://internal.backend/api/users?username=carlos&field=reset_token`  
    *Exploitation:* If the backend accepts the injected `field`, it leaks sensitive attributes (such as password reset tokens) directly into the client-facing HTTP response.

### REST Path Injection & Directory Traversal
When parameters are translated into backend URL paths rather than query strings:
*   *Frontend Query:* `GET /edit_profile.php?name=peter`
*   *Internal Backend Request:* `GET /api/private/users/peter`
*   *Traversal Injection:* Supply URL-encoded path traversal sequences:
    ```http
    GET /edit_profile.php?name=peter%2f..%2fadmin
    ```
    *Resulting Internal Request:* `GET /api/private/users/peter/../admin` -> resolves to `GET /api/private/users/admin`.

### Structured Data Injection (JSON Injection)
Occurs when user input is concatenated directly into a raw server-side JSON payload without passing through a serializer.

*   *Vulnerable Backend Pattern:*
    ```text
    // Backend string concatenation:
    String jsonPayload = "{\"name\":\"" + userInput + "\"}";
    sendToInternalApi(jsonPayload);
    ```
*   *Attacker Input:*
    ```text
    peter","access_level":"administrator
    ```
*   *Resulting Internal Payload:*
    ```json
    {"name":"peter","access_level":"administrator"}
    ```
    The backend JSON parser interprets the injected quotation marks and colons as structural boundaries rather than literal string characters, escalating privileges.

---

## 5. Defense & Hardening Checklist

- [ ] **Enforce Authorization on Every Endpoint:** Authenticating a session is insufficient; verify that the authenticated caller has the explicit role and permission to manipulate the requested resource.
- [ ] **Strict Input Whitelisting (DTO Pattern):** Bind incoming requests exclusively to strongly typed Data Transfer Objects that contain only user-editable fields. Reject unrecognized parameters.
- [ ] **Avoid String Concatenation:** Never concatenate user input to form URL paths, query strings, or JSON/XML payloads. Use parameterized HTTP clients and robust JSON/XML serializers.
- [ ] **Context-Aware Encoding:** Properly URL-encode or format input before forwarding it to backend internal APIs.
- [ ] **Generic Error Handling:** Suppress detailed internal exception messages, schema requirements, or missing parameter alerts in production. Return generic `400 Bad Request` or `403 Forbidden` statuses.
- [ ] **Restrict Documentation & Endpoints:** Protect Swagger UI and machine-readable API schemas (`/docs`, `/openapi.json`) behind authenticated gateways or omit them entirely from production environments.
