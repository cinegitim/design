# Brandstudio Cloudflare Access live check — 2026-11-03

**Cloudflare account:** Asya'da Eğitim (`info@asyadaegitim.com`). **Change authorization:** the user explicitly approved using the same four individual authorized email addresses as the existing signature-management Access application. This document intentionally does not publish that email list or any authentication material.

## Implemented settings — verified by Cloudflare API

- Created a **separate** self-hosted Access application named `Asya’da Eğitim · Brandstudio E-posta Girişi` for the full `studio.asyadaegitim.com` hostname.
- The policy `Brandstudio · Yalnızca dört yetkili e-posta` is `allow` with exactly four explicit **individual** addresses; the source was the current signature-management Access policy, confirmed equal to the separately authorized four-account allowlist. No wildcard domain, `everyone` or `login_method`-alone rule in the studio `allow` policy.
- Allowed IdP: the existing account's `onetimepin` (email verification code) provider. Application and policy token lifetimes: `720h` (30 days). **365-day Cloudflare Access sessions are not supported**; the pre-existing Brandstudio trusted-device cookie remains a separate application mechanism.
- The existing signature-management Access application and its `720h` policy were read back unchanged.
- **Narrow backup exception:** `studio.asyadaegitim.com/internal/backup` has a separate, more specific self-hosted Access app with a `bypass` rule. This does not remove the Worker-side **GitHub Actions OIDC JWT validation**: the Worker checks audience, issuer, repository, workflow ref, token expiry and RS256 signature before returning encrypted payload. An unauthenticated Chrome request returned **HTTP 401**, both before and after the Access change. **The scheduled authenticated backup workflow was not executed in this check.**
- A new isolated Chrome context opened `https://studio.asyadaegitim.com/` and was redirected to the Cloudflare Access login page with a required **Email** field and **Send login code** button.

## Still unverified / preserved

- Did **not** enter an approved person's mailbox or request a live OTP, so an authorized user's full login and subsequent older Brandstudio admin-password/trusted-device flow remain to be end-to-end tested.
- Did **not** test rejection with a real unauthorized email; policy was read back and checked, but no OTP delivery or deny-flow was attempted.
- Did **not** modify Cloudflare DNS, Worker code, Pages builds, Cloudflare account-level global Access session duration, or the existing signature application.
- Existing `brandstudio-pages-git.pages.dev` and `cinegitim.github.io/design` can still serve *public static source* independently. The protected `studio` front door does **not** make public GitHub files confidential. Do not add private briefs or unpublished confidential assets to public `docs/`.
- Do not protect the Pages static origin with an independent Access policy before migrating authenticated origin fetching: `brandstudio-edge` currently fetches public static assets from Pages without a service token, and protecting this origin now would break the studio.
- A proper retirement of the **second** password challenge is a separate future change after successfully testing the four email-code logins and rollback; Access here adds a secure external entry gate without reworking the current application.
- No style-family implementation, automated GitHub version checkpoint, or new social publishing automation was activated by this Access policy change.

## Acceptance / follow-up

Use a real authorized email to test OTP sign-in and access to the editor; verify one denied account and/or policy test; verify that `/internal/backup` continues to reject unsigned requests and that the next scheduled GitHub OIDC backup still succeeds. Review public alternate asset origins separately; preserve existing encrypted backups. The intended final policy must be **fail-closed** and limited to four people, with access/session revocation working independently of the one-year device recognition.
