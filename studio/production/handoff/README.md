# P2 — Source to target handoff protocol

This module enforces source/target isolation and immutable GitHub commit identity for the approved Brandstudio 3.0 architecture. It is a **pure validator**, not an AI agent launcher, network client or attestations authority.

- Use the P1 TaskSpec and TaskReceipt for the original task, including its original `base_sha`; keep that original in all receipts.
- `prepare(task, source, target_executor=..., target_branch=..., receipt_ref=..., root=...)` requires a nonnull 40-character source `head_sha`, distinct allowed target executor and independent branch.
- Independently observe the actual source branch HEAD with connected GitHub/git, then pass `{"observed_from":"github-connector","branch":"...","head_sha":"..."}` to `verify(envelope,observation=...)`. A string claiming "observed_from" is **not** independent verification; the caller must preserve the tool output.
- In the receiving executor's own isolated host, create a **new** target branch from the exact observed source commit. `studio/work/ephemeral.py start --base publish/opencode-... --executor work` can do this in a real supported checkout.
- The P1 executor ID `chatgpt-work` maps to the existing ephemeral manager CLI `--executor work`. Do not modify P1 contract spelling to `work`, or treat a normal chat+GitHub connector as a Work host.
- Target receipt keeps original task `base_sha`, with its own branch/HEAD. The supplied target remote observation must separately attest source-head parent. `receive` returns `received` **only in the transport sense**; it does NOT prove real local OpenCode/Work sessions, actual HTML/browser render, human approval, or social publishing.
- At every error, fail closed; no auto costly retry, no model switching, no service credentials. Old Visual Editor and Cloudflare are unaffected. Historic KAIST V2 is untouched.
