# Rewardopedia MCP tools

Status: pre-release. The server at `https://mcp.rewardopedia.com/mcp` is not yet
live. This page describes the intended behaviour of the eleven tools for
version 0.1.0. When the server is live, the tool descriptions, input/output
schemas and annotations it advertises are authoritative; if they disagree with
this page, follow the server and report the difference as a documentation bug.

## Shared rules

- **Identity.** The signed-in Rewardopedia account is determined from the OAuth
  connection. No tool accepts an account, user or customer identifier.
- **Locale and market.** Supported pairs are exactly `en-US`/`US` and
  `es-US`/`US`. Other pairs are refused; there is no fallback to another
  language or market.
- **Qualification.** Card results come only from cards currently published and
  qualified for the requested pair. Catalog presence alone is not enough.
- **Unknown values.** Absent facts are returned as unknown, never as zero,
  `false` or "none".
- **Bounded output.** Lists are paginated or capped. A short list is not proof
  that no other cards exist.
- **Request history.** Authenticated, validated business calls are recorded in
  the account's sanitized request history (operation, sanitized inputs,
  outcome, context version and recommendation references). Card lookups record
  interest only; they never create ownership facts. Protocol and health
  traffic is not history. See [the privacy guide](../../../docs/privacy-and-memory.md).
- **Quotas.** Standard accounts are limited per account across all connected
  clients: 100 requests per minute and 1,000 per hour.
- **Errors.** Missing or expired sign-in and missing permissions return
  authorization errors that ask the client to re-authorize. Quota exhaustion,
  unavailable card data and unavailable saved-context storage return distinct
  errors. A failed call never reports a saved change as successful.

## Permissions

| Permission | Allows |
| --- | --- |
| `cards:read` | The seven card tools and card, issuer and category resources |
| `context:read` | `get_my_context` and recommendations that read saved context |
| `context:write` | Saving, correcting and deleting context, and recommendations that include context updates |

A call that includes context updates without `context:write` is rejected; the
updates are never silently dropped.

## Card tools (`cards:read`)

### `search_cards`

Find cards by free text, issuer, canonical category, ranking and pagination.
Results are search results, not recommendations, and do not rank cards for the
user. Use the returned identifiers with the other card tools.

### `get_card_detail`

Return one card's published projection for the requested pair: benefits,
typed earning rates and their conditions, fee semantics, offers when
available, source references and publication identity. Unknown fields stay
unknown.

### `compare_cards`

Return two or more cards side by side in the order requested. Aliases for the
same product are de-duplicated, and any card that cannot be returned is listed
as explicitly unavailable; a missing card never implies the comparison is
complete. The result has no overall winner: present trade-offs, keep
conditions attached, and do not treat different reward currencies as equal.

### `get_card_offers`

Return current offers with their requirements, spend thresholds, time windows,
additive groups, evidence and expiry. An unknown expiry stays unknown. The tool
cannot determine whether the user is eligible for an offer.

### `get_card_benefits`

Return benefits with their conditions, enrollment requirements, caps,
exclusions and effective dates.

### `get_earning_rates`

Return earning rates with reward currency, category, caps, conditions and
effective intervals. Rates in different reward currencies are not comparable
as money.

### `get_card_fees`

Return annual, foreign transaction and other published fees with their
semantics (for example introductory or waived periods). An unknown fee is not a
zero fee.

## Recommendation tool

### `recommend_cards`

Return a qualitative shortlist for a supported goal. Requires `cards:read` and
`context:read`; including context updates also requires `context:write`.

- **Goals.** Supported goals are published in the tool's input schema. The
  planned v1 vocabulary is `cash_back`, `travel_rewards`, `dining`,
  `groceries`, `gas`, `hotel_loyalty`, `airline_loyalty` and
  `business_spending`; request order is priority. Unsupported goal tokens
  (`credit_building`, `balance_transfer`, `intro_apr`, `approval_odds`,
  `dollar_savings` or any other token) are not interpreted: the result is
  `needs_input` with follow-up questions. Free-form prose is not a goal token
  and is rejected as invalid input.
- **Hard constraints** are applied first: a maximum annual fee in US dollars,
  requiring no foreign transaction fee, and personal or business card type. A
  card whose relevant fact is unknown does not pass the constraint.
- **Wallet.** Cards the user holds resolve to canonical products and are
  excluded from additions. Unresolved cards stay disclosed as unknown and the
  result is marked `wallet_baseline_incomplete`.
- **Ordering.** Matches to the prioritized goals first, then known
  complementary benefits, then a stable identifier for ties. The order is
  deterministic for the same inputs and context version. It is a methodology
  order, not a verdict: the first candidate is not "the best", and tied
  candidates are ordered by identifier.
- **Output.** Three candidates by default and never more than five, each with
  supported facts, source references, publication identity, material
  limitations and follow-up questions, plus the methodology and context versions
  used. Current offer conditions are included when available.
- **Outcomes.** A shortlist, `needs_input`, no qualified candidates, and
  upstream or storage errors are distinct results.
- The result makes no eligibility, approval-odds, dollar-savings or
  cross-currency value claim.

## Context tools

### `get_my_context` (`context:read`)

Return the account's current saved context (cards held, spending disclosures,
goals, preferences, constraints and temporary plans, with provenance) and
paginated request history. Use it before recommending and whenever the user
asks what is remembered.

### `update_my_context` (`context:write`)

Save or correct facts the user stated explicitly. Updates are structured, not
free-form extraction. A current correction supersedes the older fact; adding or
removing one card leaves other saved cards unchanged; expired temporary plans
stop influencing recommendations. Free-text notes are limited to 4,096
characters and recognised credential, payment-identifier and URL patterns are
removed before storage, but filtering cannot catch every secret, so never send
credentials or payment details. Writes are versioned and deduplicated; a
conflicting concurrent change is reported rather than overwritten, and a
failed call saves nothing. Not read-only.

### `forget_my_context` (`context:write`)

Delete selected facts or all saved context and history. Deletion also removes
retained inputs, provenance and derived recommendation payloads that could
reconstruct the forgotten information, and prevents earlier retried requests
from recreating it. Destructive and idempotent: repeating the same deletion
has no further effect. Confirm the scope with the user first. Removal from
service backups is not immediate; its limits will be published in the privacy
guide before release.
