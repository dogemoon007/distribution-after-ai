# Separation Scorecard for Distribution Schemes, v1.1

Four questions that test whether a scheme's announced dividend can be kept.

## What this scorecard does

Any scheme that claims to share the proceeds of AI, automated production or a natural resource with people can assess itself here, or be assessed by a third party. It applies to corporate pledges, public and sovereign funds, basic-income pilots, platform revenue-sharing and on-chain protocols.

It tests one thing: whether the scheme's structure allows its announced dividend to be paid over time. The basis is two papers. Proposition 4 of *Separating Capture from Allocation*: a dividend on autonomous output is positive if and only if three conditions hold together. The rule is fixed in advance (Q1), visible to those it governs (Q2), and set by a party that keeps none of what it leaves undistributed (Q3). Proposition 1 of *Binding at the Bottleneck*: a rule collects no more than it costs to go around it (Q4).

It does not judge whether the rate is fair, the scheme's commercial prospects, or the price of any token or asset. Passing all four questions is necessary for a dividend to be kept, not sufficient.

## Rules for filling it in

1. Support every answer with evidence: a link, contract address, statute, charter clause or audit report.
2. An answer without evidence is recorded as "cannot be verified" and counts as a fail. If outsiders cannot verify it, Q2 is not met.
3. State whether this is a self-assessment or a third-party assessment. Anyone may file another assessment of the same scheme; all are published side by side.
4. State the assessment date and the version of the scheme. Reassess after any change.
5. Planned improvements may be described, but the verdict reflects only what is in force on the assessment date.

## 1. Basic information

| Item | Answer |
|---|---|
| Name of scheme | |
| Type (corporate pledge / public fund / on-chain protocol / platform revenue-sharing / other) | |
| What is distributed (existence dividend on autonomous output / payment for contributions / both) | |
| To whom, per what unit (per person / per address / per holding / per contribution) | |
| Announced rate or amount | |
| Where the distributed output comes from | |
| Assessor, and the assessor's relationship to the scheme | |
| Assessment date | |
| Version, contract version or block height | |

## 2. Q1 Precommitment

Once output is realized, can any party that would gain from a different division change or waive the rule?

| No. | Question | Answer | Evidence |
|---|---|---|---|
| 1.1 | List every party that can change the distribution rule: admin keys, upgradeable proxies, multisigs, governance votes, boards, legislatures. | | |
| 1.2 | How long is the notice period between a proposed change and its taking effect? How does it compare with the capturer's investment cycle? | | |
| 1.3 | Can a change apply to output already realized but not yet paid out? | | |
| 1.4 | Are there pause, emergency or exemption powers? Who holds them, and when can they be used? | | |
| 1.5 | If the rule is broken, what enforceable remedy do recipients have (litigation, on-chain enforcement, exit)? | | |

Verdict:
- **Pass**: no party can change or waive the rule unilaterally once output is realized (1.1, 1.3, 1.4), and changes take effect only after notice and only for later output (1.2).
- **Partial**: changes require notice and are not retroactive, but a unilateral pause power exists.
- **Fail**: some party can change or waive the rule unilaterally after output is realized.

## 3. Q2 Observability

Can those the rule governs verify the rule before they act, and the transfers afterwards?

| No. | Question | Answer | Evidence |
|---|---|---|---|
| 2.1 | Is the full rule public, in a single authoritative location, with a version number? | | |
| 2.2 | Can recipients verify each payment afterwards (on-chain data, audit reports, public registers)? | | |
| 2.3 | Is the base (total output or revenue) published, not only the amount paid out? | | |
| 2.4 | Is the history of changes to the rule public and traceable? | | |
| 2.5 | Does verification require permission, payment or access an ordinary person cannot obtain? | | |

Verdict:
- **Pass**: 2.1 to 2.4 are "yes" and 2.5 is "no".
- **Partial**: the rule and the payments can be verified, but the base is not published, so the rate cannot be checked.
- **Fail**: the rule or the payments cannot be verified.

## 4. Q3 Independence

Does whoever sets the rule, can amend it, or controls the point where it is collected keep any part of what it leaves undistributed?

| No. | Question | Answer | Evidence |
|---|---|---|---|
| 3.1 | Who sets the rule, and who can amend it? (Compare with 1.1.) | | |
| 3.2 | Do any of these parties receive any part of the undistributed residual: equity, profit, treasury, fees, tax revenue, appreciation of assets they hold? | | |
| 3.3 | How is the power to amend allocated: per person, per holding, per contribution of capital, or by appointment? | | |
| 3.4 | What share of the amending power (votes, seats) do the capturer and its affiliates hold together? | | |
| 3.5 | How is the rule-setter chosen, for how long, and can it be removed? | | |
| 3.6 | Who owns or controls the point where the rule is collected (see 4.1)? Does that party charge there on its own account, and does it receive any of what the rule leaves undistributed? | | |

Verdict:
- **Pass**: no party with power to amend, and no party that controls the collection point, receives the residual; or its interest in the residual is negligible relative to its power and publicly disclosed.
- **Partial**: amending power is dispersed, and parties that receive the residual hold only a minority of it and do not control the collection point.
- **Fail**: a party that can amend the rule also receives the residual; or parties that receive the residual control a majority of the amending power; or the party that controls the collection point receives the residual and can decide how much is collected there.

Section 3.4 of the first paper explains why: the larger a rule-setter's stake in the residual, the more it behaves like a capturer. Proposition 5 of the second paper asks the same question at the collection point: where the bottleneck has an owner, the owner is already collecting, and a levy placed on top of it can collect at most half of what the owner earned before.

## 5. Q4 Enforceability

What does it cost to move a unit of output around the rule, and does the rule ask for less than that?

| No. | Question | Answer | Evidence |
|---|---|---|---|
| 4.1 | Where is the rule collected: at the output point (revenue, fees, sales), at an input point (compute, energy, licences, block space), or both? | | |
| 4.2 | What share of the relevant output must pass through that point? | | |
| 4.3 | How can output be routed around that point (another platform, contract, chain, jurisdiction or entity, off-ledger settlement), and roughly what does that cost per unit? | | |
| 4.4 | What does the rule take per unit at that point, and is it below the bypass cost in 4.3? | | |
| 4.5 | Is the rule enforced by the mechanism itself (no payment, no transaction), or by intermediaries that may choose not to enforce it (marketplaces, custodians, agencies)? | | |
| 4.6 | Over the last period, what fraction of the amount due under the rule was actually collected? | | |

Verdict:
- **Pass**: the collection point is identified (4.1); the rule takes less than a documented bypass cost, or cannot be bypassed inside the mechanism (4.3 to 4.5); and the amount collected is close to the amount due (4.6).
- **Partial**: part of the output can bypass the rule for less than the rule takes, but most still passes through it; or the bypass cost has not been estimated, but the amount collected is close to the amount due.
- **Fail**: bypassing costs less than the rule takes and output has moved; or enforcement depends on intermediaries that are free to stop enforcing.

Proposition 1 of the second paper explains why: a rule set above the bypass cost collects nothing. Proposition 3 adds that when capturers differ, collecting at both the output point and the input point collects more than collecting at either alone.

## 6. Supplementary items

These do not enter the verdict, but they decide whether a scheme that passes all four questions can actually pay.

| No. | Question | Answer | Evidence |
|---|---|---|---|
| A | Identity: if payment is per person, how is one claim per person ensured? Roughly what does it cost to fake one identity? What does it require of privacy? | | |
| B | Separation of payments: which part is paid to everyone regardless of contribution, and which depends on contribution? | | |
| C | Interests: what is the assessor's relationship to the scheme, and does the assessor hold related assets? | | |

## 7. Summary

| Question | Verdict (pass / partial / fail / cannot be verified) | Main evidence |
|---|---|---|
| Q1 Precommitment | | |
| Q2 Observability | | |
| Q3 Independence | | |
| Q4 Enforceability | | |

A scheme that passes Q1 to Q3 is "separated". One that passes all four is "separated and enforceable". Otherwise, name the question it fails. A conclusion can follow this form:

> As of the assessment date, this scheme fails Q__ because ______. Until that is resolved, its announced rate cannot be treated as a commitment.

## 8. Three examples

Filled in from public information, to show how the scorecard is used. None is a recommendation of any scheme.

**Example 1: the EIP-1559 base-fee burn on Ethereum**

| Question | Verdict | Evidence |
|---|---|---|
| Q1 | Pass | The base fee is set by a public formula from the fullness of earlier blocks and is burned. Block producers cannot change the formula; changing it requires a network-wide hard fork. |
| Q2 | Pass | The rule is public; the base fee and the amount burned in every block can be verified on-chain. |
| Q3 | Pass (with note) | The capturer (the block producer) controls inclusion but receives no base fee. The burn benefits all ETH holders, and those who take part in upgrade decisions may hold ETH. |
| Q4 | Pass (with note) | The base fee is part of the block-validity rule: a transaction that does not pay it cannot be included, and a side payment to the block producer cannot replace it. The only way around is to move activity to another chain or a layer-2 network. |
| Item B | — | The burn benefits holders in proportion to holdings; it is not a per-person existence dividend. |

**Example 2: the Alaska Permanent Fund Dividend**

| Question | Verdict | Evidence |
|---|---|---|
| Q1 | Fail | A formula exists in statute, but the amount is reset in each year's budget. In *Wielechowski v. State* (2017) the Alaska Supreme Court held that the dividend is subject to the ordinary appropriation and veto process. |
| Q2 | Pass | The statutory formula and each year's amount are public. |
| Q3 | Fail | The legislature that sets the amount also controls what is not distributed. |
| Q4 | Pass | The state collects royalties on minerals, which cannot be moved; the state constitution sends at least 25% of them to the Permanent Fund. The failure lies in Q1 and Q3, not at the collection point. |
| Outcome | — | In 2025 the formula implied about US$3,900 per person; US$1,000 was paid. |

**Example 3: NFT creator royalties (Q4 only)**

| Question | Verdict | Evidence |
|---|---|---|
| Q4 | Fail | Royalties were enforced by marketplaces and were not a condition of the trade. As marketplaces competed, Blur set a minimum royalty of 0.5% where creators typically asked 5% to 10%; OpenSea announced in August 2023 that it would stop enforcing them. |
| Outcome | — | Weekly royalty income fell from a peak of about 28,000 ETH in April 2022 to about 2,000 ETH in June 2023; the market itself also shrank over the period. |

Sources for the examples: [Roughgarden, Transaction Fee Mechanism Design](https://arxiv.org/abs/2106.01340); [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559); [Wielechowski v. State (2017)](https://law.justia.com/cases/alaska/supreme-court/2017/s-16558.html); [Alaska Public Media, 2 May 2025](https://alaskapublic.org/news/politics/2025-05-02/alaska-senate-committee-drops-proposed-2025-pfd-to-1-000-per-recipient-an-inflation-adjusted-low); [Alaska Permanent Fund Corporation, The Fund](https://apfc.org/the-fund/); [The Art Newspaper, 23 August 2023](https://www.theartnewspaper.com/2023/08/23/opensea-nft-marketplace-ending-resale-royalties-policy); [Cointelegraph on OpenSea's royalty enforcement tool](https://cointelegraph.com/news/opensea-disable-on-chain-royalty-enforcement-tool).

## 9. Version and licence

- Version: v1.1, November 2026.
- Changes from v1.0: Q4 Enforceability added; item 3.6 added to Q3; former item 1.5 and former supplementary item B (relocation) folded into Q4; former 1.6 renumbered 1.5; former supplementary items C and D relettered B and C; Example 3 added. Assessments made under v1.0 remain valid once Q4 and 3.6 are filled in.
- Basis: Titan, *Separating Capture from Allocation: A Commitment Model of Distribution after AI*, working paper v1.0, 2026; Titan, *Binding at the Bottleneck: An Enforcement Model of Distribution after AI*, working paper v1.0, 2026.
- Licence: CC BY 4.0. Free to use, translate and adapt with attribution.
- Proposed revisions: open an issue in the GitHub repository: https://github.com/dogemoon007/distribution-after-ai/issues.
