# DICE Full Retrain Results

## Setup
- Feature profile: full ({'tier0': 'tier0_full_5hz.csv', 'tier1_alt': 'tier1_alt_full_5hz.csv', 'tier2': 'tier2_full_5hz.csv'})
- Protocol: global, benign-only fit/calibration, block_B=90, alpha=0.05, persist_k=2, gain=0.35
- Case inventory: 24 runs across 24 workload-stressor bases.

## Overall
```text
feature_profile            config  n_cases  n_features  fit_eval_seconds  roc_auc   pr_auc  roc_auc_wc  pr_auc_wc  fpr_run_alert  tpr_run_alert  median_nominal_score  median_anomaly_score  median_nominal_score_wc  median_anomaly_score_wc
           full             tier0       24          46          2.114367   0.8000 0.931899         1.0        1.0            0.0           0.30              0.004903              0.010882                      0.0                 0.006095
           full       tier0_tier1       24          64          2.875719   0.7875 0.941423         1.0        1.0            0.0           0.55              0.006950              0.023013                      0.0                 0.010584
           full tier0_tier1_tier2       24          75          3.353361   0.9500 0.989710         1.0        1.0            0.0           0.95              0.002875              0.008226                      0.0                 0.004469
```

## Final Config Stressors
```text
feature_profile stressor  roc_auc  pr_auc  roc_auc_wc  pr_auc_wc  median_neg_score  median_pos_score  median_neg_score_wc  median_pos_score_wc  pos_neg_ratio  pos_neg_diff  pos_neg_ratio_wc  pos_neg_diff_wc
           full   ATOMIC   0.9375  0.9500         1.0        1.0          0.002875          0.007733                  0.0             0.003713       2.689363      0.004858       3714.439196         0.003713
           full   BRANCH   1.0000  1.0000         1.0        1.0          0.002875          0.008158                  0.0             0.005779       2.837035      0.005283       5779.588714         0.005779
           full    CACHE   0.9375  0.9500         1.0        1.0          0.002875          0.010061                  0.0             0.006662       3.498900      0.007187       6663.487102         0.006662
           full    MEMBW   1.0000  1.0000         1.0        1.0          0.002875          0.008854                  0.0             0.005351       3.078885      0.005979       5352.468850         0.005351
           full      TLB   0.8750  0.8875         1.0        1.0          0.002875          0.006510                  0.0             0.004256       2.263995      0.003635       4256.838756         0.004256
```

## Paper-style Aggregates (Final Config)
- Base score mean stressor AUC-PR (all five): **0.9575**
- Base score mean stressor ROC-AUC (all five): **0.9500**
- WC score mean stressor AUC-PR (all five): **1.0000**
- WC score mean stressor ROC-AUC (all five): **1.0000**
- Base score mean stressor AUC-PR (excluding BRANCH/TLB): **0.9667**
- Base score mean stressor ROC-AUC (excluding BRANCH/TLB): **0.9583**
- WC score mean stressor AUC-PR (excluding BRANCH/TLB): **1.0000**
- WC score mean stressor ROC-AUC (excluding BRANCH/TLB): **1.0000**

## Diagnosis
- Feature-level diagnosis uses normalized whole-run residual-attribution prototypes as the default paper-facing result, with diagnosis-only filtering that removes monotonic counters and downweights generic memory-state features.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.4       0.6           0.4  0.322424               0.025262                 0.016051            full
      tier0_tier1       20       0.2       0.3           0.2  0.185714               0.013704                 0.011986            full
tier0_tier1_tier2       20       0.3       0.4           0.3  0.200000               0.025312                 0.019305            full
```

- Post-alert-window diagnosis is exported below as a side-by-side comparison; it uses windows immediately after the first alert/persistent alert and applies the same diagnosis-only filtering and downweighting.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.15      0.65          0.15  0.141538               0.016186                 0.015828            full
      tier0_tier1       20      0.20      0.40          0.20  0.187912               0.021122                 0.023497            full
tier0_tier1_tier2       20      0.20      0.35          0.20  0.203175               0.018322                 0.016525            full
```

- Mechanism-level diagnosis uses normalized mechanism centroids over workload-held residual summaries.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20       0.3      0.75           0.3  0.297143               0.015336                 0.013444            full
      tier0_tier1       20       0.2      0.55           0.2  0.152727               0.021631                 0.018504            full
tier0_tier1_tier2       20       0.3      0.55           0.3  0.248889               0.014276                 0.007649            full
```

- Family-level diagnosis relaxes the label space from exact stressors to mechanism families while keeping the whole-run residual-attribution representation.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile
            tier0       20      0.55      0.75      0.472222  0.398551               0.035112                 0.036276            full
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024465                 0.029432            full
tier0_tier1_tier2       20      0.55      0.95      0.638889  0.542328               0.019050                 0.015745            full
```

## Hierarchical Diagnosis
- High-confidence diagnosis adds a mechanism-family gate and abstains on low-confidence cases; whole-run attribution is the default input.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.25      0.60         0.4          0.25  0.205253      0.40          0.60            0.375000            0.750000                0.333333            0.240000               0.002409                 0.011835            0.014217              0.010873           0.010475        0.101878            full
      tier0_tier1       20      0.20      0.35         0.5          0.20  0.204286      0.55          0.45            0.090909            0.181818                0.066667            0.066667               0.001778                 0.003442            0.023535              0.024354           0.013681        0.004012            full
tier0_tier1_tier2       20      0.25      0.40         0.4          0.25  0.175000      0.60          0.40            0.250000            0.416667                0.333333            0.188889               0.011944                 0.016606            0.020081              0.016017           0.006790        0.079642            full
```

## Hierarchical Diagnosis (Post-Alert Window)
- This comparison uses the same gate on post-alert-window attribution rather than whole-run attribution.
```text
           config  n_cases  top1_acc  top2_acc  family_acc  balanced_acc  macro_f1  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_margin_to_second  median_margin_to_second  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau feature_profile
            tier0       20      0.20      0.60         0.4          0.20  0.163333      0.70          0.30            0.214286            0.642857                0.200000            0.157143              -0.006942                 0.005512            0.014217              0.010873           0.010475       -0.057800            full
      tier0_tier1       20      0.25      0.45         0.5          0.25  0.258205      0.55          0.45            0.272727            0.454545                0.266667            0.266667              -0.008678                 0.002459            0.023535              0.024354           0.013681        0.022198            full
tier0_tier1_tier2       20      0.30      0.45         0.4          0.30  0.266667      0.75          0.25            0.266667            0.400000                0.266667            0.240000              -0.002136                -0.000448            0.020081              0.016017           0.006790       -0.114092            full
```

## Hierarchical Abstain Sweep
- The sweep below shows how selective diagnosis improves as the confidence gate becomes stricter.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0  conf_0.00              0.000000      12      0.60          0.40            0.333333            0.583333                0.333333            0.203175            full
            tier0  conf_0.05              0.050000      12      0.60          0.40            0.333333            0.583333                0.333333            0.203175            full
            tier0  conf_0.10              0.100000       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286            full
            tier0    trained              0.101878       6      0.30          0.70            0.333333            0.500000                0.166667            0.114286            full
            tier0  conf_0.15              0.150000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.20              0.200000       4      0.20          0.80            0.500000            0.750000                0.333333            0.133333            full
            tier0  conf_0.25              0.250000       3      0.15          0.85            0.666667            0.666667                0.666667            0.160000            full
      tier0_tier1  conf_0.00              0.000000      14      0.70          0.30            0.142857            0.214286                0.133333            0.133333            full
      tier0_tier1    trained              0.004012      14      0.70          0.30            0.142857            0.214286                0.133333            0.133333            full
      tier0_tier1  conf_0.05              0.050000       9      0.45          0.55            0.111111            0.222222                0.100000            0.080000            full
      tier0_tier1  conf_0.10              0.100000       6      0.30          0.70            0.000000            0.166667                0.000000            0.000000            full
      tier0_tier1  conf_0.15              0.150000       4      0.20          0.80            0.000000            0.250000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
tier0_tier1_tier2  conf_0.00              0.000000      16      0.80          0.20            0.250000            0.375000                0.250000            0.172308            full
tier0_tier1_tier2  conf_0.05              0.050000      13      0.65          0.35            0.307692            0.384615                0.250000            0.200000            full
tier0_tier1_tier2    trained              0.079642      10      0.50          0.50            0.300000            0.400000                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.10              0.100000      10      0.50          0.50            0.300000            0.400000                0.200000            0.109091            full
tier0_tier1_tier2  conf_0.15              0.150000       6      0.30          0.70            0.166667            0.166667                0.200000            0.066667            full
tier0_tier1_tier2  conf_0.20              0.200000       4      0.20          0.80            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2  conf_0.25              0.250000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
```

## Hierarchical Abstain Sweep (Post-Alert Window)
- This comparison applies the same sweep to post-alert-window attribution.
```text
           config gate_label  confidence_threshold  n_kept  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1 feature_profile
            tier0    trained             -0.057800      14      0.70          0.30            0.214286            0.642857                0.200000            0.157143            full
            tier0  conf_0.00              0.000000      13      0.65          0.35            0.153846            0.615385                0.166667            0.123810            full
            tier0  conf_0.05              0.050000       8      0.40          0.60            0.125000            0.375000                0.100000            0.100000            full
            tier0  conf_0.10              0.100000       8      0.40          0.60            0.125000            0.375000                0.100000            0.100000            full
            tier0  conf_0.15              0.150000       7      0.35          0.65            0.142857            0.285714                0.100000            0.100000            full
            tier0  conf_0.20              0.200000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
            tier0  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.00              0.000000      12      0.60          0.40            0.250000            0.500000                0.266667            0.257143            full
      tier0_tier1    trained              0.022198      10      0.50          0.50            0.200000            0.400000                0.200000            0.166667            full
      tier0_tier1  conf_0.05              0.050000       7      0.35          0.65            0.142857            0.428571                0.200000            0.100000            full
      tier0_tier1  conf_0.10              0.100000       7      0.35          0.65            0.142857            0.428571                0.200000            0.100000            full
      tier0_tier1  conf_0.15              0.150000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.20              0.200000       2      0.10          0.90            0.000000            0.000000                0.000000            0.000000            full
      tier0_tier1  conf_0.25              0.250000       1      0.05          0.95            0.000000            0.000000                0.000000            0.000000            full
tier0_tier1_tier2    trained             -0.114092      17      0.85          0.15            0.294118            0.411765                0.333333            0.294286            full
tier0_tier1_tier2  conf_0.00              0.000000      10      0.50          0.50            0.300000            0.400000                0.300000            0.333333            full
tier0_tier1_tier2  conf_0.05              0.050000       5      0.25          0.75            0.600000            0.600000                0.625000            0.500000            full
tier0_tier1_tier2  conf_0.10              0.100000       4      0.20          0.80            0.500000            0.500000                0.500000            0.300000            full
tier0_tier1_tier2  conf_0.15              0.150000       3      0.15          0.85            0.666667            0.666667                0.750000            0.333333            full
tier0_tier1_tier2  conf_0.20              0.200000       2      0.10          0.90            1.000000            1.000000                1.000000            0.400000            full
tier0_tier1_tier2  conf_0.25              0.250000       0      0.00          1.00                 NaN                 NaN                     NaN                 NaN            full
```

## Diagnosis Mode Comparison
- Whole-run and post-alert-window diagnosis are exported together so the diagnosis mode can be evaluated directly.
```text
           config  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  mean_margin_to_second  median_margin_to_second feature_profile diagnosis_target    diagnosis_mode  family_acc  coverage  abstain_rate  selective_top1_acc  selective_top2_acc  selective_balanced_acc  selective_macro_f1  mean_family_margin  median_family_margin  family_margin_tau  confidence_tau                       status  min_class_count  min_group_count    group_key  include_workload
            tier0       20      0.40      0.60      0.400000  0.322424               0.025262                 0.016051            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.30      0.200000  0.185714               0.013704                 0.011986            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.40      0.300000  0.200000               0.025312                 0.019305            full    feature_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.15      0.65      0.150000  0.141538               0.016186                 0.015828            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.40      0.200000  0.187912               0.021122                 0.023497            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.20      0.35      0.200000  0.203175               0.018322                 0.016525            full    feature_level post_alert_window         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.25      0.60      0.250000  0.205253               0.002409                 0.011835            full     hierarchical         whole_run         0.4      0.40          0.60            0.375000            0.750000                0.333333            0.240000            0.014217              0.010873           0.010475        0.101878                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.20      0.35      0.200000  0.204286               0.001778                 0.003442            full     hierarchical         whole_run         0.5      0.55          0.45            0.090909            0.181818                0.066667            0.066667            0.023535              0.024354           0.013681        0.004012                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.25      0.40      0.250000  0.175000               0.011944                 0.016606            full     hierarchical         whole_run         0.4      0.60          0.40            0.250000            0.416667                0.333333            0.188889            0.020081              0.016017           0.006790        0.079642                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.20      0.60      0.200000  0.163333              -0.006942                 0.005512            full     hierarchical post_alert_window         0.4      0.70          0.30            0.214286            0.642857                0.200000            0.157143            0.014217              0.010873           0.010475       -0.057800                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.25      0.45      0.250000  0.258205              -0.008678                 0.002459            full     hierarchical post_alert_window         0.5      0.55          0.45            0.272727            0.454545                0.266667            0.266667            0.023535              0.024354           0.013681        0.022198                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.30      0.45      0.300000  0.266667              -0.002136                -0.000448            full     hierarchical post_alert_window         0.4      0.75          0.25            0.266667            0.400000                0.266667            0.240000            0.020081              0.016017           0.006790       -0.114092                          NaN              NaN              NaN          NaN               NaN
            tier0       20      0.55      0.75      0.472222  0.398551               0.035112                 0.036276            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
      tier0_tier1       20      0.45      0.75      0.361111  0.305463               0.024465                 0.029432            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
tier0_tier1_tier2       20      0.55      0.95      0.638889  0.542328               0.019050                 0.015745            full     family_level         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN                          NaN              NaN              NaN          NaN               NaN
            tier0       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
      tier0_tier1       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
tier0_tier1_tier2       20       NaN       NaN           NaN       NaN                    NaN                      NaN            full       supervised         whole_run         NaN       NaN           NaN                 NaN                 NaN                     NaN                 NaN                 NaN                   NaN                NaN             NaN skipped_insufficient_samples              4.0              4.0 base_case_id               1.0
```

## Final Config Tier Contribution Summary
```text
stressor  tier0_share  tier1_alt_share  tier2_share dominant_tier_mode feature_profile
  ATOMIC     0.621365         0.266699     0.111935              tier0            full
  BRANCH     0.651864         0.217645     0.130490              tier0            full
   CACHE     0.524250         0.209631     0.266120              tier0            full
   MEMBW     0.663732         0.237702     0.098566              tier0            full
     TLB     0.597877         0.277747     0.124376              tier0            full
```

## Final Config Mechanism Summary
```text
stressor dominant_mechanism_mode  compute_share  memory_io_share  thermal_power_share  scheduler_runtime_share  platform_pressure_share feature_profile
  ATOMIC               memory_io       0.327209         0.334459             0.097073                 0.122251                 0.119008            full
  BRANCH               memory_io       0.294700         0.398598             0.070525                 0.148255                 0.087923            full
   CACHE                 compute       0.448885         0.322490             0.062213                 0.090291                 0.076122            full
   MEMBW               memory_io       0.300791         0.376469             0.091178                 0.118479                 0.113083            full
     TLB               memory_io       0.325175         0.354801             0.100023                 0.121594                 0.098407            full
```

## Supervised Diagnosis
- This path is intended for expanded anomaly sets with repeated runs per workload-stressor pair. It is skipped automatically until each stressor has enough samples.
```text
           config                       status  n_cases  top1_acc  top2_acc  balanced_acc  macro_f1  min_class_count  min_group_count    group_key  include_workload feature_profile
            tier0 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
      tier0_tier1 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
tier0_tier1_tier2 skipped_insufficient_samples       20       NaN       NaN           NaN       NaN                4                4 base_case_id                 1            full
```

## Sequential Decisioning
```text
           config  benign_run_alert_rate  benign_persist_alerts_per_hour  benign_block_alerts_per_hour  anomaly_detect_rate  median_time_to_detect_s  p90_time_to_detect_s  detect_within_120s  detect_within_300s  detect_within_600s feature_profile
            tier0                    0.0                             0.0                           0.0                 0.30                     91.5                 688.5                 0.2                0.20                0.25            full
      tier0_tier1                    0.0                             0.0                           0.0                 0.55                     91.0                 836.0                 0.3                0.35                0.40            full
tier0_tier1_tier2                    0.0                             0.0                           0.0                 0.95                     91.0                 810.2                 0.6                0.60                0.70            full
```

## Files
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/overall_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/config_runtime_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/run_context.json`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/case_inventory.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/case_block_traces.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_metrics_final_config.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/sequential_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/case_diagnosis_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_family_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_feature_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_feature_diagnosis_runlevel_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_feature_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_feature_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_supervised_diagnosis_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_abstain_sweep.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_diagnosis_post_alert_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_abstain_sweep_post_alert.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_diagnosis_top_blocks_metrics.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_abstain_sweep_top_blocks.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/diagnosis_mode_comparison.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/mechanism_group_summary.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_family_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_supervised_confusion_matrix.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_tier_contributions.csv`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/overall_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_metrics_final_config.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/stressor_hierarchical_diagnosis_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/sequential_metrics.tex`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_roc_pr_by_config.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_roc_pr_by_config_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_run_score_boxplot.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_run_score_boxplot_wc.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_stressor_confusion_matrix.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_stressor_confusion_matrix_feature.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_stressor_confusion_matrix_feature_top_blocks.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_stressor_tier_contributions.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_mechanism_group_summary.png`
- `/Users/hsiaopingni/DICE/data generation/dataset/ITC_M2Pro_DATA/results_dice_full_full/figures/fig_detection_latency.png`
