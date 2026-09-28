# Synthetic examples

These files show how an assistant should use the Rewardopedia tools. Everything
in them is invented: card names, slugs, rates, fees, URLs, identifiers and
field names. They are not Rewardopedia data and not a schema reference. When
the server is live, its advertised tool schemas are authoritative.

| File | Shows |
| --- | --- |
| [needs-input.json](needs-input.json) | No supported goal, so the result asks follow-up questions |
| [shortlist-with-saved-context.json](shortlist-with-saved-context.json) | Disclosure notice, an explicit wallet fact, a fee constraint with an unknown fee, and conditions kept attached |
| [compare-without-a-winner.json](compare-without-a-winner.json) | Different reward currencies, an unknown fee and no universal winner |
| [correct-and-forget.json](correct-and-forget.json) | Spanish (`es-US`) inspection, a correction and confirmed deletion |

CI validates each file against [`schemas/example.schema.json`](../schemas/example.schema.json)
and rejects URLs outside reserved example domains. Keep new examples synthetic:
never use real people, accounts, card numbers or live card offers.
