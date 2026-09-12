# Research Log — Condensed Digest

This is a condensed English summary of the project's full hypothesis
log. The original working log ran to 90+ individually documented
cycles in Ukrainian; this digest groups them by theme, keeps the
numbers that matter, and skips the step-by-step derivations. For a
one-line index of every single cycle (still useful for spotting
duplicates), see `tested_hypotheses.md`. For the list of distinct
mathematical mechanisms tried, see `methods_registry.md`.

## Data and protocol

- **Dataset:** UK49s draws, ~905 draws from the start of the current
  regime (2026-01-27) through early September 2026, 4 draws/day.
- **"Threads":** three independent ways of partitioning the numbers
  1-49 into groups — K-groups (10 blocks of consecutive numbers),
  R-groups (7 rows of a 7×7 grid), C-groups (7 columns of the same
  grid, spaced 7 apart).
- **Standard verification protocol**, applied to essentially every
  hypothesis below before calling anything a finding:
  1. A specific, falsifiable hypothesis.
  2. A Monte Carlo null model (simulated random draws), not just "does
     it look non-random."
  3. A train/test split (first half vs. second half of the data).
  4. A breakdown across 6 documented time segments (S1-S6) and,
     later in the project, small rolling windows — because a null
     result on the full sample can hide a real local effect, and vice
     versa.
  5. Bonferroni correction against every other hypothesis already
     tested in the session (both a "local" correction when several
     variants were screened in one go, and a running "global" count).
  6. Only if all of the above hold up is something called CONFIRMED.

## Part 1 — Structural findings that held up (established before this session)

A handful of static, non-random skews survived the full protocol and
are the closest thing this project has to a real, reproducible signal:

- **C3** (the column {3,10,17,24,31,38,45}) has a stable, statistically
  significant elevated hit-rate — confirmed across 7+ months, all 4
  quarters, with no internal break points. This is the strongest
  single finding of the whole project.
- **C2–C6** — the strongest "opposite pair" by hit-rate, confirmed in
  every quarter.
- **K6→R7** — an opposite pair by both density and shot strength, with
  a full train/test pass (p=0.0275, p=0.0119).
- **17 → 31, lag +4** — the strongest specific lagged relationship
  found in the project, between two individual numbers, both inside
  C3. It survives a Bonferroni correction across 35 tested lag
  combinations (threshold ≈0.0014).
- **The triple (17, 24, 45)**, all inside C3 — the specific 3-number
  combination that recurs most often within C3's own "fat" draws
  (thickness ≥3). On held-out test data it appeared 3 times in 441
  draws against a theoretical expectation of 0.48 (6.25× enrichment).
- A minimal 2-rule consensus system (C3-K10 + C2-C6) is the only
  hit-rate system that passed a genuine train/test backtest (+6pp,
  p=0.0135).

These are treated as the project's baseline "known structure," and
every later hypothesis is checked against whether it's just
rediscovering one of these (mainly C3) rather than finding something
new.

## Part 2 — The big physics/astronomy/chemistry sweep (~50 variants, all rejected)

Early in the project, a large batch of hypotheses borrowed directly
from physical and astronomical laws, on the theory that these are
well-understood formal tools for detecting structure or its absence
in a process. All were rejected:

- Radioactive decay law / geometric distribution of pause lengths
  ("half-life") for hit streaks — REJECTED (nearly perfect memoryless
  decay for C3, unstable train/test for other threads).
- Center of mass, moment of inertia, dipole moment of a draw,
  autocorrelation of each — all REJECTED (p=0.87, 0.07, 0.89).
- Conjunction/syzygy of anchor groups (astronomy) — REJECTED (p=0.73).
- Bond length / gap distribution between drawn numbers (chemistry) —
  REJECTED (p=0.53).
- Shannon entropy trend over time (thermodynamics) — REJECTED (raw
  p=0.0125 looked interesting, but train and test had opposite signs).
- Harmonic oscillator / resonant ACF lag (physics) — REJECTED (p=0.54).
- Boltzmann population inversion, Ising-model magnetization (statistical
  physics) — both REJECTED (p=0.71, p=0.13).
- Hurst exponent, Lyapunov exponent, DFA scaling exponent, permutation
  entropy, Higuchi fractal dimension (nonlinear dynamics/chaos
  toolkit) — all REJECTED; the DFA candidate looked marginal (raw
  p=0.045) but failed Bonferroni and showed a trend consistent with a
  known DFA non-stationarity artifact rather than a real effect.
- Gutenberg-Richter power law for hit-streak lengths (seismology) —
  REJECTED (a high R² by itself isn't evidence without a null model).
- Fano factor / bunching-antibunching (quantum optics) — REJECTED;
  every thread showed "antibunching," which turned out to be a
  structural artifact of sampling 6 numbers without replacement, not
  a real effect.
- A cluster of hypotheses about "clustered" draws on the 7×7 number
  grid (geometric adjacency) — the initial result looked promising
  (deviation of -23pp, p=0.0013, just barely missing Bonferroni) but a
  forward-predictive test showed the effect vanishing completely
  (-23pp → +0.6pp), and a version of the grid with wraparound
  (toroidal) adjacency killed the effect too. Conclusion: this was a
  flat-grid-boundary artifact, not a real spatial clustering
  phenomenon.

**Conclusion for this whole family:** treated as an exhausted
direction. A new hypothesis from physics/astronomy is only proposed
later in the project if it's a genuinely different mechanism, not
another "law from physics applied to draws."

## Part 3 — A physical pendulum model ("Motor A/B") — rejected after several rounds

An external dynamical-systems model (a Jacobian-based pendulum
analogy, two variants "A" and "B") was tested extensively:

- First pass: both REJECTED, though B looked borderline (p=0.012,
  stable across quarters/train-test) until Bonferroni correction
  (needed by a factor of 12).
- A bug was found and fixed (wrong draw count), then both re-tested
  across all 6 time segments — REJECTED everywhere.
- A systematic search for a "rescue window" that might make the
  models work in their weak periods found nothing that survived
  Bonferroni, and what did look promising for one segment (W=270)
  turned out to be **data leakage** — it passed on the data used to
  select it, but failed completely on genuinely held-out future
  segments. This became a standing cautionary example referenced
  later whenever a "best window" search comes up.
- Re-evaluated later using P(≥3)/P(≥4)/P(≥5) hit-count metrics instead
  of the mean — still REJECTED for both variants.

## Part 4 — Complexity vs. simplicity (a genuinely useful negative result)

A combined "threads + hot numbers" algorithm was checked against a
naive strategy of just always betting on C3 with no algorithm at all.

- On the mean-hits metric, the naive C3-only bet actually
  **outperformed** the full combined algorithm (+0.120 vs +0.099 for
  the core, +0.170 vs +0.097 for the full pool) — complexity was
  hurting, not helping.
- This conclusion reversed once the evaluation metric was corrected
  to P(≥3)/P(≥4)/P(≥5) (the metrics that actually matter for a
  lottery, since a near-miss average is worthless): the complex
  8-number pool gave significantly more 4+-hit draws (10 vs 4,
  p=0.006) than the naive bet. **Lesson embedded in the project's own
  methodology after this: always evaluate with P(≥k) thresholds, never
  with a raw average.**

## Part 5 — Short-term memory, tested from every angle (all rejected)

A large fraction of the session was spent testing whether any thread
has short-term "memory" — does a recent hit make another hit more or
less likely soon after. Every formulation, across multiple
independent mathematical toolkits, came back negative:

- **Momentum / burst→hit** at W=3,5,10 for C3 — REJECTED, chaotic
  signs across quarters (p=0.79/0.25/0.69).
- **Runs Test** (Wald–Wolfowitz, the cryptography standard used to
  certify RNGs, NIST SP 800-22) on C3's hit series — REJECTED, cross-
  confirmed by both the analytical formula (p=0.798) and Monte Carlo
  (p=0.998).
- **Markov chain order test** (genomics/bioinformatics likelihood-
  ratio method) for C3, tested for memory depths k=1 through 5 all at
  once — REJECTED for every depth (best case, k=1: p=0.74).
- **Screening all 23 other threads at once** (excluding C3) for
  forward short-term momentum across windows 3-80 — the best
  candidate (K7, W=3) looked interesting (raw p=0.049) but needed
  p<0.00036 after correcting for the 138 combinations screened; it
  did show a consistent direction across all 4 quarters and train/
  test, which flagged it as worth a dedicated, non-screened follow-up
  rather than dismissing it outright (see Part 7, the K7 story).
- **A user-suggested pair, K7→K1** ("after K7 shows up, K1 tends to
  follow soon") — tested directly in both the same-draw and the
  forward t→t+1 form. Neither held up (p=0.214 and p=0.079), and
  the forward version's actual direction ran opposite to what was
  described in 3 of 4 quarters. Framed honestly as most likely a case
  of selective memory for memorable coincidences.
- **A specific personal observation** ("K7 hitting 4 numbers means it
  comes back again soon") — tested directly on the 11 times this
  actually happened in the dataset. No real effect either direction
  (n too small for power, and if anything the immediate next-draw
  rate was slightly below baseline, not above); the "it always comes
  back" impression was explained by the fact that K7's baseline
  probability of hitting again within a few draws is already close to
  ceiling (90%+) regardless of any prior event.
- **"Chain reaction" between different fat threads** (does one
  thread's big hit trigger another thread's big hit soon after) —
  tested across all 475 "fat" events (thickness ≥3) recorded across
  all 24 threads. REJECTED; if anything the observed rate was
  slightly below the unconditional baseline.

## Part 6 — Cross-domain methods sweep (the bulk of the later session)

Once the "obvious" memory tests were exhausted, the project
deliberately pulled in formal tools from unrelated fields — partly to
avoid re-testing the same underlying idea with a different label, and
partly because different mathematical machinery can catch different
kinds of structure. All of the following were tested with the full
protocol (null model, quarters, train/test, Bonferroni) and came back
negative unless noted:

- **ARCH-LM** (finance/GARCH family) — does the *volatility* of
  hit-rate itself cluster in time (do big deviations follow big
  deviations)? REJECTED for C2/C3/C6/K10 across 4 window sizes.
- **Transfer entropy** (neuroscience/complex-systems analysis) — a
  nonlinear, information-theoretic measure of directed information
  flow between two threads. Tested on 6 thread pairs, including a
  sanity check on pairs already confirmed at the *same-draw* level
  (which correctly came back near-zero, since transfer entropy tests
  a different, forward-in-time relationship) — REJECTED for all pairs
  tested for forward prediction.
- **Survival analysis / hazard rate of dry streaks** (reliability
  engineering) — REJECTED; an apparent "aging" pattern (rising hazard
  with streak length) turned out to be a statistical estimator
  artifact, not a real effect, confirmed via null model.
- **Lempel-Ziv complexity** (information/coding theory) — REJECTED
  after catching and fixing a bug in the first implementation, which
  had produced a false positive.
- **Hawkes self-exciting point process** (seismology/epidemiology,
  MLE-fitted) — REJECTED; the maximum-likelihood fit itself converged
  to zero self-excitation for every thread tested.
- **Formal change-point detection**, three different implementations
  across the session — a maximum-likelihood-ratio scan with a
  Monte Carlo null on the *maximum* statistic (correctly handling the
  multiple-comparisons problem of scanning many candidate split
  points), a recursive binary-segmentation version approximating
  PELT, and a full Bayesian Online Change Point Detection (BOCPD,
  Adams & MacKay) that tracks a posterior distribution over "how long
  has the current regime lasted" at every single time step. All three
  — REJECTED across every thread tested, though one thread (C2) kept
  coming up as the "closest to significant" candidate across multiple
  unrelated methods without ever actually crossing the line.
- **Recurrence Quantification Analysis (RQA)** (nonlinear dynamics) —
  REJECTED.
- **Perron-Frobenius / spectral gap** of a composite multi-thread
  state's transition matrix (spectral graph theory) — a way of
  measuring how fast the system "forgets" its state — REJECTED
  (p=0.65), no slow-mixing structural memory detected.
- **Wavelet decomposition (DWT)** (signal processing, a genuinely
  different mathematical basis from the earlier Fourier/ACF spectral
  test, which had been rejected as a smoothing artifact) — REJECTED
  for three threads, but produced a robust result for K7 (see Part 7).
- **C-score / checkerboard co-occurrence with curveball randomization**
  (ecology, Stone & Roberts) — a null model that, unlike the project's
  standard Monte Carlo, preserves *both* how often each thread fires
  *and* how many threads are simultaneously active in each specific
  draw. This produced the two most interesting results of the entire
  project (see Part 7), and also independently cross-validated the
  three already-confirmed opposite pairs (C3×K10, C2×C6, K6×R7 all
  showed z-scores of 3.6-4.8 under this stricter null model, in the
  expected "segregation" direction).
- **Extremal index (θ)** (climatology/extreme value theory) — a
  formal measure of whether extreme events cluster in time more than
  chance would predict (the same statistic used to ask "do heat waves
  come in clusters"). Tested with a full breakdown across time
  segments and small rolling windows specifically to make sure no
  local signal was being averaged away — REJECTED at every level of
  detail; a pooled version that initially looked like clustering
  turned out to be a mechanical artifact of the sheer number of "fat"
  events, confirmed by comparing directly to what a null model
  produces on pure noise.
- **Temporal scan statistic** (epidemiology — the same class of method
  used to detect disease-outbreak clusters). This was run specifically
  in response to a request to check small windows (5/10/20 draws)
  directly, rather than aggregate statistics over the whole ~900-draw
  sample, with a Monte Carlo null model on the *maximum* over all
  scanned windows (the statistically correct way to avoid the "some
  window will look extreme by pure chance if you scan a thousand of
  them" trap). REJECTED in both directions (bursts and gaps) for
  every thread and pair tested.
- Two "everyday allegories" proposed by the person running the
  project were also translated into formal tests: a "fluid with
  suspended clumps" analogy (does the overall "flow" of the board
  slow down approaching a big event and speed up after) and a "gas
  pedal" analogy (a shared, inertial intensity regime driving the
  whole board at once). Both were rejected: the apparent slowdown at
  a "fat" event turned out to be purely mechanical (3+ of 6 numbers
  locked into one thread mechanically leaves less room for the rest
  of the board, with zero lead-in or lag), and no shared intensity
  index showed any autocorrelation beyond noise.

## Part 7 — The K7 story (the project's most-investigated open thread)

K7 (the numbers 31-35) is the one thread that kept surfacing as
"closest to interesting" across genuinely independent methods, so it
got a dedicated final round of scrutiny:

- **C-score (ecology, #71/#81/#82):** K7 showed statistically
  significant *segregation* (avoids co-occurring) with several other
  threads at once — K1 (z=3.01), and, once a screen was widened to
  check all 15 threads that don't physically overlap with K7, K4
  (z=3.42) and R6 (z=3.25) as well. A precision re-check of K7×K4
  with more samples gave z=3.78 on the full dataset, which is strong
  enough to pass even a strict global Bonferroni correction — the
  only result in the whole project to do so. However, on a genuine
  train/test split the effect weakened substantially (train z=3.68,
  test z=1.64), the classic signature of an unstable or decaying
  effect rather than a solid structural one.
- **Wavelet analysis (#80):** independently, K7 showed a robust
  concentration of energy at the coarsest (slowest) decomposition
  scale (p=0.001, stable across random seeds, mostly stable across
  quarters, consistent on train/test) — not explainable as a simple
  linear trend in K7's hit-rate.
- **Important control:** K7's own base hit-rate is completely normal
  (0.4906 vs. a theoretical 0.4952, p=0.646) — whatever is unusual
  about K7 is about how it relates to other threads, not about its
  own frequency.
- **Practical test:** a scoring "lens" that penalizes K7 or K1
  whenever the other was recently active was added directly to the
  live prediction algorithm and backtested on 855 draws. Even though
  it changed the actual predicted number pool on 390 of 855 draws,
  **P(≥3) and P(≥4) — the metrics that actually matter — did not move
  by a single decimal point.** Any real effect here is too small to
  matter for the actual prediction task.

**Final verdict on K7:** a real, repeatable pattern across two
independent statistical disciplines, one result formally clearing even
the strictest correction threshold — but unstable on a genuine
train/test split and of zero demonstrated practical value. Logged as
"interesting, not confirmed," topic closed pending new data rather
than treated as a discovery.

## Part 8 — Testing GitHub's "AI" lottery predictors (this project's comparison point)

As a final, separate exercise, three approaches representative of
what's publicly claimed to work for lottery prediction on GitHub were
faithfully reimplemented and benchmarked against this project's own
method, using an identical 75/25 train/test split:

| Method | Avg. hits (pool of 8) | P(≥3) | P(≥4) |
|---|---|---|---|
| LSTM (Embedding→LSTM→Dense sigmoid, the standard architecture behind most "AI lottery" repos, including a paid $15/report service) | 0.987 | 0.027 | 0.000 |
| "Hot numbers" (rolling-frequency heuristic) | 1.022 | 0.063 | 0.000 |
| First-order Markov chain | 1.058 | 0.045 | 0.000 |
| Theoretical random baseline | 0.980 | 0.022 | 0.001 |
| **This project's thread-based algorithm** | **1.133** | **0.075** | **0.007** |

The LSTM's average hit rate was statistically indistinguishable from
pure chance. The two simpler heuristics did technically beat the
theoretical random baseline — but checking why showed their top-8
picks overlapped with the already-known C3 skew on 4.7 of 7 slots on
average (vs. 1.1 expected by chance): they weren't finding anything
new, just crudely and noisily rediscovering C3 through brute frequency
counting. None of the three came close to this project's own,
considerably simpler method.

## Overall conclusion

Out of roughly 90 individually tested hypotheses, spanning around 20
distinct mathematical mechanisms borrowed from physics, astronomy,
chemistry, cryptography, genomics, finance, neuroscience, ecology,
climatology, epidemiology, reliability engineering, signal processing,
and information theory, the vast majority came back REJECTED. A small
number of pre-existing static skews (mainly C3) remain the project's
only reproducible structure. Two additional results (K7's co-occurrence
pattern and its wavelet signature) are flagged as genuinely interesting
but not confirmed, and have already been shown to carry no practical
predictive value even where they are statistically real. This is
treated throughout as the expected, correct outcome for a fairly-run
lottery, not as a disappointing one — the point of the exercise was
the rigor of the process, not finding a way to win.
