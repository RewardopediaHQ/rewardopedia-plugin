# Rewardopedia MCP tools

Status: pre-release. The server at `https://mcp.rewardopedia.com/mcp` is not yet
live. This page describes the eleven tools for version 0.1.0. It follows the
tool contract exported from Rewardopedia's server code into
[`schemas/vendor/rewardopedia-mcp/tools.json`](../../../schemas/vendor/rewardopedia-mcp/tools.json),
and CI checks the examples against that contract. When the server is live, the
tool descriptions, input/output schemas and annotations it advertises are
authoritative; if they disagree with this page, follow the server and report
the difference as a documentation bug.

## Shared rules

- **Identity.** The signed-in Rewardopedia account is determined from the OAuth
  connection. No tool accepts an account, user or customer identifier.
- **Arguments.** Argument names are camelCase, exactly as in each tool's input
  schema. Card tools and `recommend_cards` require `contentLocale` and
  `market`.
- **Locale and market.** Supported pairs are exactly `contentLocale` `en-US` or
  `es-US` with `market` `US`. Other pairs are refused; there is no fallback to
  another language or market.
- **Qualification.** Card results come only from cards with an eligible
  Rewardopedia publication for exactly the requested pair. A card missing from
  a result is not evidence that it does not exist.
- **Unknown values.** Unknown facts are `null` or listed as unknown, never zero,
  `false` or "none".
- **Bounded output.** Lists are paged or capped. A short list is not proof that
  no other cards exist.
- **Request history.** Every tool call except `forget_my_context` is recorded
  in the account's sanitized request history (operation, sanitized inputs,
  outcome and context version). Card tools record interest only (search text
  with long numbers, credentials and links redacted, filters and card slugs),
  never ownership. A call that cannot be recorded returns an error instead of
  its result, so no tool is read-only. See
  [the privacy guide](../../../docs/privacy-and-memory.md).
- **Quotas.** Each account is limited across all connected clients: 100
  requests per minute and 1,000 per hour.
- **Errors.** Missing or expired sign-in and missing permissions return
  authorization errors that ask the client to re-authorize. Quota exhaustion,
  unavailable card data and unavailable saved-context storage return distinct
  errors. A failed call never reports a saved change as successful.

## Permissions

| Permission | Allows |
| --- | --- |
| `cards:read` | The seven card tools, `recommend_cards`, and the card, issuer and category resources |
| `context:read` | `get_my_context`, and reading saved context in `recommend_cards` |
| `context:write` | `update_my_context` and `forget_my_context` |

`recommend_cards` needs `cards:read` and `context:read`. It accepts no context
updates and never changes saved context; save facts with `update_my_context`.

## Card tools (`cards:read`)

All seven take `contentLocale` and `market`. Except `search_cards`, each takes
one `slug` (a canonical slug from `search_cards` or a retired alias); results
name the canonical slug. A slug with no eligible publication for the pair
returns an error.

### `search_cards`

Find cards by `q` (one phrase matched against card name, issuer name or slug),
`issuer` (canonical issuer slug), `category` (canonical card category) and
`ranking` (a published Rewardopedia best list, returned in its order with each
card's published rank). Filters combine. Results are paged with `page` and
`pageSize` (at most 20); request `nextPage` until it is `null`. Results are
search results, not recommendations.

### `get_card_detail`

Return one card's full published facts for the pair: fees, earning rates and
their conditions, offers, benefits, APR, source references and publication
identity. Unknown values are `null`.

### `compare_cards`

Compare 2 to 5 cards given as `slugs`, in the requested order. Each entry is
`available` (with the card's facts), `duplicate` (an alias or repeat of an
earlier entry, named by position) or `unavailable`. `complete` is `false`
whenever an entry is unavailable: never present an incomplete comparison as
covering every requested card. Rewardopedia does not score or rank compared
cards; present trade-offs, keep conditions attached, and do not treat
different reward currencies as equal.

### `get_card_offers`

Return the card's current welcome-offer legs as the server evaluates them on
its `asOf` UTC date (legs past their end date or before their start date are
excluded). Legs sharing `offerGroupId` are additive parts of one offer;
different offers are alternatives and are never added together. Each leg keeps
its bonus in its own unit. `expiryKnown: false` means no end date is recorded,
which is not proof the offer is still available. A leg may carry a
`composition`: every part of the welcome offer (points, miles, cash back,
statement credits, free nights and so on), each in its own kind and unit, never
added together or converted. `perUnitCap` is the maximum for one unit, never
multiplied by the count. `limitations` lists material gaps. The tool cannot
determine whether the user is eligible.

### `get_card_benefits`

Return the card's benefits as served: rich benefit details (coverage, limits
with amounts, units and periods, activation requirements, covered and excluded
items, claim process, verification date and sources) and simple benefit rows.
Absence of a benefit is not evidence the card lacks it.

### `get_earning_rates`

Return each earning rate's category, rate in its native `rateUnit` (points or
miles per dollar, or percent cash back), conditions, cap period, effective
window (`effectiveFrom`/`effectiveTo`) and, when served, typed rate
components, thresholds, enrollment, promotional scope, minimum transaction,
linked-account tier, dynamic categories and merchant inclusions or exclusions,
with the card's reward currency and program. Rows are those Rewardopedia
records as current and not ended: a row whose `effectiveTo` is before today's
UTC date is not served (UTC can be ahead of the US local date). A missing
`effectiveTo` is an unknown end, not proof the rate continues. A cap amount
may be unknown even when a cap period is known. Rates in different units or
programs are not comparable as money.

### `get_card_fees`

Return each served fee's `type`, `amount` in its own unit (`$95`, `3%`),
notes and waiver conditions. Today Rewardopedia serves the annual fee and the
foreign transaction fee; `unreportedFeeTypes` lists every other fee type
(balance transfer, cash advance, late payment, over limit) as unknown, never
zero or waived. `waivedFirstYear` appears only when the source states it;
absent is not `false`.

## Recommendation tool

### `recommend_cards`

Return a qualitative shortlist for one pair with the `card-qualitative-v1`
method. Requires `cards:read` and `context:read`. Rewardopedia's API selects and
orders candidates; the tool never re-ranks them.

- **Arguments.** `contentLocale`, `market`, `goals` (goal tokens, highest
  priority first), `wallet` (cards the user owns now, each
  `{productName, cardSlug}`), `constraints` (`maxAnnualFeeUsd`,
  `noForeignTransactionFee`, `cardType` `personal` or `business`) and `limit`
  (default 3, at most 5).
- **Goals.** Vocabulary `card-goals-v1`: `cash_back`, `travel_rewards`,
  `dining`, `groceries`, `gas`, `hotel_loyalty`, `airline_loyalty` and
  `business_spending`. Unsupported tokens (`credit_building`,
  `balance_transfer`, `intro_apr`, `approval_odds`, `dollar_savings` or any
  other token) are not interpreted: the outcome is `needs_input` with
  follow-up questions. Free-form prose is refused as invalid input.
- **Saved context.** Saved context is read on every call. Remembered goals
  apply only when `goals` is empty; remembered wallet cards are added (an
  empty `wallet` does not clear them); a constraint sent now replaces the
  remembered one. Omit `wallet` when it is unknown. `savedContextUsed` is
  `true` exactly when the saved entries in `contextRefs` determined the
  answer; `unappliedContextRefs` names saved preferences and excluded issuers
  this method does not apply.
- **Hard constraints** apply first. A card whose relevant fact is unknown does
  not pass the constraint.
- **Wallet.** Owned cards are excluded. Cards that cannot be resolved leave
  the result marked `wallet_baseline_incomplete`.
- **Ordering.** Goal matches first, then complementary benefits, then a stable
  identifier for ties. Each candidate's `rank` (1 to 5) is this methodology
  order, not a quality score: never present `rank` 1 as "the best" or "#1".
- **Output.** `outcome` (`recommendations`, `needs_input` or
  `no_qualified_candidates`), candidates with matched and unmatched goals,
  facts, reasons, drawbacks, current offers (with any `composition`), unknowns
  and publication identity, `exclusions` as counts per reason, and
  `followUpQuestions` as objects with a `code` and, where relevant,
  `allowedValues`.
- The result makes no eligibility, approval-odds, dollar-savings or
  cross-currency value claim.
- **History.** The call records only the top goal, the pair, the
  `contextRefs` and the outcome; never the wallet, constraints or results.

## Context tools

`update_my_context` and `forget_my_context` are destructive and idempotent.
Both require `requestId`, a new UUID you choose for each distinct change, and
`expectedVersion`, the `contextVersion` from `get_my_context`. To retry the
same change after an error or a lost answer, resend it with the same
`requestId` and `expectedVersion`: it is applied once and the retry reports
`duplicate: true`. If saved context changed in between, the call fails with
`version_conflict` and nothing changes: call `get_my_context` again and decide
what still applies. Never resend a conflicting change automatically.

### `get_my_context` (`context:read`)

Return the account's saved entries (wallet cards, spending, goals,
preferences, constraints and temporary plans), each with its entry `id`,
source request and time, plus one page of request history, newest first.
Expired entries have `active: false` and never influence recommendations.
`contextVersion` is the `expectedVersion` for the next change. Page older
history with `before` set to `nextBefore`. The inspection itself is recorded
in history.

### `update_my_context` (`context:write`)

Save facts the user stated explicitly, as structured entries only. There is no
free-text field and nothing is inferred.

- `updates`: entries identified by `kind` and `key`. Kinds are `wallet`
  (`{productName, cardSlug}`), `spending` (`{category, monthlyAmount}` in USD),
  `goal` (`{goal, priority}`), `preference` (`{feature, priority}`),
  `constraint` (`{maxAnnualFeeUsd, noForeignTransactionFee, excludedIssuers,
  cardType}`) and `plan` (`{needs, destinationCountry}`, which requires
  `expiresAt`). A new `key` adds an entry and leaves others unchanged; an
  existing `key` replaces that entry. Use `assertionType: "correction"` when
  the user corrects a fact.
- `removeIds`: entry IDs from `get_my_context` to remove. One call cannot both
  update and remove the same entry.
- Hypotheticals, searches and comparisons are never ownership. Values that
  look like card numbers, account numbers or credentials are refused.

### `forget_my_context` (`context:write`)

Permanently delete saved context and history. `all: true` deletes every saved
entry and every history entry. Otherwise `entryIds` deletes those entries, and
`requestIds` deletes those history entries plus the entries they created or
changed. Every history entry recorded while a deleted entry existed is deleted
too, so later unrelated calls can go with it. Selective forgetting also clears
free text and proposed updates from all remaining history. Deleted requests can
never be replayed. Confirm the scope with the user first. This does not delete
the Rewardopedia account. Deleted data can remain in service backups until
they expire; for retention questions or full account deletion, the user emails
info@rewardopedia.com.
