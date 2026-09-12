# Short list of tested hypotheses (for a quick duplicate check)

Full details for each — in `research_log.md`. This file is only for
quickly scanning "has this already been tested" before generating a
new hypothesis.

- [2026-09-10] C6 "fat start" — CONFIRMED (shelved, narrow window)
- [2026-09-10] C3-K10 positional pattern (odd days) — partially CONFIRMED (shelved)
- [2026-09-10] Consensus signal (threads ∩ analog) — CONFIRMED (tied to turbulence)
- [2026-09-10] C2 turbulence, local vs. systemic — CONFIRMED (local)
- [2026-09-10] Dynamic consensus trigger — REJECTED
- [2026-09-10] slow_balance_monitor wired into the score — REJECTED
- [2026-09-10] Optimal core/complement split (1..7) — REJECTED, "5+3 best"
- [2026-09-10] Thread pool of 5 vs. 8 — INCONCLUSIVE
- [2026-09-10] Compensation effect of the complement when the core fails — CONFIRMED
- [2026-09-10] Compositional null model, C2-C6 correlation — CONFIRMED (after fixing the method)
- [2026-09-10] Compression (0101) of the whole board — REJECTED
- [2026-09-10] Correlation dimension (chaos) of C3 — REJECTED
- [2026-09-10] Moran's I, individual draws — REJECTED
- [2026-09-10] Moran's I, aggregated frequency — REJECTED
- [2026-09-10] Coulomb's law (distance to C3) — REJECTED
- [2026-09-10] Variance of group thickness (crowding/clustering) — confirmed C3, nothing new
- [2026-09-10] Lag scan of the forecast, averaged — REJECTED
- [2026-09-10] Lag scan, local windows — REJECTED
- [2026-09-10] Cross-correlation of threads with each other (shadow/lag) — REJECTED
- [2026-09-10] #20 Fat start for R4 (variant of #1 for a row group) — REJECTED
- [2026-09-10] #21 Direct overlap of draw t and t-1 (no groups) — REJECTED
- [2026-09-10] #22 New thread family: toroidal diagonals D1-D7, turbulence scan — REJECTED (winner unstable across windows; p=0.15 even without correction)
- [2026-09-10] #23 New thread family: anti-diagonals AD1-AD7, hit-rate on the last 400 — REJECTED (AD4 direction consistent, but p=0.0125→0.0875 after correcting for choosing among 7, far above Bonferroni; unstable on a 300 window)
- [2026-09-10] #24 K6→R7 across 6 documented event segments (first run of Step 6) — REJECTED (full data already NOISE-LIKE, p=0.115; only the S6 tail p=0.0175, passes neither the global nor local correction)

**Next hypothesis number: #25**
**n for bonferroni_note() at start: 24**

- [2026-09-11] #25 "Reserve thread" during a triple pause (C3=0 ∧ K10=0 ∧ K6=0) — REJECTED (winner R7 confounded with the already-known K6→R7 rule; raw p=0.1125, passes neither the local scan threshold nor Bonferroni)
- [2026-09-11] #26 Draw position within the day (session effect, 1-4) — REJECTED (winner R4, spread=9.73pp, raw p=0.6457, a new analysis axis — not tested before)

**Next hypothesis number: #27**
**n for bonferroni_note() at start: 26**

- [2026-09-11] #27 Pause length vs. strength of the "snap-back" (spring effect) — REJECTED (winner R7, corr=-0.174, raw p=0.1943; direction opposite to the folk theory, a new test of the "gambler's fallacy" intuition)

**Next hypothesis number: #28**
**n for bonferroni_note() at start: 27**

- [2026-09-11] #28 Chi-square frequency test of individual numbers (atomic level) — REJECTED as an independent finding (statistically significant, p=0.0, but 55% of the statistic comes from group C3 alone — a confound with the already-known C3 skew, not new information)

**Next hypothesis number: #29**
**n for bonferroni_note() at start: 28**

- [2026-09-11] #29 Synergy of number pairs within a draw, controlling for the marginal skew (a new "weighted null model") — REJECTED (winner (17,24), both in C3; uniform null model p=0.1367, controlled for real marginals p=0.80 — the effect is fully explained by the known C3 skew from #28, no pair synergy)

**Next hypothesis number: #30**
**n for bonferroni_note() at start: 29**

- [2026-09-11] #30 Radioactive decay law (geometric distribution of pauses, "half-life") — REJECTED (winner K7, chi2=15.12, p=0.174; unstable, train=4.03/test=15.88; C3 chi2=0.676 — near-perfect memoryless decay, further closing out #28/#29)

**Next hypothesis number: #31**
**n for bonferroni_note() at start: 30**

- [2026-09-11] #31 Center of mass of a draw, autocorrelation (astronomy) — REJECTED (p=0.873)
- [2026-09-11] #32 Moment of inertia of a draw, autocorrelation (physics) — REJECTED (p=0.070)
- [2026-09-11] #33 Activation energy — instantaneous full saturation (chemistry) — INCONCLUSIVE (0 events for all 24 groups, statistic structurally degenerate at this data volume)
- [2026-09-11] #34 Conjunction/syzygy of anchor groups (astronomy) — REJECTED (p=0.733)
- [2026-09-11] #35 Dipole moment of a draw, autocorrelation (electrodynamics) — REJECTED (p=0.893)
- [2026-09-11] #36 Bond length — distribution of gaps between numbers (chemistry) — REJECTED (p=0.527)
- [2026-09-11] #37 Shannon entropy, trend over time (thermodynamics) — REJECTED (raw p=0.0125, but train/test have opposite signs, fails Bonferroni)
- [2026-09-11] #38 Harmonic oscillator, resonant ACF lag (physics) — REJECTED (p=0.544)
- [2026-09-11] #39 Population inversion — Boltzmann distribution (statistical physics) — REJECTED (p=0.712)
- [2026-09-11] #40 Magnetization — Ising model (physics) — REJECTED (p=0.126)

**Next hypothesis number: #41**
**n for bonferroni_note() at start: 40**

- [2026-09-11] #41 Hurst exponent R/S (nolds.hurst_rs, dynamical systems) — REJECTED (p=0.22)
- [2026-09-11] #42 Lyapunov exponent (nolds.lyap_r, chaos) — REJECTED (p=0.06)
- [2026-09-11] #43 DFA scaling exponent (nolds.dfa) — REJECTED (winner K10, raw p=0.045, fails Bonferroni; a monotonic trend across quarters — likely a DFA non-stationarity artifact, not a new effect)
- [2026-09-11] #44 Permutation entropy (antropy.perm_entropy) — REJECTED (p=0.15)
- [2026-09-11] #45 Higuchi fractal dimension (antropy.higuchi_fd) — REJECTED (p=0.645)

**Next hypothesis number: #46**
**n for bonferroni_note() at start: 45**

- [2026-09-11] #41 Gutenberg-Richter law, power-law distribution of hit-streak lengths (seismology) — REJECTED (winner K10, R²=0.9602, p=0.33; a high R² alone is not evidence without a null model)

**Next hypothesis number: #42**
**n for bonferroni_note() at start: 41**

- [2026-09-11] #42 Fano factor, bunching/antibunching (quantum optics/statistical physics) — REJECTED (all 24 groups show antibunching, F<1; winner K4, p=0.823 — a structural artifact of hypergeometric sampling, not a signal)

**Next hypothesis number: #43**
**n for bonferroni_note() at start: 42**

- [2026-09-11] #43 "Clustered" draws (cluster ≥3 on the 7×7 grid) and overlap with threads — INCONCLUSIVE (winner C1, dev=-23.44pp; fully explained by grid-edge geometry — R7/K10 are also the grid's edge row; p=0.0013 after correcting for 24 groups vs. a Bonferroni threshold of 0.001163 — fails, but by a hair; stable across quartiles/train-test)

**Next hypothesis number: #44**
**n for bonferroni_note() at start: 43**

- [2026-09-11] #44 "Clustered" draws — predictive value (forward test, no threads) — REJECTED (both tests noise, p=0.98/0.64; the #43 effect fully vanishes in the forward test: C1's deviation drops from -23.44 to +0.58 — confirms #43 was purely a structural fact about a single draw, not a predictor)

**Next hypothesis number: #45**
**n for bonferroni_note() at start: 44**

- [2026-09-11] #45 Spatial concentration of "clustered" draws on the 7×7 grid (heatmap) — explained by geometry (center 39.4% vs. edge 15.5%, a monotonic gradient with distance from center; the null model produces the same gradient within ~1.5σ) — REJECTED as a new finding

**Next hypothesis number: #46**
**n for bonferroni_note() at start: 45**

- [2026-09-11] #46 Re-check of "clustered" draws under toroidal adjacency (C1<->C7, R1<->R7) — REJECTED (C7/R1/R7 effect disappears/flips sign; C1 weakens by half to p=0.0675 NOISE-LIKE; conclusively confirms #43/#45 were a flat-grid-boundary geometric artifact)

**Next hypothesis number: #47**
**n for bonferroni_note() at start: 46**

- [2026-09-11] #47 Full protocol for cluster↔thread linkage under the torus (4 quarters + train/test) — conclusively REJECTED (all 6 anchor threads small and chaotic across quarters; the residual C1 fades to near zero: -20→-12→-11→+1 by quarter)

**Next hypothesis number: #48**
**n for bonferroni_note() at start: 47**

- [2026-09-11] #49 Methodological check of short memory windows (3-5-10 draws) for the cluster→thread forward effect — REJECTED (W=3,5: p≈0.82 pure noise; W=10: C6 p=0.022, fails Bonferroni and unstable across neighboring W)

**Next hypothesis number: #50**
**n for bonferroni_note() at start: 49**

- [2026-09-11] #50 Motor A and Motor B (Gtablenew_v6.py, OscillationEngineV4) — both REJECTED (A: p=0.282 pure noise; B: p=0.012, stable across quarters/train-test, but fails Bonferroni by a factor of 12)

**Next hypothesis number: #51**
**n for bonferroni_note() at start: 50**

- [2026-09-11] #51 Fix for #50: Motor A/B on the correct 905 draws + breakdown across 6 segments S1-S6 — REJECTED for both motors in all segments (closest: B/S3 p=0.014 fails the local Bonferroni ×86; A/S5 p=0.052 doesn't even clear the raw 0.05)

**Next hypothesis number: #52**
**n for bonferroni_note() at start: 51**

- [2026-09-11] #52 Search for a "rescue window" for weak periods of Motor A/B — REJECTED (diagnostics: window choice doesn't correlate with weakness; unconditional scan of 18 windows: winner W=200 (not short!), p=0.026, fails Bonferroni ×27, fades over time)

**Next hypothesis number: #53**
**n for bonferroni_note() at start: 52**

- [2026-09-11] #53 "Winning" windows for weak segments (S1/S3/S4) of Motor A/B — conclusively REJECTED (W=270 for S1 passed all internal tests and formally Bonferroni on the full sample, but this turned out to be data leakage: on a genuinely held-out S2-S6, p=0.116, failure; the other two candidates were pure noise immediately)

**Next hypothesis number: #54**
**n for bonferroni_note() at start: 53**

- [2026-09-11] #55 Short-term momentum for C3 at W=3,5,10 (burst→hit) — REJECTED (all three NOISE-LIKE: p=0.79/0.25/0.69; chaotic signs across quarters and train/test; consistent with #30 — C3 is memoryless)

**Next hypothesis number: #56**
**n for bonferroni_note() at start: 55**

- [2026-09-11] #56 Combined algorithm "threads + hot numbers" (step3_combined_fixed.py) — a real effect confirmed (p=0.0000, stable 4/4 quarters), but 78.6% of its strength is just the already-known C3 skew; a naive fixed bet on C3 with no algorithm at all OUTPERFORMS the whole complex algorithm (+0.120 vs +0.099 core; +0.170 vs +0.097 final) — complexity hurts here, it doesn't help

**Next hypothesis number: #57**
**n for bonferroni_note() at start: 56**

- [2026-09-11] #58 FIX for #56/#57: evaluating via P(≥3)/P(≥4)/P(≥5) instead of the mean — the picture CHANGES: the complex FINAL(8) gives significantly more 4+ hits (10, p=0.006) than the naive C3(4, p=0.42); the earlier conclusion "complexity hurts" was only true for the mean metric, not for 3+/4+

**Next hypothesis number: #59**
**n for bonferroni_note() at start: 58**

- [2026-09-11] #59 Re-check of Motor A/B via P(≥3)/P(≥4)/P(≥5) — REJECTED for both (A: even worse than chance on P≥4; B: P≥4 formally passes Bonferroni on the full sample, but Q4=0, test=noise p=0.31 — all 11 events occurred before July 2, then 2+ months of zero)

**Next hypothesis number: #60**
**n for bonferroni_note() at start: 59**

- [2026-09-12] #63 C3's dependence on draw position within the day (1-4) — REJECTED (spread between positions p=0.92 NOISE-LIKE, smaller than typical noise; direction chaotic across quarters: pos.3→pos.1→no leader→pos.1)

**Next hypothesis number: #64**
**n for bonferroni_note() at start: 63**

- [2026-09-12] #64 C3's dependence on day of week (Mon-Sun) — REJECTED (spread p=0.384 NOISE-LIKE, leading day chaotic across quarters: Tue→Wed→Sat→Mon)

**Next hypothesis number: #65**
**n for bonferroni_note() at start: 64**

- [2026-09-12] #65 Runs Test (Wald-Wolfowitz, NIST SP800-22, a cryptography method) on C3's hit series — REJECTED (analytical p=0.798, Monte Carlo p=0.998, both consistently NOISE-LIKE; cross-confirms C3's static nature via a method from a different discipline)

**Next hypothesis number: #66**
**n for bonferroni_note() at start: 65**

- [2026-09-12] #66 Markov chain order test (genomics, likelihood-ratio G-test) for C3's short-term memory, k=1-5 — REJECTED for all k (best, k=1: p=0.74 chi-sq / 0.77 MC; none clears even a raw 0.05)

**Next hypothesis number: #67**
**n for bonferroni_note() at start: 66**

- [2026-09-12] #67 Screening 23 threads (excluding C3) × 6 windows (3-80) for short forward memory — REJECTED after correcting for 138 combinations (best candidate K7/W=3: raw p=0.049, needs <0.00036; but 4/4 quarters and train/test agree on direction — a candidate for a separate, pre-registered check on new data)

**Next hypothesis number: #68**
**n for bonferroni_note() at start: 67**

- [2026-09-12] #68 K7→K1 ("after K7, K1 shows up" — the person's own observation) — REJECTED for both formulations (same draw, p=0.214; forward t→t+1, p=0.079 and the direction is OPPOSITE to what was described, in 3/4 quarters)

**Next hypothesis number: #69**
**n for bonferroni_note() at start: 68**

- [2026-09-12] #69 ARCH-LM volatility-clustering test (finance/GARCH) for C2 (4 windows) + C3/C6/K10 — REJECTED everywhere (closest: C2/W=10, p=0.434)
- [2026-09-12] #70 Transfer entropy (neuroscience, lag+1) for 6 thread pairs — REJECTED everywhere; K7→K1 closest (p=0.093), the 3rd independent method that fails to confirm this relationship

**Next hypothesis number: #71**
**n for bonferroni_note() at start: 70**

- [2026-09-12] #71 C-score (ecology, curveball null model) for K7×K1 — NOT CONFIRMED under Bonferroni, but z=3.01, consistent on train (z=1.85)/test (z=1.65), segregation — the strongest result of the session, a candidate for a dedicated follow-up
- [2026-09-12] #72 Survival analysis / hazard rate of dry streaks (C3,K7,C2,K10) — REJECTED (the rise in hazard is an estimator artifact, p=0.276)
- [2026-09-12] #73 Lempel-Ziv complexity (C3,K7,C2,K10) — REJECTED (after fixing a bug in the first implementation)
- [2026-09-12] #74 Hawkes self-excitation process (K7,C3) — REJECTED (MLE gives alpha=0 for both)
- [2026-09-12] #75 Formal change-point detection with a multiplicity correction (C2,C3,K7,K10) — REJECTED (C2 closest, p=0.093)

**Next hypothesis number: #76**
**n for bonferroni_note() at start: 75**

- [2026-09-12] Experiment: the K7<->K1 lens in the algorithm backtest — P(≥3)/P(≥4) did not change despite 390/855 changed pools; no practical benefit
- [2026-09-12] #76 C-score on C3×K10/C2×C6/K6×R7 (cross-validation) — all 3 confirmed (z=3.64/4.81/3.62)
- [2026-09-12] #77 Binary segmentation (C2,C3,K7) — REJECTED (consistent with #75)
- [2026-09-12] #78 RQA Determinism (C3,K7,C2,K10) — REJECTED, C2 closest (p=0.067)
- [2026-09-12] #79 Perron-Frobenius spectral gap (composite C3,K7,K1) — REJECTED (p=0.65)
- [2026-09-12] #80 Wavelet DWT energy (C3,K7,C2,K10) — K7 NOT CONFIRMED under global Bonferroni, but p=0.001, robust across seed/quarters/train-test; the 2nd independent method pointing at K7

**Next hypothesis number: #81**
**n for bonferroni_note() at start: 80**

- [2026-09-12] #81 C-score for K7 against 15 physically independent threads (fixed the R5/C-group artifact) — K4 (z=3.42) and R6 (z=3.25) pass the local Bonferroni correction
- [2026-09-12] #82 Precision check of K7×K4/K7×R6 (60 samples + train/test) — K7×K4 passes the global threshold on the full data (z=3.78), but weakens on test (z=1.64); K7's own hit-rate is normal (p=0.646). FINAL VERDICT: interesting, not stable enough, topic closed pending new data

**Next hypothesis number: #83**
**n for bonferroni_note() at start: 82**

- [2026-09-12] #83 K7 "pulsation" after a fat shot (the person's own observation) — REJECTED (n=11 events, direction even reversed at W=1,2)
- [2026-09-12] #84 Chain reaction, fat thread X → fat thread Y, a different one (the person's own observation) — REJECTED (475 events, p=0.65-0.73)
- [2026-09-12] #85 The "fluid with clumps" allegory (flow slowing down/speeding up around a fat event) — REJECTED, the effect is purely mechanical, only at the exact moment, with no inertia
- [2026-09-12] #86 The "gas pedal" allegory (a shared intensity regime with inertia) — REJECTED (autocorrelation of the thickness-variance index, p=0.12-0.92); the 3rd independent check of a "shared regime" this session

**Next hypothesis number: #87**
**n for bonferroni_note() at start: 86**

- [2026-09-12] #87 Extremal index theta (climatology/EVT, the weather allegory) for C3/K7/C2/K10/POOL, with S1-S6 segments and small rolling windows — REJECTED at every level of detail; the 7th independent check of "shared clustering of anomalies," also a null result

**Next hypothesis number: #88**
**n for bonferroni_note() at start: 87**

- [2026-09-12] #88 Scan statistic (epidemiology, Kulldorff) for K7/C3/C2/K10 and 5 pairs, W=5/10/20/40, both directions (burst and gap) — REJECTED everywhere; methodologically confirms that the "gray noise" isn't hiding a local signal even in the smallest windows

**Next hypothesis number: #89**
**n for bonferroni_note() at start: 88**

- [2026-09-12] #89 BOCPD (Bayesian Online Change Point Detection, Adams-MacKay) for C2/C3/K7/K10 — REJECTED (K10 closest, p=0.09); fixed a bug in the first implementation along the way

**Next hypothesis number: #90**
**n for bonferroni_note() at start: 89**

- [2026-09-12] #90 3 methods from GitHub (LSTM/LotteryAi-style, hot numbers, first-order Markov) on a 75/25 train-test split — LSTM is pure noise (P≥3 0.027, P≥4=0.000, worse than our algorithm); hot-numbers/Markov "beat" only the theoretical baseline, because they rediscover C3 (4.66/7 overlap); none beats our thread-based algorithm (P≥3=0.0749)

**Next hypothesis number: #91**
**n for bonferroni_note() at start: 90**
