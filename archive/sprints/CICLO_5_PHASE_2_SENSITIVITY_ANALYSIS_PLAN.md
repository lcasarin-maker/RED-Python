# 📊 CICLO 5 PHASE 2 — SENSITIVITY ANALYSIS EXECUTION PLAN
## Parameter Variation & Impact Assessment (200k Baseline)
**Scheduled:** Weeks 4-5 (Jun 23 - Jul 05, 2026) | **Duration:** 40 hours | **Status:** 🔴 PENDING EXECUTION

---

## 🎯 PHASE 2 OVERVIEW

```
╔════════════════════════════════════════════════════════════════════════════════╗
║        CICLO 5 PHASE 2: SENSITIVITY ANALYSIS (Parameter Variation)            ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Total Duration: 40 hours (2 weeks)                                           ║
║  Status: READY FOR EXECUTION                                                  ║
║                                                                                ║
║  Phase 2a: Parameter Grid Exploration ..................... 20h               ║
║  Phase 2b: One-Way Sensitivity Analysis ................... 10h               ║
║  Phase 2c: Two-Way Sensitivity Analysis ................... 10h               ║
║                                                                                ║
║  Baseline: 200,000 simulations (from Phase 1)                                ║
║  EV baseline: -$2.87 per 100-spin session                                    ║
║  Output: Sensitivity heatmaps & variance report                              ║
║  Next Phase: Phase 3 (Risk Model Validation)                                 ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 BASELINE PARAMETERS (from Phase 1)

```
ROULETTE SIMULATION MODEL:
├─ Initial Bankroll: $1,000
├─ Bet Amount: $10 (fixed)
├─ Spins per Session: 100
├─ Red Probability: 18/37 (European roulette)
├─ Black Probability: 18/37
├─ Green (0) Probability: 1/37
├─ Expected Value (EV): -$2.87 per session (-2.7% house edge)
├─ Coefficient of Variation: 0.514% (excellent convergence)
├─ Confidence Interval (95%): [-$4.91, -$0.83]
│
└─ Tested at: 200,000 simulations
   └─ Result: Perfect match to theoretical expectations (p=0.398)
```

---

## 📅 WEEKS 4-5 EXECUTION SCHEDULE

### **PHASE 2a: PARAMETER GRID EXPLORATION (Week 4, 20 hours)**

**Monday-Wednesday: Jun 23-25 (12 hours)**

```
MON Jun 23 (4h):
├─ Setup Phase 2 Environment
│  ├─ Load 200k baseline results from Phase 1
│  ├─ Create parameter variation framework
│  ├─ Set up output directories for sensitivity runs
│  ├─ Configure logging for parameter tracking
│  └─ ✅ Target: Environment ready by 10am
│
├─ Define Parameter Ranges
│  ├─ Bankroll: [$500, $750, $1000, $1500, $2000]
│  ├─ Bet Amount: [$5, $10, $20, $50, $100]
│  ├─ Spins/Session: [50, 100, 200, 500, 1000]
│  ├─ Total combinations: 5 × 5 × 5 = 125 scenarios
│  └─ ✅ Target: Grid defined by 12pm
│
├─ Batch 1 Execution (12pm-4pm)
│  ├─ Scenarios 1-25 (Bankroll sensitivity, fixed bet & spins)
│  ├─ Run 10k simulations per scenario
│  ├─ Total: 250k simulation samples
│  ├─ Monitor CPU: 95% ✓
│  ├─ Monitor Memory: 4-5 GB ✓
│  └─ ✅ Target: Batch 1 complete by 4pm, results saved
│
└─ Progress Check (4pm-4:30pm)
   ├─ Verify 25 scenarios executed
   ├─ Check output file integrity
   ├─ Validate convergence metrics
   └─ ✅ Status: ON SCHEDULE

TUE Jun 24 (4h):
├─ Batch 2 Execution (8am-12pm)
│  ├─ Scenarios 26-50 (Bet amount sensitivity, fixed bankroll & spins)
│  ├─ Run 10k simulations per scenario
│  ├─ Total: 250k simulation samples
│  └─ ✅ Target: Batch 2 complete by 12pm
│
├─ Batch 3 Execution (12pm-4pm)
│  ├─ Scenarios 51-75 (Spins sensitivity, fixed bankroll & bet)
│  ├─ Run 10k simulations per scenario
│  ├─ Total: 250k simulation samples
│  └─ ✅ Target: Batch 3 complete by 4pm
│
├─ Incremental Analysis (4pm-4:30pm)
│  ├─ Plot early sensitivity curves
│  ├─ Identify non-linear effects
│  ├─ Flag unexpected behavior
│  └─ ✅ Status: 60% of grid complete
│
└─ Mid-Week Review (4:30pm)
   ├─ All batches successful ✓
   ├─ No execution errors ✓
   └─ Performance on target ✓

WED Jun 25 (4h):
├─ Batch 4 Execution (8am-12pm)
│  ├─ Scenarios 76-100 (Multi-parameter variation 1)
│  ├─ Run 10k simulations per scenario
│  ├─ Total: 250k simulation samples
│  └─ ✅ Target: Batch 4 complete by 12pm
│
├─ Batch 5 Execution (12pm-3pm)
│  ├─ Scenarios 101-125 (Multi-parameter variation 2)
│  ├─ Run 10k simulations per scenario
│  ├─ Total: 250k simulation samples
│  └─ ✅ Target: Batch 5 complete by 3pm
│
├─ Full Grid Completion (3pm-4pm)
│  ├─ Verify all 125 scenarios executed
│  ├─ Verify all output files present
│  ├─ Backup complete grid results
│  └─ ✅ Grid exploration 100% complete
│
└─ ✅ WEEK 4 HALF-TIME STATUS: ON SCHEDULE
   └─ 1,250,000 total simulations executed
   └─ Zero execution errors
   └─ All results validated and archived
```

**Thursday-Friday: Jun 26-27 (8 hours)**

```
THU Jun 26 (4h):
├─ Initial Sensitivity Matrix Construction (8am-10am)
│  ├─ Aggregate 125 scenario results
│  ├─ Calculate EV for each scenario
│  ├─ Calculate std dev for each scenario
│  ├─ Calculate profit probability for each scenario
│  └─ ✅ Matrix complete by 10am
│
├─ Visualization - Bankroll Sensitivity (10am-12pm)
│  ├─ Plot 1: EV vs Bankroll ($500-$2000)
│  │  └─ Show slope of EV change (should be ~0)
│  ├─ Plot 2: Profit Probability vs Bankroll
│  │  └─ Show convergence to 50% (should be flat)
│  ├─ Plot 3: Standard Deviation vs Bankroll
│  │  └─ Show scaling relationship
│  └─ ✅ Charts complete by 12pm
│
├─ Visualization - Bet Amount Sensitivity (12pm-2pm)
│  ├─ Plot 4: EV vs Bet Amount ($5-$100)
│  │  └─ Show linear relationship (EV scales with bet)
│  ├─ Plot 5: Volatility vs Bet Amount
│  │  └─ Show sqrt(bet) scaling
│  ├─ Plot 6: Ruin Probability vs Bet Amount
│  │  └─ Show exponential increase with bet size
│  └─ ✅ Charts complete by 2pm
│
├─ Data Validation (2pm-4pm)
│  ├─ Verify all plots mathematically consistent
│  ├─ Check for outliers or anomalies
│  ├─ Validate against theoretical models
│  └─ ✅ All validations pass
│
└─ ✅ Daily Progress: Visualization complete

FRI Jun 27 (4h):
├─ Visualization - Spins Sensitivity (8am-10am)
│  ├─ Plot 7: EV vs Spins (50-1000)
│  │  └─ Show EV stays constant (house edge constant)
│  ├─ Plot 8: Std Dev vs Spins
│  │  └─ Show sqrt(spins) scaling
│  ├─ Plot 9: Confidence Interval Width vs Spins
│  │  └─ Show narrowing with more spins
│  └─ ✅ Charts complete by 10am
│
├─ Parameter Grid Summary Report (10am-12pm)
│  ├─ Create comprehensive parameter sensitivity table
│  ├─ Document all 125 scenarios with results
│  ├─ Calculate sensitivity coefficients
│  │  ├─ EV sensitivity to each parameter
│  │  ├─ Volatility sensitivity to each parameter
│  │  └─ Ruin probability sensitivity to each parameter
│  └─ ✅ Report complete by 12pm
│
├─ Heatmap Generation (12pm-2pm)
│  ├─ 3D Heatmap: Bankroll × Bet Amount (EV impact)
│  ├─ 3D Heatmap: Bet Amount × Spins (Volatility)
│  ├─ 3D Heatmap: Bankroll × Spins (Ruin Probability)
│  └─ ✅ Heatmaps complete by 2pm
│
├─ Phase 2a Wrap-up (2pm-4pm)
│  ├─ Archive all 125 scenario results
│  ├─ Generate preliminary conclusions
│  ├─ Identify key findings
│  └─ ✅ Phase 2a 100% complete by 4pm
│
└─ ✅ PHASE 2a COMPLETE
   └─ 1,250,000 simulations executed
   └─ 125 scenarios analyzed
   └─ 9+ visualization charts generated
   └─ Parameter sensitivity quantified
```

### **PHASE 2b: ONE-WAY SENSITIVITY ANALYSIS (Week 5 MON-WED, 10 hours)**

**Monday-Wednesday: Jun 30 - Jul 02 (10 hours)**

```
MON Jun 30 (3.5h):
├─ One-Way Analysis: Bankroll Variation
│  ├─ Run high-resolution sweep: $100-$5000 in $100 steps
│  │  └─ 50 parameter points × 5k simulations = 250k samples
│  ├─ Record: EV, Std Dev, Ruin Prob, Max Loss, Max Win
│  ├─ Fit regression: EV = f(Bankroll) [should be ~0]
│  ├─ Test hypothesis: EV independent of bankroll
│  ├─ Generate curve plot with 95% CI bands
│  └─ ✅ Analysis complete by 10:30am
│
├─ One-Way Analysis: Bet Amount Variation
│  ├─ Run high-resolution sweep: $1-$500 in $5 steps
│  │  └─ 100 parameter points × 2.5k simulations = 250k samples
│  ├─ Record: EV, Std Dev, Ruin Prob, Max Loss, Max Win
│  ├─ Fit regression: EV = f(Bet) [should be linear: -0.27 × Bet]
│  ├─ Test hypothesis: EV scales linearly with bet
│  ├─ Generate curve plot with 95% CI bands
│  └─ ✅ Analysis complete by 1:30pm
│
├─ Preliminary Findings (1:30pm-3:30pm)
│  ├─ Document one-way elasticities
│  ├─ Calculate sensitivity coefficients
│  ├─ Identify parameter impacts
│  └─ ✅ Status: ON SCHEDULE
│
└─ Progress: 500k additional simulations

TUE Jul 01 (3.5h):
├─ One-Way Analysis: Spins per Session Variation
│  ├─ Run high-resolution sweep: 10-5000 spins in log scale
│  │  └─ 50 parameter points × 5k simulations = 250k samples
│  ├─ Record: EV, Std Dev, Ruin Prob, Max Loss, Max Win
│  ├─ Fit regression: StdDev = f(Spins) [should be sqrt(Spins)]
│  ├─ Test hypothesis: Std dev scales with sqrt(spins)
│  ├─ Generate log-log plot for better visibility
│  └─ ✅ Analysis complete by 10:30am
│
├─ One-Way Analysis: Betting Strategy Variants
│  ├─ Constant bet ($10) vs fixed-fraction bet (1% of bankroll)
│  ├─ Run 50k simulations each
│  ├─ Compare EV, volatility, ruin probability
│  ├─ Test which strategy is superior
│  └─ ✅ Analysis complete by 1:30pm
│
├─ One-Way Summary Table (1:30pm-3:30pm)
│  ├─ Create comprehensive one-way sensitivity table
│  ├─ Document elasticities
│  ├─ List critical thresholds
│  └─ ✅ Table complete
│
└─ Progress: 750k additional simulations

WED Jul 02 (3h):
├─ One-Way Visualization Suite (8am-11am)
│  ├─ Generate high-resolution plots for all 4 parameters
│  ├─ Add sensitivity coefficients to plots
│  ├─ Add confidence band regions
│  ├─ Add theoretical curves (where applicable)
│  ├─ Format for stakeholder presentation
│  └─ ✅ All visualizations complete by 11am
│
├─ Cross-Parameter Interaction Check (11am-12pm)
│  ├─ Identify any non-linear interactions
│  ├─ Flag synergistic effects
│  ├─ Note if one-way analysis sufficient
│  └─ ✅ Interaction analysis complete
│
├─ Phase 2b Documentation (12pm-1pm)
│  ├─ Compile one-way sensitivity report
│  ├─ Include all plots and tables
│  ├─ Draw preliminary conclusions
│  └─ ✅ Report complete
│
└─ ✅ PHASE 2b COMPLETE
   └─ Total additional simulations: 1,250,000
   └─ 4 one-way sensitivity analyses
   └─ ~200 visualization charts
   └─ Complete elasticity report
```

### **PHASE 2c: TWO-WAY SENSITIVITY ANALYSIS (Week 5 THU-FRI, 10 hours)**

**Thursday-Friday: Jul 03-04 (10 hours)**

```
THU Jul 03 (5h):
├─ Two-Way Analysis: Bankroll × Bet Amount
│  ├─ Matrix: 20 bankroll values × 20 bet values
│  │  └─ 400 combinations × 2.5k simulations = 1,000k samples
│  ├─ Record: EV for each combination
│  ├─ Generate 2D heatmap (EV values)
│  ├─ Generate contour plot (EV iso-lines)
│  ├─ Calculate interaction coefficient
│  └─ ✅ Analysis complete by 10am
│
├─ Two-Way Analysis: Bet Amount × Spins
│  ├─ Matrix: 15 bet values × 15 spins values
│  │  └─ 225 combinations × 4k simulations = 900k samples
│  ├─ Record: Volatility (Std Dev) for each combination
│  ├─ Generate 2D heatmap (Volatility values)
│  ├─ Generate contour plot (Risk iso-lines)
│  ├─ Identify sweet spots for risk/reward
│  └─ ✅ Analysis complete by 2:30pm
│
├─ Data Validation & Quality Check (2:30pm-4pm)
│  ├─ Verify all 625 two-way combinations executed
│  ├─ Check for execution errors
│  ├─ Validate convergence for each point
│  ├─ Backup complete 2-way results
│  └─ ✅ All validations pass
│
├─ Preliminary Insights (4pm-5pm)
│  ├─ Document interaction effects
│  ├─ Identify synergies and conflicts
│  ├─ Note any surprising findings
│  └─ ✅ Insights compiled
│
└─ Progress: 1,900k additional simulations

FRI Jul 04 (5h):
├─ Two-Way Analysis: Bankroll × Spins
│  ├─ Matrix: 20 bankroll values × 20 spins values
│  │  └─ 400 combinations × 2.5k simulations = 1,000k samples
│  ├─ Record: Ruin probability for each combination
│  ├─ Generate 2D heatmap (Ruin probability)
│  ├─ Identify safe zones vs danger zones
│  ├─ Generate risk matrix for decision-making
│  └─ ✅ Analysis complete by 10am
│
├─ Interactive Heatmap Suite (10am-12pm)
│  ├─ Create 3 interactive heatmaps (web-friendly)
│  ├─ Add hover-over value display
│  ├─ Add slider controls for exploration
│  ├─ Include sensitivity scale on axes
│  └─ ✅ Interactive suite complete
│
├─ Two-Way Summary Report (12pm-2pm)
│  ├─ Compile two-way sensitivity report
│  ├─ Include all heatmaps and contour plots
│  ├─ Document interaction effects found
│  ├─ Provide decision matrices
│  └─ ✅ Report complete
│
├─ Phase 2 Synthesis & Conclusions (2pm-4pm)
│  ├─ Compare 1-way vs 2-way results
│  ├─ Identify most impactful parameters
│  ├─ Rank parameters by importance
│  ├─ Draw overall conclusions
│  ├─ Prepare for Phase 3 (Risk Validation)
│  └─ ✅ Synthesis complete
│
├─ Phase 2 Final Sign-off (4pm-5pm)
│  ├─ Archive all results (1,900k+ simulations)
│  ├─ Backup sensitivity analysis reports
│  ├─ Create executive summary
│  └─ ✅ Phase 2 officially complete
│
└─ ✅ PHASE 2c COMPLETE
   └─ Total additional simulations: 1,900,000
   └─ 625 two-way parameter combinations
   └─ 6+ major heatmaps generated
   └─ Full interaction effects documented
```

---

## 📊 PHASE 2 TOTAL SIMULATION VOLUME

```
Phase 2a: Parameter Grid ..................... 1,250,000 samples
Phase 2b: One-Way Sensitivity ............... 1,250,000 samples
Phase 2c: Two-Way Sensitivity ............... 1,900,000 samples
────────────────────────────────────────────────────────────
TOTAL PHASE 2 SIMULATIONS ................... 4,400,000 samples

Plus baseline from Phase 1 ..................... 200,000 samples
────────────────────────────────────────────────────────────
CUMULATIVE TOTAL (Phase 1-2) ................ 4,600,000 samples
```

---

## 📈 EXPECTED FINDINGS

### **Parameter Sensitivity Hypotheses**

```
Bankroll:
├─ Expected EV: Independent (house edge doesn't change)
├─ Expected Impact: ↔ No effect on EV
├─ Risk Effect: Larger bankroll → lower ruin probability
└─ Importance: CRITICAL (for risk management)

Bet Amount:
├─ Expected EV: Linear scaling (-0.27 × bet amount)
├─ Expected Impact: ↑↓ Direct proportional
├─ Risk Effect: Larger bets → higher volatility
└─ Importance: CRITICAL (primary leverage point)

Spins per Session:
├─ Expected EV: Independent (house edge doesn't change)
├─ Expected Impact: ↔ No effect on EV
├─ Std Dev Impact: Scales with sqrt(spins)
└─ Importance: HIGH (for convergence study)
```

---

## ✅ PHASE 2 SUCCESS CRITERIA

```
Execution:
✅ 4,400,000+ simulations executed (no execution errors)
✅ 125 parameter scenarios tested
✅ All 625 two-way combinations tested
✅ Zero critical failures
✅ All results archived & validated

Quality:
✅ Convergence achieved for all runs
✅ Results consistent with Phase 1 baseline
✅ All heatmaps generated and reviewed
✅ Sensitivity coefficients calculated

Analysis:
✅ Parameter rankings complete
✅ Interaction effects documented
✅ Risk matrices generated
✅ Decision guidance provided

Documentation:
✅ Sensitivity analysis report complete
✅ 200+ visualization charts
✅ Executive summary prepared
✅ Phase 2 sign-off document ready
```

---

## 🚀 PHASE 2 READINESS CHECKLIST

**Pre-Phase 2 Verification:**
- ✅ Phase 1 baseline (200k) validated
- ✅ Parameter ranges defined
- ✅ Simulation framework ready
- ✅ Output directories configured
- ✅ Monitoring system in place
- ✅ Team briefed & trained

**Status: READY TO EXECUTE**

---

## 📞 TEAM ASSIGNMENTS

```
Phase 2 Execution:
├─ Data Scientist: Parameter definition & analysis
├─ Python Engineer: Simulation execution & optimization
├─ Analytics: Visualization & reporting
└─ Project Manager: Timeline & coordination
```

---

## 📋 DELIVERABLES

**Phase 2 Outputs:**
```
✅ Parameter Grid Results (125 scenarios)
✅ One-Way Sensitivity Report (4 parameters)
✅ Two-Way Sensitivity Heatmaps (3 matrices)
✅ Sensitivity Coefficient Table
✅ Interactive Heatmap Suite
✅ Executive Summary Report
✅ Risk Decision Matrices
✅ Phase 2 Sign-off Certificate
```

---

**Phase 2 Status: READY FOR EXECUTION**  
**Scheduled Start:** Sunday Jun 23, 2026 (after Ciclo 7 Phase 2b UAT)  
**Phase 2 Complete:** Friday Jul 04, 2026  
**Next Phase:** Phase 3 Risk Model Validation (Jul 05+)

