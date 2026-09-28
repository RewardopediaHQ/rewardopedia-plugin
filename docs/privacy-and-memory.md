# Privacy, memory, retention and deletion

Status: pre-release. This describes how the Rewardopedia MCP service is designed
to handle your data for version 0.1.0. The service is not yet live, and the
measured values marked "to be published" will be added before release.

Read this before you connect an assistant to Rewardopedia.

## What Rewardopedia can see

Rewardopedia only receives what your assistant sends in a tool call, plus the
identity of the Rewardopedia account you signed in with. It does not receive
your whole conversation. Your assistant provider (for example ChatGPT, Claude,
Grok or Perplexity) keeps your conversation under its own privacy terms.

## What is saved to your account

| Saved item | Examples | Created by |
| --- | --- | --- |
| Cards you hold | "I have the Example Travel Card" | Only an explicit statement saved with `update_my_context` |
| Spending and goals | "Dining is my priority" | Explicit disclosures |
| Preferences and constraints | "No annual fee above $95", "no foreign transaction fee" | Explicit disclosures |
| Temporary plans | "Trip abroad next month" | Explicit disclosures; they stop influencing results when they expire |
| Provenance | Which request saved a fact, when, and what it replaced | Every saved change |
| Sanitized request history | Tool name, sanitized inputs, outcome, context version, recommendation references | Every authenticated, validated tool call, including ones that fail for business reasons |

Searching for or comparing a card records interest only. It never records that
you hold the card. Hypothetical questions are not saved as facts.

Saved context belongs to your Rewardopedia account, not to one assistant. If
you connect two assistants with the same account, both use the same context.
Different Rewardopedia accounts never see each other's context.

## What you should never share

Do not share card numbers, security codes, bank or card account numbers,
government identifiers, passwords, one-time codes or any other credential.
Free-text notes are limited to 4,096 characters, and recognised credential,
payment-identifier and URL patterns are removed before anything is stored.
Automatic filtering cannot recognise every secret, so do not rely on it.
Free text is never treated as a fact or an instruction.

## How long it is kept

Saved context and sanitized request history are kept until you delete them or
delete your Rewardopedia account. Operational logs record request identifiers,
outcome codes, status and timing, not your inputs or credentials.

## Inspecting and deleting

- **Inspect:** ask your assistant what Rewardopedia remembers
  (`get_my_context`). You see current facts, their provenance and your request
  history.
- **Correct:** tell your assistant the correct fact. The new statement
  supersedes the old one (`update_my_context`).
- **Delete some or all:** ask your assistant to forget specific facts or
  everything (`forget_my_context`). Deleting also removes the stored inputs,
  provenance and recommendation results that could reconstruct what you
  deleted, and blocks earlier retried requests from saving it again. Repeating
  a deletion is safe.
- **Delete your account:** deleting your Rewardopedia account (instructions to
  be published before release) erases your saved context, history and stored
  identity. Only a one-way hashed marker of the deleted sign-in identity is
  kept, so that identity cannot be used again to write to the deleted account.

## Backups

Deletion takes effect in the live service. Copies inside service backups are
not removed immediately. The maximum backup retention period and how restores
honour deletions are to be published here before release; until then, assume
deleted data can remain in backups for a period that has not yet been measured.

## Permissions you grant

| Permission | Lets the assistant |
| --- | --- |
| `cards:read` | Look up, search and compare published card facts |
| `context:read` | Read your saved context and history, and use it for recommendations |
| `context:write` | Save, correct and delete your context |

You can revoke access at any time by disconnecting Rewardopedia in your
assistant's settings.
