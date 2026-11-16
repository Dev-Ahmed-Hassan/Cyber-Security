API TESTING & SECURITY
│
├── 1. API RECONNAISSANCE & DISCOVERY (Goal: Map endpoints, schemas, methods, formats, rate limits & auth)
│   │
│   ├── Authentication & Request Anatomy
│   │   ├── Input Schemas: Compulsory vs. optional parameters + expected media formats
│   │   └── Auth Workflows: Session cookies, API keys, Bearer tokens (JWT), OAuth headers
│   │
│   ├── Documented Endpoints (Human-readable consoles vs. Machine-readable JSON/YAML)
│   │   ├── Common Discovery Paths: /docs, /api, /api.json, /swagger, /swagger/index.html,
│   │   │                         /openapi.json, /swagger.json, /api-docs (e.g., exposed FastAPI Swagger UI)
│   │   ├── Base Path Traversal: /api/v1/users/123 ──► step back to /api/v1/users ──► /api/v1 ──► /api
│   │   └── Parsing & Audit Tooling
│   │       ├── Burp Scanner (auto-crawls & audits OpenAPI, JSON, YAML specs)
│   │       ├── OpenAPI Parser BApp (populates Burp site map from definitions)
│   │       └── Postman / SoapUI (imports schemas for rapid endpoint querying)
│   │
│   └── Web Routes vs. API Endpoints
│       ├── Web Route (GET /app/users) ──► Returns HTML shell + frontend JS bundles
│       ├── API Endpoint (GET /app/api/v1/users) ──► Async background fetch for raw JSON/XML from DB
│       └── JavaScript Analysis: Inspect .js bundles for hardcoded routes, params & hidden flags
│           └── Tool: JS Link Finder BApp (automates route extraction from bundled JS)
│
├── 2. INTERACTING & METHOD ENUMERATION (Tools: Burp Repeater & Intruder)
│   │
│   ├── HTTP Method Enumeration (Never assume only GET / POST; test PUT, PATCH, DELETE)
│   │   ├── OPTIONS Probing: Send OPTIONS /api/products/1/price ──► Inspect "Allow: GET, PATCH" header
│   │   └── Direct Verb Probing: Fuzz standard HTTP verbs via Intruder (target test/non-critical objects)
│   │
│   ├── Content-Type Switching (Exploits parser discrepancies across formats)
│   │   ├── Swap "Content-Type: application/json" ──► "application/xml" (e.g., safe JSON vs. vulnerable XML parser)
│   │   ├── Tool: Content Type Converter BApp (auto-converts payloads between formats)
│   │   └── Verbose Error Clues: {"error": "Only 'application/json' Content-Type is supported"}
│   │
│   └── High-Speed Fuzzing (Bypasses Burp Community throttling via ffuf + SecLists)
│       ├── Hidden Endpoints:
│       │   └── ffuf -w raft-medium-words.txt -u https://target.com/api/user/FUZZ -X POST -mc 200,401,403
│       └── Hidden JSON Parameters:
│           └── ffuf -w secret-keywords.txt -u https://target.com/api/checkout -X POST -d '{"FUZZ":"test"}' -fc 400 -t 50
│
├── 3. PARAMETER RECONNAISSANCE & MASS ASSIGNMENT (GET query strings & JSON bodies)
│   │
│   ├── Error-Based Parameter Discovery (Provoking strict backend schema validators)
│   │   ├── Send empty object {} or malformed values (e.g., PATCH /api/products/1/price with {})
│   │   └── Read error leak: {"error": "price parameter is missing"} ──► Exploit with {"price": 0}
│   │
│   └── Data Leakage via Method Mismatch (Mass Assignment)
│       ├── Root Cause: Unified DTOs / ORM models bind client input directly to internal DB objects
│       └── 3-Step Attack Pattern:
│           1. Read via GET /api/checkout ──► Leaks {"chosen_discount":{"percentage":0},"chosen_products":[]}
│           2. Compare normal POST ──► Client normally only sends "chosen_products"
│           3. Exploit via POST ──► Inject leaked field: {"chosen_discount":{"percentage":100}, ...}
│
├── 4. SERVER-SIDE PARAMETER POLLUTION (SSPP) (User input concatenated into internal backend calls)
│   │
│   ├── Query String Injection & Truncation (Frontend input ──► Internal query string)
│   │   ├── Normal Flow: POST /forgot-password (username=carlos) ──► internal/api/users?username=carlos&field=email
│   │   ├── Truncation (%23 ──► #):
│   │   │   └── username=carlos%23 ──► ...?username=carlos#&field=email ──► {"error": "Field not specified."}
│   │   └── Parameter Injection (%26 ──► &):
│   │       └── username=carlos%26field=reset_token ──► ...?username=carlos&field=reset_token ──► Leaks reset token
│   │
│   ├── REST Path Injection & Directory Traversal (Input placed into backend URL path)
│   │   ├── Normal Flow: GET /edit_profile.php?name=peter ──► Internal: GET /api/private/users/peter
│   │   └── Traversal (%2f..%2f): name=peter%2f..%2fadmin ──► Resolves to GET /api/private/users/admin
│   │
│   └── Structured Data Injection (JSON Injection via raw string concatenation)
│       ├── Vulnerable Code: "{\"name\":\"" + userInput + "\"}" (bypasses proper JSON serializer)
│       └── Input: peter","access_level":"administrator ──► {"name":"peter","access_level":"administrator"}
│
└── 5. DEFENSE & HARDENING CHECKLIST
    ├── [1] Enforce Authorization on Every Endpoint (AuthN != AuthZ; verify role/ownership per request)
    ├── [2] Strict Input Whitelisting / DTO Pattern (Bind only user-editable fields; reject unknown params)
    ├── [3] Avoid String Concatenation (Use parameterized HTTP clients & proper JSON/XML serializers)
    ├── [4] Context-Aware Encoding (URL-encode / sanitize inputs before forwarding to internal APIs)
    ├── [5] Generic Error Handling (Return generic 400 / 403; suppress schema & missing-field leaks)
    └──
