# Juice Shop Endpoint Map

## main.js endpoints
```
GET   /rest/user/authentication-details/
GET   /rest/user/change-password?current=&new=&repeat=     ← note: GET, not POST, and takes password in query string
POST  /rest/2fa/verify
GET   /rest/2fa/status
POST  /rest/2fa/setup
POST  /rest/2fa/disable
```

### Core & Account Management
/data-export
/dataerasure
/erasure-request
/file-upload
/application-configuration
/application-version

### Web3 / NFT Endpoints
/rest/web3
/nftUnlocked
/nftMintListen
/submitKey
/walletExploitAddress
/walletNFTVerify

### REST Features & Challenge Handlers
/rest/captcha
/rest/image-captcha/
/rest/chat
/rest/memories
/rest/country-mapping
/rest/track-order
/rest/wallet/balance
/rest/repeat-notification
/rest/continue-code
/rest/continue-code/apply/
/rest/continue-code-findIt
/rest/continue-code-findIt/apply/
/rest/continue-code-fixIt
/rest/continue-code-fixIt/apply/

### Backend Entities & Operations (/api/ & others)
/api/Addresss
/api/BasketItems
/api/Cards
/api/Complaints
/api/Deliverys
/api/Feedbacks
/api/Hints
/api/Recycles
/orders
/reviews

## Authentication Endpoints (current focus)

```
GET   /rest/user/login
POST  /rest/user/login                          → 401 then 200 (failed then successful login)
GET   /rest/user/whoami
GET   /rest/user/whoami?fields=email
GET   /rest/user/security-question?email=...     → tried with random@gmail.com, user1@gmail.com, user1
POST  /rest/user/reset-password                  → 401 then 200
GET   /rest/saveLoginIp
POST  /api/Users/                                 → registration, 201
POST  /api/SecurityAnswers/                        → 201
```

**Notable:** `/rest/user/security-question?email=user1` (no domain) returned 200 with the
same response shape as a full email. Worth checking if this endpoint leaks whether an
email/username exists — classic user enumeration.

---

## Backend API (Sequelize-style REST, `/api/`)

```
GET   /api/Challenges/
GET   /api/Challenges/?name=Score%20Board
GET   /api/Quantitys/
GET   /api/SecurityQuestions/
GET   /api/Users/
POST  /api/Users/                                 → 201 (registration)
GET   /api/Users/25                                → referenced but not requested (grey)
GET   /api/SecurityAnswers/
POST  /api/SecurityAnswers/                        → 201
GET   /api/SecurityAnswers/23                       → referenced but not requested
```

> `/api/Users/25` and `/api/SecurityAnswers/23` are IDs the app referenced but never
> directly requested — good candidates for later IDOR testing (out of scope for now).

## Other REST Endpoints (`/rest/`)

```
GET   /rest/admin/application-configuration
GET   /rest/admin/application-version
GET   /rest/languages
GET   /rest/products/search
GET   /rest/products/search?q=
GET   /rest/basket/6
GET   /rest/order-history
GET   /rest/deluxe-membership
```

> `/rest/admin/...` is worth a second look later — "admin" in a path any user can hit is
> a common access-control bug (out of scope for now).

## Profile / Account Pages

```
GET   /profile
POST  /profile                                     → 302 then a POST with 0-length response
GET   /profile/image/file
GET   /profile/image/url
POST  /profile/image/file
POST  /profile/image/url
```

## JS Files (map the app's logic — search for hidden routes)

```
/main.js
/polyfills.js
/scripts.js
/chunk-DAJ4olp_.js
/chunk-DBPdFzgj.js
/chunk-eYAgyLdn.js
/rolldown-runtime-BoHGiXSq.js
/vendor/beercss/beer.min.js
```

## Static Assets / Vendor CSS (low priority)

```
/styles.css
/vendor/beercss/beer.min.css
/vendor/material-icons/material-icons.css
/assets/public/css/roboto.css
/assets/public/css/userProfile.css
/vendor/fontsource-roboto/*.css
```

## Images / Icons / Fonts (safe to ignore)

```
/assets/public/images/JuiceShop_Logo.png
/assets/public/images/products/*.jpg|.png|.jpeg
/assets/public/images/uploads/default.svg
/assets/public/images/deluxe/blankBoxes.png
/media/*.woff, *.woff2
/media/*.svg (country flags, ~40 files)
```

## WebSocket / Polling Noise (ignore)

```
/socket.io/?EIO=4&transport=polling...  (repeated on each page load)
/socket.io/?EIO=4&transport=websocket...
```
