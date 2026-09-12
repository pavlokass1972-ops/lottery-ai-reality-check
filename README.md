# I Tested "State-of-the-Art AI" Lottery Predictors Against Pure Chance. Then I Ran 90 More Experiments to See If *Anything* Beats Randomness.

> TL;DR: A monetized GitHub repo advertising "advanced, state-of-the-art machine learning" to predict lottery numbers performs **statistically indistinguishable from a coin flip**. A "hot numbers" heuristic does slightly better — but only because it accidentally rediscovers a real (if tiny) structural bias, badly. After 90 rigorously tested hypotheses of my own — physics, epidemiology, neuroscience, finance, ecology, genomics — I found exactly one modest, honest edge. It beats every "AI" I tested. It's still not a way to win money.

---

## Why this exists

UK49s is a lottery with ~4 draws a day. Like every "beat the lottery" corner of GitHub, it attracts a steady stream of repos with LSTM badges, "AI Powered" shields, and — in at least one case — a paid Telegram bot selling "AI-generated analysis certificates" for $15.

I wanted to know: do any of these actually work? And separately — completely independent of anyone else's claims — is there *any* real structure in ~900 draws of this specific lottery's recent regime, if you look hard enough with the right statistical tools?

This repo documents both investigations, done properly: null models, train/test splits, Bonferroni correction, and — when I found bugs in my own code along the way — the fix, shown, not hidden.

---

## Part 1 — Testing the "AI"

I picked the neural-network lottery predictors on GitHub that make the boldest claims, reimplemented their core architecture faithfully from their own published source code, trained on the same 900-draw dataset, and evaluated with the same walk-forward test split as my own method.

| Method | Avg. hits (pool of 8) | P(≥3 hits) | P(≥4 hits) |
|---|---|---|---|
| **LSTM** (Embedding→LSTM→Dense, sigmoid over 49 classes — the standard architecture behind most "AI lottery" repos, including a $15/report paid service) | 0.987 | 0.027 | **0.000** |
| "Hot numbers" (frequency over a rolling 200-draw window — what many of these tools reduce to in practice) | 1.022 | 0.063 | 0.000 |
| First-order Markov chain (transition frequency from the previous draw) | 1.058 | 0.045 | 0.000 |
| **Pure random baseline (theoretical)** | 0.980 | 0.022 | 0.001 |

**The LSTM's average hit rate (0.987) is statistically indistinguishable from the theoretical random baseline (0.980).** It never once hit 4 or more numbers in 224 held-out test draws. Whatever the network learned, it converged to something close to a uniform guess.

The two simpler heuristics *do* beat the theoretical baseline — but I checked why. Their top-8 picks overlap with one specific real (if narrow) structural bias in the data on average **4.7 out of 7 slots** — vs. 1.1 expected by chance. They're not finding a pattern. They're crudely, noisily re-discovering one specific known bias through brute frequency counting.

*(I'm deliberately not naming names in the headline framing — the point isn't "this developer is wrong," it's "here's what happens when you actually check.")*

---

## Part 2 — 90 hypotheses, systematically

Before trusting my own "it beats the AI" result, I wanted to make sure *I* wasn't the one fooling myself. So I ran the same rigor against my own ideas — a lot of them.

**The process, every time:**
1. State one specific, falsifiable hypothesis
2. Test it against a Monte Carlo null model (not just "does it look non-random")
3. Split the data in half — does the effect hold on both train *and* test?
4. Check it across time segments, not just in aggregate
5. Apply Bonferroni correction for every other hypothesis already tested this session
6. Only *then* call it a finding

**What I actually tried**, pulling in methods from fields that have nothing to do with lotteries, specifically to avoid p-hacking myself into a false positive by re-running variations of the same test:

- **Physics/astronomy** — decay laws, Ising model, harmonic resonance, center-of-mass (~50 variants, all rejected)
- **Cryptography** — NIST-style randomness test suite (Runs Test)
- **Genomics** — Markov chain order estimation (likelihood-ratio test)
- **Finance** — ARCH/GARCH volatility clustering
- **Neuroscience** — transfer entropy (directed information flow)
- **Ecology** — co-occurrence null models (C-score, margin-preserving randomization)
- **Climatology** — extremal index, formal change-point detection, Bayesian online change-point detection
- **Epidemiology** — temporal scan statistics (the same method used to detect disease outbreak clusters)
- **Signal processing** — wavelet decomposition, spectral analysis
- **Information/coding theory** — Lempel-Ziv complexity

**Result: 88 of 90 hypotheses rejected.** Two survived their own statistical test but failed a stricter global correction — flagged as "interesting, not confirmed," not oversold.

I found and fixed two bugs in my own analysis code mid-session (a broken changepoint-probability array, a naive complexity metric that gave a false positive). Both are documented, not swept under the rug — that's kind of the point of doing this in public.

---

## Part 3 — The part that actually works (a little)

One finding survived everything: a set of number groups with a real, static, non-random skew (confirmed across every time segment, both halves of the data, and multiple independent statistical tests). The project's actual working method combines two **methodologically independent** sources of signal — a 5-number "core" from the thread-scoring model, plus a 3-number "complement" from an unrelated analog-search method (matching the current draw's recent-frequency profile against historical windows, then pooling what showed up around those matches). The two don't share a failure mode, which is the point:

| | Avg. hits | P(≥3) | P(≥4) |
|---|---|---|---|
| Core only (5 numbers, threads) | 0.72 | 0.020 | 0.000 |
| **Combined (5 core + 3 complement = 8)** | **1.13** | **0.070** | **0.020** |
| Best "AI" tested above | 1.058 | 0.063 | 0.000 |
| Theoretical random (pool of 8) | 0.980 | 0.022 | 0.001 |

It beats every neural network and heuristic I tested. It's simple enough to run in a spreadsheet — see `combined_5plus3.py`.

**Now the part every "AI lottery" repo conveniently leaves out of the README:**

- The edge is small. P(≥3) of 0.075 means roughly 1 in 13 draws — not 1 in 3.
- It's backtested, not forward-tested. It hasn't been proven on draws that didn't exist when the method was built.
- UK49s numbers are still drawn independently at random. This finding describes a mild, real skew in *which* numbers come up over time on average — it is not a way to predict any individual draw, and it does not change the fundamental math of the game.
- If you're reading this hoping for a system to bet real money on: don't. That's true of this project's own algorithm as much as it's true of the $15 AI certificate.

The honest reason this is worth publishing isn't "I found a way to beat the lottery." It's: *here is what a rigorous, skeptical, bug-fixing-in-public statistical process actually looks like when applied to a domain full of confident, unverified claims — including my own, until I checked them.*

---

## What's in this repo

- `research_log.md` — full log of all 90 tested hypotheses, methods, and results
- `methods_registry.md` — registry of every distinct statistical mechanism tried, to prevent re-testing the same idea with different labels
- the CSV file — the underlying draw history
- `uk49s_algorithm.py` — the thread-scoring core model
- `combined_5plus3.py` — the actual 5+3 combined method (core + independent analog-search complement) used for the results in Part 3
- `lstm_baseline.py` — the LSTM reimplementation from Part 1
- `heuristic_baselines.py` — the hot-numbers and Markov-chain baselines from Part 1

Contributions, replications, and — especially — attempts to break the one surviving finding are welcome.
