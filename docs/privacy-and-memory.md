# Privacy, memory, retention and deletion

Status: pre-release. This describes how the Rewardopedia MCP service is designed
to handle your data for version 0.1.0. The service is not yet live.

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
| Sanitized request history | Tool name, sanitized inputs, outcome, context version, and for recommendations the saved facts that were used | Every authenticated, validated tool call except a deletion, including ones that fail for business reasons |

Facts are saved when you state them explicitly. Rewardopedia's instructions tell
your assistant to explain what is saved before its first Rewardopedia request
in a conversation, and not to save anything you ask it not to. The request
history is different: it is recorded automatically for every Rewardopedia tool
request except a deletion, including card searches and comparisons, even if you
never save a fact. If a request cannot be recorded, it returns an error instead
of a result.

What the history keeps depends on the request:

- **Card searches and lookups:** the search text, with long numbers,
  credentials and links redacted, plus the filters or card identifiers asked
  about and the outcome.
- **Recommendations:** the highest-priority goal, the language and market, the
  saved facts that determined the answer, and the outcome. The cards you
  listed, your constraints and the recommended cards are not kept.
- **Saving and correcting facts:** the change that was made.

Searching for or comparing a card records interest only. It never records that
you hold the card. Hypothetical questions are not saved as facts.

Saved context belongs to your Rewardopedia account, not to one assistant. If
you connect two assistants with the same account, both use the same context.
Different Rewardopedia accounts never see each other's context.

## What you should never share

Do not share card numbers, security codes, bank or card account numbers,
government identifiers, passwords, one-time codes or any other credential.
Saved facts are structured entries, not free-form notes, and values that look
like card numbers, account numbers or credentials are refused. Search text
kept in history has recognised credential, payment-identifier and URL patterns
removed first. Automatic filtering cannot recognise every secret, so do not
rely on it. Search text is never treated as a fact or an instruction.

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
- **Delete some or all:** ask your assistant to forget specific facts,
  specific requests, or everything (`forget_my_context`). Deleting a request
  also deletes the facts it saved. Deleting a fact also deletes every history
  entry recorded while that fact existed, so some later, unrelated requests can
  be deleted with it, and clears search text from your remaining history.
  Deleted requests can never be replayed to save the information again.
  Repeating a deletion is safe.
- **Delete your account:** deleting your Rewardopedia account erases your saved
  context, history and stored identity. Only a one-way hashed marker of the
  deleted sign-in identity is kept, so that identity cannot be used again to
  write to the deleted account. To delete your account entirely, email
  info@rewardopedia.com.

## Backups

Deletion from Rewardopedia is immediate; provider backup copies roll off
automatically within about 8 days (backups are kept for 7 days; measured in
October 2026 and re-measured whenever backup settings change). For retention
questions or to delete your Rewardopedia account entirely,
email info@rewardopedia.com.

## Permissions you grant

| Permission | Lets the assistant |
| --- | --- |
| `cards:read` | Look up, search and compare published card facts, and ask for recommendations |
| `context:read` | Read your saved context and history, and use saved facts in recommendations |
| `context:write` | Save, correct and delete your context |

Recommendations never save or change your facts; only an explicit save does.

You can revoke access at any time by disconnecting Rewardopedia in your
assistant's settings.
