# Registry of tested MATHEMATICAL MECHANISMS

The purpose of this file is to distinguish a "new idea" (a new mechanism)
from a "new parameter combination" (the same mechanism, a different
thread/window). Before Step 2 in `CLAUDE.md`, ALWAYS check this list
first.

Format: **Mechanism** (source field) — what it tests — status and
short summary — cycles where it was applied.

## Mechanisms used

1. **Conditional frequency difference (conditional_diff/quarter_check/
   train_test_check)** (basic statistics) — whether the presence of
   group X in a draw changes the probability of Y (same or next draw).
   The basis of almost all "lag" hypotheses and opposite-pair searches
   in the project. Status: produced confirmed results (C3→K10, C2→C6,
   K6→R7, 17→31+4) for SIMULTANEOUS/near-term relationships; the
   forward version on arbitrary pairs (K7→K1 etc.) — noise. Cycles:
   most of the session, #55, #63, #64, #67, #68.

2. **Physics/astronomy analogies** (thermodynamics, nuclear physics,
   astronomy, seismology) — decay law, Ising model, Boltzmann, Fano
   factor, Gutenberg-Richter, center of mass, syzygy, harmonic
   resonator. Status: ~50 variants tested, ALL REJECTED. **Consider
   this direction exhausted** — a new hypothesis from this field
   should only be proposed if it's genuinely a different mechanism
   (not another "physics law applied to draws"). Cycles: #26-#45
   (old numbering), detailed in the reference doc.

3. **Physical pendulum model / Jacobian (Motor A/B)** — a dynamical
   system with external code. Status: REJECTED after several rounds
   of fixes (#50-#53, #59). Exhausted.

4. **7×7 grid geometry (toroidal topology, neighbor clusters)** —
   whether the "clustering" of adjacent numbers on the grid relates
   to threads. Status: REJECTED, explained as a grid-boundary artifact
   (#43-#47). Exhausted for this specific grid.

5. **Spectral analysis / autocorrelation of the smoothed series (ACF,
   peak search)** (signal processing) — whether there is periodicity
   in thickness/hit-rate. Status: REJECTED, explained as an artifact
   of the rolling-average smoothing itself (#61, confirmed in the
   reference doc too). Exhausted.

6. **Runs Test (Wald–Wolfowitz)** (cryptography / RNG certification,
   NIST SP 800-22) — whether runs of 0/1 cluster or alternate more
   than chance. Status: REJECTED (#65). Formally a different
   mathematical approach from the spectral/correlation one — counted
   as a separate, already-used mechanism.

7. **Markov chain order test (likelihood-ratio G-test)**
   (genomics/bioinformatics) — whether the last k states improve
   prediction of the next one, for k=1-5. Status: REJECTED for all k
   (#66). The reference doc also mentions "high-order Markov chains"
   as previously rejected — consistent.

8. **ARCH-LM (volatility clustering)** (finance/markets, GARCH
   family) — whether hit-rate volatility itself clusters in time
   (large deviations follow large deviations). Status: REJECTED for
   C2/C3/C6/K10 across 4 windows (#69).

9. **Transfer entropy** (neuroscience / complex systems analysis) —
   nonlinear directed information flow X→Y beyond Y's own past.
   Status: REJECTED for 6 pairs, including a sanity check on already-
   confirmed SIMULTANEOUS pairs (#70).

10. **Screening many threads at once (forward-momentum)**
    (a methodological approach, not a separate field) — the same
    mechanism as #1, but applied to ALL 23 threads at once with an
    explicit multiplicity correction. Status: REJECTED after
    correction (K7/W=3 closest, raw p=0.049 vs. the required 0.00036)
    (#67).

11. **C-score / checkerboard, curveball randomization** (ecology,
    Stone & Roberts) — pairwise thread co-occurrence, a null model
    that preserves BOTH marginal sums (thread frequency + draw
    "load"), a stricter control than standard Monte Carlo. Status:
    K7×K1 — the strongest result of the session (z=3.01, consistent
    on train/test), does not pass Bonferroni. Other pairs not yet
    tested with this method. Cycle #71.

12. **Survival analysis / hazard rate of dry streaks** (reliability
    theory) — whether the probability that a "dry streak" ends
    depends on how long it has already lasted. Status: REJECTED
    (C3,K7,C2,K10) — the apparent rise in hazard turned out to be an
    estimator artifact (too little data at large L). Cycle #72.

13. **Lempel-Ziv complexity** (coding theory) — the number of unique
    phrases in a greedy parse of the binary series. Status: REJECTED
    (C3,K7,C2,K10). Cycle #73.

14. **Hawkes process (MLE)** (seismology/epidemiology) — a self-
    exciting point process, LR-test against a pure Poisson process.
    Status: REJECTED (K7,C3) — the MLE itself converges to α=0.
    Cycle #74.

15. **Formal change-point detection (max-LR + Monte Carlo on the
    maximum)** (climatology/quality control) — with a correct
    correction for the multiplicity of candidate split points.
    Status: REJECTED (C2,C3,K7,K10), C2 closest (p=0.093), consistent
    with #69. Cycle #75.

16. **C-score on several pairs at once** (ecology, continuation of
    #11) — cross-validation of the already-confirmed pairs C3×K10,
    C2×C6, K6×R7. Status: all 3 confirmed (z=3.62-4.81). Cycle #76.

17. **Binary segmentation (multiple change points)** (continuation
    of #15, an approximation of PELT) — recursive search for change
    points. Status: REJECTED, consistent with #15/#75 (C2, same
    point, p=0.090). Cycle #77.

18. **Recurrence Quantification Analysis (RQA)** (nonlinear dynamics
    / complex-systems physics) — Determinism of the recurrence matrix
    in phase space. Status: REJECTED (C3,K7,C2,K10), C2 closest
    (p=0.067). Cycle #78.

19. **Perron-Frobenius / spectral gap** (spectral graph theory /
    Markov chains) — the "forgetting" rate of a composite state
    (C3,K7,K1 simultaneously). Status: REJECTED (p=0.65). Cycle #79.

20. **Wavelet analysis (DWT, db4)** (signal processing, different
    math from the spectral/Fourier method #5) — energy distribution
    across scales. Status: K7 — NOT CONFIRMED under the strict global
    Bonferroni correction (p=0.001, needs <0.000625), but robust
    across seed/quarters/train-test; the second independent method
    (after C-score #71) that points specifically at K7. C3, C2, K10 —
    REJECTED. Cycle #80.

## Cross-cutting finding of the session: K7 (numbers 31-35)

Two DIFFERENT mechanisms from different fields (C-score/ecology #71,
wavelet #80) independently point to K7 specifically as something
atypical — though neither passes the strict global Bonferroni
correction, and a practical check (the K7↔K1 lens in the backtest)
produced no improvement in P(≥3)/P(≥4). Worth priority attention in
future rounds — possibly worth checking K7 specifically with 1-2 more
independent methods (RQA with a different embed_dim, Recurrence Rate
instead of Determinism, or C-score for K7 against OTHER threads, not
just K1) before considering this exhausted.

21. **Bayesian Online Change Point Detection (BOCPD)** (Adams &
    MacKay, Bayesian statistics) — the posterior distribution of the
    current regime's run length at EVERY step, more precise than
    max-LR (#15/#17). Status: REJECTED (C2,C3,K7,K10), K10 closest
    (p=0.09). Cycle #89.

## Directions NOT yet used (candidates for future cycles)

- C-score for OTHER pairs (not just K7×K1) — method #11 has only been
  tested on one pair; worth trying on a few of the most notable pairs
  from the reference doc
- Bayesian change-point (PELT, BOCPD) — a more precise method than
  max-LR (#15) for finding multiple change points at once, not just
  one
- Recurrence Quantification Analysis (RQA) — ALREADY used (#18/#78)
  with Determinism; Recurrence Rate as the primary metric, or other
  embed_dim/radius values, not yet tried
- Perron-Frobenius / stationary distribution of the Markov chain —
  separate from the order test (#7), checking whether the EMPIRICAL
  transition matrix has an eigenvector that differs from uniform
- Wavelet analysis (instead of Fourier/spectral #5) — periodicity
  localized in both time and frequency, may catch non-stationary
  cycles that plain spectral analysis missed

## Update rule

After EVERY cycle that introduces a new mechanism (not just a new
parameter combination of an existing one), add an entry here with a
reference to the cycle number, before writing the summary in
`research_log.md`.

## MANDATORY rule (often forgotten — restate every time)

**S1-S6 segments and small rolling windows are checked ALWAYS, even
if the null model on the full sample already gave a clear
NOISE-LIKE result.** This is not an optional "extra step for
interesting results" — a total REJECTED on the full sample can hide
a segment or window with a real local effect (as happened with #67,
K7/W=3, where the full sample also failed the threshold, but the
direction was stable across 4/4 quarters). Before writing "VERDICT:
REJECTED" in the log, always show: (1) the breakdown by S1-S6, (2) at
least 3-4 small rolling windows (~100 draws). Only if none of them
show anything beyond what the null model already explained is
REJECTED considered final and complete.
