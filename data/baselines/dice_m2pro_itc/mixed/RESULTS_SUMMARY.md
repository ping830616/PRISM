# DICE Full Retrain Results

## Setup
- Feature profile: mixed ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_core_5hz.csv', 'tier2': 'tier2_core_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=45, alpha=0.1, persist_k=1, gain=0.2
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
          mixed             tier0       24          46          2.264059   0.8125 0.940232         1.0        1.0            0.0           0.40              0.008992              0.018790                      0.0                 0.010056
          mixed       tier0_tier1       24          57          2.781141   0.8375 0.957016         1.0        1.0            0.0           0.75              0.000044              0.000108                      0.0                 0.000052
          mixed tier0_tier1_tier2       24          64          3.090461   0.8500 0.959180         1.0        1.0            0.0           0.75              0.000046              0.000116                      0.0                 0.000057
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
          mixed   ATOMIC   0.8125 0.804167         1.0        1.0          0.000046          0.000093                  0.0             0.000048       1.997535      0.000047         49.082329         0.000048
          mixed   BRANCH   0.9375 0.950000         1.0        1.0          0.000046          0.000180                  0.0             0.000125       3.831216      0.000134        126.248362         0.000125
          mixed    CACHE   0.8125 0.804167         1.0        1.0          0.000046          0.000096                  0.0             0.000056       2.056098      0.000050         56.790682         0.000056
          mixed    MEMBW   0.9375 0.950000         1.0        1.0          0.000046          0.000156                  0.0             0.000089       3.320313      0.000110         90.268587         0.000089
          mixed      TLB   0.7500 0.679167         1.0        1.0          0.000046          0.000108                  0.0             0.000052       2.307380      0.000062         53.068448         0.000052
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.8375**
- Base score mean stressor ROC-AUC (all five): **0.8500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.8528**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.8542**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.238961               0.026874                 0.019659           mixed
      tier0_tier1       20      0.40      0.70          0.40  0.347863               0.018287                 0.012528           mixed
tier0_tier1_tier2       20      0.55      0.75          0.55  0.573260               0.016891                 0.015736           mixed
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.55          0.30  0.268759               0.012067                 0.009172           mixed
      tier0_tier1       20      0.10      0.25          0.10  0.057143               0.091171                 0.052458           mixed
tier0_tier1_tier2       20      0.15      0.45          0.15  0.136364               0.083148                 0.030023           mixed
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.30      0.70          0.30  0.284444               0.015321                 0.009909           mixed
      tier0_tier1       20      0.40      0.65          0.40  0.386061               0.014429                 0.008773           mixed
tier0_tier1_tier2       20      0.25      0.65          0.25  0.235556               0.011835                 0.010561           mixed
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.6      0.80      0.500000  0.421818               0.034267                 0.035943           mixed
      tier0_tier1       20       0.5      0.75      0.444444  0.356745               0.025808                 0.030215           mixed
tier0_tier1_tier2       20       0.5      0.75      0.500000  0.449084               0.025957                 0.027414           mixed
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20       0.4      0.60        0.50           0.4  0.333333      0.45          0.55            0.444444            0.555556                0.400000            0.293333              -0.009565                 0.001601            0.016105              0.015766           0.012014        0.067853           mixed
      tier0_tier1       20       0.3      0.65        0.40           0.3  0.280000      0.60          0.40            0.416667            0.666667                0.366667            0.388889              -0.000582                 0.000254            0.022480              0.023535           0.015606        0.020231           mixed
tier0_tier1_tier2       20       0.5      0.75        0.35           0.5  0.462424      0.55          0.45            0.727273            0.909091                0.700000            0.660000               0.007098                 0.003656            0.020506              0.016412           0.018037        0.056829           mixed
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.35      0.65        0.50          0.35  0.337013       0.5           0.5            0.300000            0.500000                0.200000            0.190476              -0.018978                -0.000980            0.016105              0.015766           0.012014       -0.035413           mixed
      tier0_tier1       20      0.25      0.35        0.40          0.25  0.165714       0.6           0.4            0.333333            0.416667                0.333333            0.220000              -0.056140                -0.019060            0.022480              0.023535           0.015606       -0.103431           mixed
tier0_tier1_tier2       20      0.20      0.45        0.35          0.20  0.168889       0.5           0.5            0.100000            0.300000                0.100000            0.080000               0.041013                 0.005616            0.020506              0.016412           0.018037        0.087501           mixed
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      11      0.55          0.45            0.454545            0.636364                0.400000            0.310000           mixed
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.500000            0.625000                0.500000            0.293333           mixed
            tier0    trained              0.067853       7      0.35          0.65            0.571429            0.571429                0.500000            0.320000           mixed
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.500000                0.500000            0.293333           mixed
            tier0  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.20              0.200000       3      0.15          0.85            0.666667            0.666667                0.500000            0.160000           mixed
            tier0  conf_0.25              0.250000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
      tier0_tier1  conf_0.00              0.000000      13      0.65          0.35            0.384615            0.615385                0.395833            0.335556           mixed
      tier0_tier1    trained              0.020231       8      0.40          0.60            0.250000            0.500000                0.166667            0.088889           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.500000                0.250000            0.066667           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.500000                0.250000            0.066667           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.400000                0.333333            0.066667           mixed
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.500000            0.500000                0.500000            0.133333           mixed
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.562500            0.750000                0.483333            0.502424           mixed
tier0_tier1_tier2  conf_0.05              0.050000       7      0.35          0.65            0.428571            0.714286                0.444444            0.200000           mixed
tier0_tier1_tier2    trained              0.056829       7      0.35          0.65            0.428571            0.714286                0.444444            0.200000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       6      0.30          0.70            0.500000            0.666667                0.444444            0.214286           mixed
tier0_tier1_tier2  conf_0.15              0.150000       5      0.25          0.75            0.400000            0.600000                0.333333            0.114286           mixed
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.200000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.035413      11      0.55          0.45            0.272727            0.545455                0.200000            0.190476           mixed
            tier0  conf_0.00              0.000000      10      0.50          0.50            0.300000            0.500000                0.200000            0.190476           mixed
            tier0  conf_0.05              0.050000       7      0.35          0.65            0.285714            0.428571                0.300000            0.213333           mixed
            tier0  conf_0.10              0.100000       5      0.25          0.75            0.400000            0.600000                0.375000            0.233333           mixed
            tier0  conf_0.15              0.150000       2      0.10          0.90            0.500000            1.000000                0.500000            0.200000           mixed
            tier0  conf_0.20              0.200000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
            tier0  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN           mixed
      tier0_tier1    trained             -0.103431      11      0.55          0.45            0.272727            0.363636                0.250000            0.120000           mixed
      tier0_tier1  conf_0.00              0.000000       9      0.45          0.55            0.111111            0.222222                0.250000            0.066667           mixed
      tier0_tier1  conf_0.05              0.050000       6      0.30          0.70            0.166667            0.166667                0.250000            0.080000           mixed
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.166667            0.166667                0.250000            0.080000           mixed
      tier0_tier1  conf_0.15              0.150000       5      0.25          0.75            0.200000            0.200000                0.250000            0.080000           mixed
      tier0_tier1  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000           mixed
      tier0_tier1  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.00              0.000000      13      0.65          0.35            0.076923            0.307692                0.066667            0.057143           mixed
tier0_tier1_tier2  conf_0.05              0.050000       9      0.45          0.55            0.000000            0.333333                0.000000            0.000000           mixed
tier0_tier1_tier2    trained              0.087501       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.10              0.100000       8      0.40          0.60            0.000000            0.250000                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.15              0.150000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.20              0.200000       7      0.35          0.65            0.000000            0.285714                0.000000            0.000000           mixed
tier0_tier1_tier2  conf_0.25              0.250000       6      0.30          0.70            0.000000            0.333333                0.000000            0.000000           mixed
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.30      0.55      0.300000  0.238961               0.026874                 0.019659           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.40      0.70      0.400000  0.347863               0.018287                 0.012528           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.75      0.550000  0.573260               0.016891                 0.015736           mixed    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.30      0.55      0.300000  0.268759               0.012067                 0.009172           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.10      0.25      0.100000  0.057143               0.091171                 0.052458           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.15      0.45      0.150000  0.136364               0.083148                 0.030023           mixed    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.40      0.60      0.400000  0.333333              -0.009565                 0.001601           mixed     hierarchical         whole_run        0.50      0.45          0.55            0.444444            0.555556                0.400000            0.293333            0.016105              0.015766           0.012014        0.067853                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.30      0.65      0.300000  0.280000              -0.000582                 0.000254           mixed     hierarchical         whole_run        0.40      0.60          0.40            0.416667            0.666667                0.366667            0.388889            0.022480              0.023535           0.015606        0.020231                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.462424               0.007098                 0.003656           mixed     hierarchical         whole_run        0.35      0.55          0.45            0.727273            0.909091                0.700000            0.660000            0.020506              0.016412           0.018037        0.056829                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.35      0.65      0.350000  0.337013              -0.018978                -0.000980           mixed     hierarchical post_alert_window        0.50      0.50          0.50            0.300000            0.500000                0.200000            0.190476            0.016105              0.015766           0.012014       -0.035413                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.35      0.250000  0.165714              -0.056140                -0.019060           mixed     hierarchical post_alert_window        0.40      0.60          0.40            0.333333            0.416667                0.333333            0.220000            0.022480              0.023535           0.015606       -0.103431                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.45      0.200000  0.168889               0.041013                 0.005616           mixed     hierarchical post_alert_window        0.35      0.50          0.50            0.100000            0.300000                0.100000            0.080000            0.020506              0.016412           0.018037        0.087501                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.60      0.80      0.500000  0.421818               0.034267                 0.035943           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.50      0.75      0.444444  0.356745               0.025808                 0.030215           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.50      0.75      0.500000  0.449084               0.025957                 0.027414           mixed     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN           mixed       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.699158         0.148379     0.152463              tier0           mixed
  BRANCH     0.763807         0.090778     0.145416              tier0           mixed
   CACHE     0.540196         0.354105     0.105700              tier0           mixed
   MEMBW     0.781800         0.096912     0.121288              tier0           mixed
     TLB     0.701943         0.142727     0.155330              tier0           mixed
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.264215         0.401388             0.092819                 0.208222                 0.033357           mixed
  BRANCH               memory_io       0.243988         0.465668             0.051019                 0.193696                 0.045628           mixed
   CACHE               memory_io       0.467322         0.274844             0.069098                 0.139313                 0.049424           mixed
   MEMBW               memory_io       0.232873         0.485260             0.057354                 0.166322                 0.058191           mixed
     TLB               memory_io       0.300270         0.400358             0.078216                 0.192555                 0.028601           mixed
```

## Supervised Diagnosis
- This path is intended for expanded anomaly sets with repeated runs per workload-stressor pair. It is skipped automatically until each stressor has enough samples.
```text
           config                       status  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  min_class_count  min_group_count    group_key  include_workload feature_profile
            tier0 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
      tier0_tier1 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
tier0_tier1_tier2 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1           mixed
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    0.0                             0.0                           0.0                 0.40                     45.0                 669.4                0.25                0.25                 0.3           mixed
      tier0_tier1                    0.0                             0.0                           0.0                 0.75                     84.0                 860.4                0.40                0.40                 0.6           mixed
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.75                     45.0                 540.4                0.45                0.45                 0.7           mixed
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full/figures/fig_detection_latency.png`
