## What will I write here
I will just write Observations here in this one liner format 


### Stuff to Test Later
* There are 25 users before me already... their emails can be enumerated... or passwords as well

* interesting thing, that the items have a review section. This section displays reviews with reference to the email itself. and a very very simple recon showed me an admin email with a review. I can note down the valid accounts and enumerate their passwords this way i think. 

### Authentication Observations

* It has a password reset page, but in that page, it requires an email and a security question. The email is checked everytime a character is changed (!) t

* User has a property field in the profile page, called role... which is set to customer.

* one can set their username as well... 

* image url.. 

### Test plan

1. **Login (`POST /rest/user/login`)** — send to Repeater. Compare success vs failure
   response shape. Decode the token (Decoder / Inspector) and see what claims it carries.
   Try basic SQL injection in the email field (`' or 1=1--`).
2. **whoami** — call with no token, a tampered token, and a valid token. Does behavior or
   response differ?
3. **Registration (`POST /api/Users/`)** — check what fields the body accepts. Can you set
   `role` or `isAdmin` even though the UI doesn't expose it? (mass assignment)
4. **Security question flow** — this is the enumeration lead. Compare responses for an
   email that exists vs one that doesn't (status, shape, timing).
5. **Reset password** — once you have a security question, try resetting a password for
   an account that isn't yours.
6. **saveLoginIp** — check what it does and whether it requires auth.

