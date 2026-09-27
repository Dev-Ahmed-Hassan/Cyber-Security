# JWT (JSON Web Token) — Testing Checklist

> JWTs are used as bearer tokens for session/auth state. The core risk: if the server doesn't verify a JWT properly, an attacker can forge or modify the token's claims to impersonate other users or escalate privileges.

---

## 1. Basic Inspection

- [ ] Decode the JWT (header + payload) — no signature needed, it's just Base64. Use jwt.io or Burp's JWT decoder.
- [ ] Check the payload for interesting claims: `role`, `isAdmin`, `userId`, `email`, `scope`, etc.
- [ ] Check the header for `alg` and `kid` (key ID) fields.
- [ ] Check expiry claims (`exp`, `iat`, `nbf`) — are they present at all?

---

## 2. Signature Verification Bypass

- [ ] **`alg: none` attack** — change the header's `alg` to `none`, strip the signature entirely, keep payload modified. Some libraries historically accepted this.
- [ ] **Algorithm confusion (RS256 → HS256)** — if the server uses RS256 (asymmetric), try re-signing the token with HS256 using the **public key as the HMAC secret**. Some libraries don't check which algorithm was actually used to verify.
- [ ] Try simply modifying the payload (e.g., `"role":"user"` → `"role":"admin"`) and resending **without** re-signing — check if the server actually validates the signature at all before trusting claims.

---

## 3. Secret Key Attacks (for HS256/symmetric)

- [ ] Try common/weak secrets: `secret`, `123456`, app name, etc.
- [ ] Brute-force the signing secret offline with a wordlist (tools: `hashcat`, `jwt_tool`, `jwt-cracker`).
- [ ] Check if the secret is leaked anywhere client-side (JS bundle, config files, error messages, GitHub if it's a real target — not applicable here since source is off-limits).

---

## 4. Header Injection Attacks

- [ ] **`kid` (Key ID) manipulation** — if the server looks up the verification key using the `kid` value from the token header, try:
  - Path traversal in `kid` pointing to a predictable file (e.g., `/dev/null`) — if it resolves to an empty key, sign with an empty string as secret.
  - SQL injection in `kid` if it's used in a DB lookup.
- [ ] **`jku` (JWK Set URL) manipulation** — if present, check if you can point it to an attacker-controlled URL serving your own public key, then sign the token with your matching private key.
- [ ] **`jwk` (embedded JWK) injection** — some implementations accept a public key embedded directly in the header and trust it. Try adding your own `jwk` field with your key and self-signing.
- [ ] **`x5c` (certificate chain) manipulation** — similar idea, some libraries trust a self-signed cert embedded here.

---

## 5. Claim Tampering

- [ ] Modify `userId`/`sub` claim to another user's ID — does the server actually re-verify or just trust it?
- [ ] Modify `role`/`isAdmin`/`scope` claims — test for privilege escalation.
- [ ] Check if `exp` is enforced server-side (not just checked client-side) — try replaying an expired token directly against the API.
- [ ] Check if `aud` (audience) or `iss` (issuer) claims are validated, if present — cross-service token reuse can sometimes be forced.

---

## 6. Token Lifecycle

- [ ] Is there a token revocation mechanism? (i.e., does logging out actually invalidate the JWT, or is it still valid until natural expiry since JWTs are stateless by design?)
- [ ] Does changing the password invalidate previously issued tokens?
- [ ] Is there a refresh token flow? If so, apply the same claim-tampering/signature checks to it too.
- [ ] Check token storage location client-side (localStorage vs cookie) — affects XSS impact (localStorage tokens are readable by any injected script; cookie tokens can at least get `HttpOnly`).

---

## 7. Quick Testing Flow (in order)

1. Decode token → look at claims and header.
2. Try `alg:none`.
3. Try algorithm confusion if RS256 is used.
4. Try tampering claims without re-signing (checks if verification happens at all).
5. Try common/weak secret brute-force if HS256.
6. Check `kid`/`jku`/`jwk` header manipulation if present.
7. Check expiry/revocation behavior last.

---

**Tooling:** `jwt_tool` (Python) automates most of steps 2–6 and is worth learning — it's basically the sqlmap of JWT testing.
