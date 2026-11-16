AUTHENTICATION VULNERABILITIES (MASTER MIND MAP)
│
├── 1. PASSWORD-BASED LOGIN (Core: username + secret password = proof of identity)
│   │
│   ├── Brute-Force & Credential Guessing (Logic & human patterns > pure randomness)
│   │   ├── Username Guessing
│   │   │   ├── Predictable defaults: admin, administrator, support / IT accounts
│   │   │   ├── Corporate formats: firstname.lastname@company.com
│   │   │   └── Recon sources: public profiles, emails leaked in HTTP responses
│   │   └── Password Guessing (Rule-evasion habits)
│   │       └── Mutations: password ──► Password1! ──► Mypassword1! ──► Mypassword2!
│   │
│   ├── Username Enumeration (App behavior leaks whether a username exists)
│   │   ├── HTTP status codes
│   │   ├── Error messages ("Invalid username" vs. "Incorrect password")
│   │   ├── Response length differences
│   │   ├── Response timing (Valid user = slower due to password check; Invalid = faster)
│   │   │   └── Pro Tip: Send an extra-long password to amplify timing differences
│   │   ├── Account lock behavior differences
│   │   └── Registration page messages
│   │
│   ├── Flawed Brute-Force Protections
│   │   ├── Account Locking Flaws
│   │   │   ├── Different lock messages leak valid usernames
│   │   │   └── Bypassed via Credential Stuffing / Spraying (many usernames + few passwords = never hits lock limit)
│   │   └── IP Rate-Limiting Flaws
│   │       ├── Trusts attacker-controlled IP headers (e.g., X-Forwarded-For)
│   │       └── Allows multiple credential guesses inside a single request
│   │
│   └── HTTP Basic Authentication [Header: Authorization: Basic base64(username:password)]
│       ├── Credentials transmitted repeatedly on every single request
│       ├── Often lacks brute-force / rate-limit protection
│       ├── Static token value (no rotation)
│       ├── No built-in CSRF protection
│       └── Exposed credentials risk cross-site reuse
│
├── 2. MULTIFACTOR AUTHENTICATION (2FA / MFA)
│   │
│   ├── Core Principle & Factor Independence
│   │   ├── Combines: [Something you know (Password)] + [Something you have (Temp Code/Device)]
│   │   ├── Factors MUST be genuinely separate channels (Out-of-band device)
│   │   └── Weak Factor Warning: Email OTP = 1FA with extra steps if email creds are compromised
│   │
│   ├── Token Generation Security
│   │   ├── Strong (Generated locally on device — never crosses network)
│   │   │   └── RSA tokens, hardware keypads/tokens, Authenticator apps (Google Authenticator)
│   │   └── Weak (Transmitted over network/carrier)
│   │       └── SMS tokens ──► Vulnerable to interception & SIM swapping
│   │
│   └── Implementation Flaws (Visual 2FA != Logical Enforcement)
│       ├── Bypassing 2FA by Skipping Step 2
│       │   ├── Cause: Server creates valid session immediately after password step
│       │   └── Attack: Submit valid password ──► Hit 2FA page ──► Browse directly to /my-account
│       ├── Broken 2FA Logic (Client-Side State Trust)
│       │   ├── Cause: Server relies on user-controlled cookies (user=username or verify=username)
│       │   └── Attack: Log in as wiener ──► Change cookie to verify=carlos ──► Brute-force Carlos's OTP
│       └── Flawed 2FA Brute-Force Protection
│           ├── Cause: Logging user out after N failed OTP attempts resets the counter on re-login
│           └── Attack: Automate full loop (Login ──► 2FA ──► N guesses ──► Logout ──► Re-login ──► Repeat)
│
├── 3. SESSION & "REMEMBER-ME" COOKIES (Overlooked Secondary Auth Mechanisms)
│   │
│   ├── Predictable Cookie Constructions
│   │   ├── username:timestamp
│   │   ├── username:password
│   │   ├── base64(username:password)
│   │   └── username:md5(password)
│   │
│   ├── Encoding vs. Encryption vs. Hashing Mistakes
│   │   ├── Base64 is ENCODING, not encryption (instantly reversible)
│   │   └── Unsalted hashes (e.g., raw MD5) ──► Vulnerable to wordlist hashing & public hash lookup DBs
│   │
│   └── Exploiting & Analyzing Cookies
│       ├── Missing Rate Limits: Brute-forcing cookie values bypasses login form rate limits
│       └── Studying Cookie Patterns
│           ├── Register own account ──► Capture cookie ──► Decode & spot pattern ──► Forge victim cookie
│           ├── Steal sample cookie via XSS (when registration is closed)
│           └── Read open-source codebase for cookie generation logic
│
└── 4. PASSWORD RESET & PASSWORD CHANGE FLOWS
    │
    ├── Email Delivery Security
    │   └── NEVER send plaintext passwords via email
    │       ├── Why: Stays in inbox indefinitely, syncs across devices, exposed on networks/compromised email
    │       └── Fix: Send short-lived OTP or high-entropy reset link
    │
    ├── Reset URL & Token Design
    │   ├── Vulnerable: Predictable/tamperable IDs (/reset-password?user=username)
    │   └── Secure: High-entropy, unguessable token (/reset-password?token=a0ba0d1c...)
    │       ├── Token-to-user mapping stored strictly server-side
    │       └── Backend checks: (1) Exists? (2) Matches user? (3) Not expired? (4) Unused? ──► Destroy immediately
    │
    ├── Broken Password Reset Logic (Step Validation Mismatch)
    │   ├── Cause: Server validates token on GET (loading form) but NOT on POST (saving new password)
    │   └── Attack: Get valid token for self ──► Open form ──► Remove token / change username=victim in POST
    │
    ├── Password Reset Poisoning (Host Header Injection)
    │   ├── Cause: App builds reset link from untrusted request header ({Host Header}/reset-password?token=...)
    │   └── Attack Flow:
    │       1. Request password reset for victim with modified "Host: attacker.com"
    │       2. Victim receives email with poisoned link & clicks it
    │       3. Victim's browser sends reset token to attacker's server logs
    │       4. Attacker replays stolen token on real site ──► Account Takeover
    │
    └── Password Change Functionality Flaws (Often neglected vs. reset)
        ├── Fails to verify current password
        ├── Leaks distinct responses for valid vs. invalid current password
        ├── Allows brute-forcing current password (missing rate limits)
        └── Trusts user-controlled parameter (username / user_id) to decide whose password changes

        
CROSS-TOPIC CONNECTIONS & CHAINING PATHS
│
├── Chain 1: Recon ──► Credential Attack ──► 2FA Bypass
│   └── Enumerate valid usernames (Timing/Errors) ──► Password Spray (evades lockout) ──► Skip 2FA or swap verify= cookie
│
├── Chain 2: Client-Side Bug ──► Weak Cookie Crypto ──► Account Takeover
│   └── Exploit XSS to steal Remember-Me cookie ──► Decode Base64 / crack unsalted MD5 ──► Forge admin cookie
│
├── Chain 3: Reset Poisoning ──► Full Auth Bypass
│   └── Poison Host header in Forgot Password ──► Steal victim's reset token ──► Reset password (bypasses login & often 2FA)
│
└── QUICK TESTING CHECKLIST (Every Auth Audit)
    ├── [1] Compare valid vs. invalid username responses (status code, length, error text, timing)
    ├── [2] Probe account lockout thresholds & test password spraying across many users
    ├── [3] Test rate-limit bypasses (IP headers, multi-guess requests, re-login loops on 2FA, cookie guessing)
    ├── [4] Hunt predictable usernames, exposed emails, & Authorization: Basic headers
    ├── [5] Test 2FA step-skipping (/my-account) & cookie tampering (verify=victim)
    ├── [6] Decode/analyze Remember-Me cookies for Base64, timestamps, or unsalted hashes
    ├── [7] Test Password Reset POST requests with missing tokens or altered username parameters
    ├── [8] Inject arbitrary Host headers on Password Reset requests to check for link poisoning
    └── [9] Audit Password Change endpoints for missing current-password checks & IDOR parameters
