# Security policy

## Scope

This repository contains the public plugin package: manifests, the assistant
skill, documentation, examples and validation scripts. The Rewardopedia MCP
server and API are operated by Rewardopedia and are not in this repository,
but you may report issues with them here too.

Examples of security issues:

- a credential, token or personal data committed to this repository;
- a manifest or guide that points users at an endpoint other than
  `https://mcp.rewardopedia.com/mcp`;
- skill or documentation text that could lead an assistant to leak saved
  context, store payment details or skip a deletion confirmation;
- an authorization, account-isolation or deletion flaw in the Rewardopedia
  service.

## Reporting a vulnerability

Please do not open a public issue or pull request for a vulnerability.

Report it privately through this repository's **Security** tab using
**Report a vulnerability**. If private reporting is unavailable, contact
Rewardopedia through [rewardopedia.com/contact](https://www.rewardopedia.com/contact)
and ask for a private channel, without including vulnerability details.

Include what you found, how to reproduce it and its impact. Never include real
card numbers, account credentials or another person's data; use synthetic
values.

## Supported versions

Nothing has been released yet. Once `v0.1.0` is tagged, security fixes apply to
the latest release.

## If a secret is exposed

If you notice a credential in this repository or its history, report it
privately as above. Rewardopedia will revoke and rotate the credential first;
removing it from Git history alone is not enough.
