"""Regenerate numerical paper tables from pinned analysis reports.

Adapted mechanically from canonical notebook Section 17E at 6289c4d.
This does not fit models or read telemetry. All writes go to output_dir.
"""
from pathlib import Path


def export_tables(repo_root, output_dir):
    REPO_ROOT = Path(repo_root).resolve()
    # Paper reproduction from pinned summaries; no raw data or model fitting.
    from statistics import NormalDist
    import hashlib
    import json
    import numpy as np
    import pandas as pd
    from scipy.stats import chi2
    def display(*args, **kwargs):
        pass

    def Markdown(text):
        return text

    MANUSCRIPT_ROOT = Path(output_dir)
    MANUSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)
    OPERATIONAL_SCORECARD = pd.read_csv(REPO_ROOT / "paper/results/development/table-9-operational-evidence-scorecard.csv")
    SCENARIO_COVERAGE = pd.read_csv(REPO_ROOT / "paper/results/development/table-10-scenario-detection-coverage.csv")
    MANUSCRIPT_SOURCES = REPO_ROOT / "paper/results/manuscript/sources"
    manifest = json.loads((MANUSCRIPT_SOURCES / "input-manifest.json").read_text(encoding="utf-8"))

    def require_paper(condition, message):
        if not condition:
            raise RuntimeError(f"Paper evidence mismatch: {message}")

    for relative, expected in manifest["bundled_sha256"].items():
        actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
        require_paper(actual == expected, relative)

    def read_paper_report(name):
        report = json.loads((MANUSCRIPT_SOURCES / name).read_text(encoding="utf-8"))
        require_paper(report.get("locked_test_accessed") is False, name)
        return report

    v2_paper = read_paper_report("v2-independent-confirmation.json")
    v3_paper = read_paper_report("v3-independent-confirmation.json")
    v3_development = read_paper_report("v3-development-selection.json")
    v3_selected = v3_development["selected"]
    require_paper(
        v3_paper["development_dataset_fingerprint"] == v3_development["dataset_fingerprint"],
        "v3 development fingerprint",
    )
    for revision, report in (("v2", v2_paper), ("v3", v3_paper)):
        protocol = REPO_ROOT / "configs" / f"{revision}-independent-confirmation.toml"
        plan = REPO_ROOT / "data" / f"{revision}-independent-confirmation-plan.csv"
        require_paper(hashlib.sha256(protocol.read_bytes()).hexdigest() == report["protocol_sha256"],
                      f"{revision} protocol fingerprint")
        require_paper(hashlib.sha256(plan.read_bytes()).hexdigest() == report["plan_sha256"],
                      f"{revision} plan fingerprint")
        require_paper(report["fit_or_tune_on_confirmation"] is False, f"{revision} evidence role")
        require_paper(report["candidate_count"] == 1, f"{revision} confirmation candidate count")

    require_paper(v3_development["development_g3_passed"] is True, "v3 development gate")
    require_paper(v3_selected["strict_platform_fold_g3"] is True, "v3 subgroup gates")
    require_paper(v2_paper["pooled_metrics"]["false_alerts"] == 17, "v2 episode count")
    require_paper(v3_paper["confirmation_passed"] is False, "v3 preserved confirmation")
    require_paper(v3_paper["eligible_for_locked_test"] is False, "reserved boundary")
    require_paper((v3_selected["detected"], v3_selected["runs"]) == (71, 120), "event counts")
    require_paper(v3_selected["false_alerts"] == 6, "development episode count")
    require_paper(np.isclose(v3_selected["benign_hours"], 36.53333333333333), "development exposure")
    require_paper(np.isclose(v3_selected["ttd"], 337.48666995798703), "conditional delay")
    require_paper(v3_selected["telemetry_fault_identification_rate"] == 1.0, "fault identification")

    original = pd.read_csv(MANUSCRIPT_SOURCES / "original-inventory.csv")
    quality = pd.read_csv(MANUSCRIPT_SOURCES / "original-quality.csv").set_index("Platform")
    original_count = int(original["Admitted runs"].sum())
    reserved_count = int(original["Locked rows still planned"].sum())
    supplement_count = len(pd.read_csv(REPO_ROOT / "data" / "development-benign-supplement-plan.csv"))
    v2_count = int(v2_paper["pooled_metrics"]["runs"])
    v3_count = int(v3_paper["pooled_metrics"]["runs"])
    development_count = original_count + supplement_count + v2_count
    total_count = development_count + v3_count
    require_paper((original_count, development_count, total_count, reserved_count) == (160, 192, 208, 92),
                  "inventory totals")
    # The supplement plan supplies its declared count; the preserved v3 dataset
    # report attests its admission. This is not another raw validation pass.

    def export_manuscript_table(table, stem, caption, label, decimals=3):
        table.to_csv(MANUSCRIPT_ROOT / f"{stem}.csv", index=False)
        # Compact print headers; CSV headings remain descriptive for reuse.
        print_table = table.rename(columns={
            "Warnings": "Warn.", "Min. availability": "Min. avail.",
            "Revision": "Rev.", "Added runs": "Added", "Cumulative": "Total",
            "Confirmation runs": "Confirm.", "Development checkpoint": "Monitor",
            "Selection": "Dev. status",
        }).copy()
        if "Dev. status" in print_table:
            print_table["Dev. status"] = print_table["Dev. status"].replace(
                {"Advanced to confirmation": "Pass"}
            )
        if stem == "table-ix-transfer-calibration":
            print_table.columns = pd.MultiIndex.from_tuples([
                ("Destination (min)", ""), ("M2 to EPYC", "FAH"),
                ("M2 to EPYC", "DR"), ("EPYC to M2", "FAH"), ("EPYC to M2", "DR"),
            ])
        tabular = print_table.to_latex(index=False, escape=True, na_rep="---",
                                      multicolumn_format="c",
                                      float_format=lambda x: f"{x:.{decimals}f}")
        latex = ("\\begin{table}[!t]\n\\centering\n"
                 + f"\\caption{{{caption}}}\n\\label{{{label}}}\n"
                 + "{\\scriptsize\n\\setlength{\\tabcolsep}{3pt}\n"
                 + "\\renewcommand{\\arraystretch}{1.05}\n"
                 + "\\resizebox{\\columnwidth}{!}{%\n" + tabular
                 + "}\n}\n\\end{table}\n")
        (MANUSCRIPT_ROOT / f"{stem}.tex").write_text(latex, encoding="utf-8")
        display(Markdown(f"### {caption}"))
        display(table.round(decimals))

    quality_rows = []
    for row in original.to_dict("records"):
        platform = row["Platform"]
        q = quality.loc[platform]
        quality_rows.append({
            "Platform": "Apple M2 Pro" if platform == "M2_MACOS" else "AMD EPYC 9354",
            "C/D": f"{row['Calibration runs']}/{row['Development runs']}",
            "V/I": f"{int(q['Valid runs'])}/{int(q['Invalid runs'])}",
            "Benign h": float(q["Valid benign hours"]),
            "Warnings": int(q["Warning events"]),
            "Min. availability": float(q["Minimum critical availability"]),
            "Reserved": int(row["Locked rows still planned"]),
        })
    quality_rows.append({
        "Platform": "Combined", "C/D": "8/152", "V/I": "160/0",
        "Benign h": sum(r["Benign h"] for r in quality_rows),
        "Warnings": sum(r["Warnings"] for r in quality_rows),
        "Min. availability": min(r["Min. availability"] for r in quality_rows),
        "Reserved": reserved_count,
    })
    export_manuscript_table(pd.DataFrame(quality_rows), "table-vi-data-quality",
                            "Original matched evidence and admission integrity audit.",
                            "tab:development_data_quality")

    revision_rows = [{"Revision": "v1", "Added runs": "160 + 16", "Cumulative": original_count + supplement_count,
                      "Confirmation runs": np.nan, "Benign h": np.nan, "Episodes": np.nan, "FAH": np.nan}]
    for revision, report, cumulative in (("v2", v2_paper, development_count), ("v3", v3_paper, total_count)):
        p = report["pooled_metrics"]
        require_paper(np.isclose(p["fah"], p["false_alerts"] / p["benign_hours"]), f"{revision} FAH")
        require_paper(np.isclose(p["benign_hours"], 16.8), f"{revision} exposure")
        revision_rows.append({"Revision": revision, "Added runs": str(p["runs"]), "Cumulative": cumulative,
                              "Confirmation runs": p["runs"], "Benign h": p["benign_hours"],
                              "Episodes": p["false_alerts"], "FAH": p["fah"]})
    revision_table = pd.DataFrame(revision_rows)
    for column in ["Confirmation runs", "Episodes"]:
        revision_table[column] = revision_table[column].astype("Int64")
    export_manuscript_table(revision_table, "table-vii-revision-history",
                            "Evidence inventory and independent confirmation by revision.", "tab:prism_revision_history")

    initial = pd.read_csv(MANUSCRIPT_SOURCES / "initial-checkpoints.csv").set_index("Method")
    progression = []
    for name in ["Static VAR", "Guarded adaptive VAR", "Robust residual fusion"]:
        row = initial.loc[name]
        progression.append({"Development checkpoint": name, "FAH": f"{row['False alerts/hour']:.2f}",
                            "DR": f"{row['Detection (%)']:.1f}%",
                            "Selection": "Pooled only" if name == "Robust residual fusion" else "Outside"})
    progression.append({"Development checkpoint": "PRISM sequential (v3)", "FAH": f"{v3_selected['fah']:.3f}",
                        "DR": f"{100*v3_selected['detection']:.1f}%", "Selection": "Advanced to confirmation"})
    export_manuscript_table(pd.DataFrame(progression), "table-viii-development-progression",
                            "Development trajectory toward the selected G3 setting.", "tab:development_g3")

    transfer = pd.read_csv(MANUSCRIPT_SOURCES / "development-transfer-calibration.csv")
    require_paper(set(transfer["family"]) == {"robust_normalized_fusion"}, "transfer checkpoint")
    transfer_rows = []
    for minutes in [0, 1, 2, 4, 8, 12]:
        row = {"Destination min": minutes}
        for source, name in [("M2_MACOS", "M2 to EPYC"), ("EPYC_LINUX", "EPYC to M2")]:
            match = transfer[(transfer["source_platform"] == source) &
                             (transfer["destination_calibration_minutes"] == minutes)]
            require_paper(len(match) == 1, f"transfer {source}, {minutes} min")
            item = match.iloc[0]
            row[f"{name} FAH"] = float(item["false_alerts_per_hour"])
            row[f"{name} DR"] = f"{100 * item['anomaly_run_detection_rate']:.1f}%"
        transfer_rows.append(row)
    require_paper(not ((transfer["false_alerts_per_hour"] <= .25) &
                      (transfer["anomaly_run_detection_rate"] >= .5)).any(), "transfer gate result")
    export_manuscript_table(pd.DataFrame(transfer_rows), "table-ix-transfer-calibration",
                            "Development transfer calibration in both platform directions.", "tab:transfer_calibration")

    def poisson_interval(count, hours):
        lower = 0.0 if count == 0 else .5 * chi2.ppf(.025, 2 * count) / hours
        return lower, .5 * chi2.ppf(.975, 2 * (count + 1)) / hours

    interval_rows = []
    for name, p in [("Development FAH", v3_selected), ("Confirmation FAH", v3_paper["pooled_metrics"])]:
        low, high = poisson_interval(p["false_alerts"], p["benign_hours"])
        interval_rows.append({"Quantity": name, "Unit": "episodes/h", "Lower 95%": low, "Upper 95%": high})
    for platform, p in v3_paper["platform_metrics"].items():
        low, high = poisson_interval(p["false_alerts"], p["benign_hours"])
        interval_rows.append({"Quantity": f"{platform} confirmation FAH", "Unit": "episodes/h",
                              "Lower 95%": low, "Upper 95%": high})
    n, detected = v3_selected["runs"], v3_selected["detected"]
    p, z = detected/n, NormalDist().inv_cdf(.975)
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n))/denominator
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/denominator
    interval_rows.append({"Quantity": "Development detection", "Unit": "%",
                          "Lower 95%": 100*(center-half), "Upper 95%": 100*(center+half)})
    interval_table = pd.DataFrame(interval_rows)
    interval_table.to_csv(MANUSCRIPT_ROOT / "table-uncertainty.csv", index=False)
    display(Markdown("### Conditional statistical uncertainty"))
    display(interval_table.round(3))

    # Exact replay accounting from the preserved per-run confirmation report.
    replay_runs = pd.read_csv(MANUSCRIPT_SOURCES / "v3-confirmation-runs.csv")
    confirmation_plan = pd.read_csv(REPO_ROOT / "data" / "v3-independent-confirmation-plan.csv")
    require_paper(replay_runs["run_id"].is_unique, "unique confirmation runs")
    require_paper(set(replay_runs["run_id"]) == set(confirmation_plan["run_id"]), "confirmation inventory")
    replay_rows = []
    for label, platform in [("Apple M2", "M2_MACOS"), ("AMD EPYC", "EPYC_LINUX"), ("Pooled", None)]:
        rows = replay_runs if platform is None else replay_runs.loc[replay_runs["platform_id"] == platform]
        summary = v3_paper["pooled_metrics"] if platform is None else v3_paper["platform_metrics"][platform]
        rich = int(rows["full_tier_blocks"].sum())
        valid = int(rows["valid_blocks"].sum())
        eligible = int(rows["eligible_blocks"].sum())
        require_paper(np.isclose(rich / valid, summary["full_tier_duty_cycle"]), f"{label}: replay ratio")
        require_paper(np.isclose(valid * 5 / 3600, summary["benign_hours"]), f"{label}: replay exposure")
        require_paper(int(rows["false_alerts"].sum()) == summary["false_alerts"], f"{label}: confirmation episodes")
        require_paper(np.isclose(valid / eligible, summary["valid_monitoring_fraction"]), f"{label}: valid fraction")
        replay_rows.append({"Scope": label, "Rich blocks": rich, "Valid blocks": valid,
                            "Rich seconds": 5 * rich, "Valid seconds": 5 * valid,
                            "Rich tier (%)": 100 * rich / valid})
    for fold in (0, 1):
        rows = replay_runs.loc[replay_runs["fold"] == fold]
        counts = rows.groupby(["platform_id", "workload"]).size()
        require_paper(len(rows) == 8 and len(counts) == 8 and (counts == 1).all(),
                      f"confirmation group {fold} design")
        require_paper(np.isclose(rows["false_alerts"].sum() / rows["benign_hours"].sum(),
                                 v3_paper["fold_metrics"][str(fold)]["fah"]), f"confirmation group {fold} FAH")
    replay_table = pd.DataFrame(replay_rows)
    replay_table.to_csv(MANUSCRIPT_ROOT / "table-replay-accounting.csv", index=False)
    require_paper((replay_rows[-1]["Rich blocks"], replay_rows[-1]["Valid blocks"]) == (37, 12096),
                  "pooled replay numerator and denominator")
    display(Markdown("### Confirmation replay accounting: retention, not acquisition savings"))
    display(replay_table.round(3))

    # Cross-check the operational table generated/displayed earlier in Section 17D.
    scorecard = OPERATIONAL_SCORECARD.set_index("Metric")
    for label, platform in [("Apple M2", "M2_MACOS"), ("AMD EPYC", "EPYC_LINUX"), ("Pooled", None)]:
        d = v3_selected if platform is None else v3_selected["platform_metrics"][platform]
        c = v3_paper["pooled_metrics"] if platform is None else v3_paper["platform_metrics"][platform]
        expected = {
            "Event coverage (development)": 100*d["detection"],
            "FAH (development)": d["fah"],
            "Benign monitoring (development)": d["benign_hours"],
            "Independent benign monitoring": c["benign_hours"],
            "FAH (confirmation)": c["fah"],
            "Telemetry fault ID": 100*d["telemetry_fault_identification_rate"],
            "Valid confirmation time": 100*c["valid_monitoring_fraction"],
            "Rich telemetry avoided (replay)": 100*(1-c["full_tier_duty_cycle"]),
        }
        for metric, value in expected.items():
            require_paper(np.isclose(float(scorecard.loc[metric, label]), value), f"{label}: {metric}")
    require_paper(np.isclose(scorecard.loc["Median TTD", "Pooled"], v3_selected["ttd"]), "scorecard delay")
    scenario_table = SCENARIO_COVERAGE.set_index("Scenario")
    for name, values in v3_selected["scenario_metrics"].items():
        require_paper(int(scenario_table.loc[name, "Detected"]) == values["detected"], f"{name}: detected")
        require_paper(int(scenario_table.loc[name, "Runs"]) == values["runs"], f"{name}: eligible")
    confirmation = v3_paper["pooled_metrics"]
    require_paper((confirmation["runs"], confirmation["false_alerts"]) == (16, 6), "v3 confirmation counts")
    require_paper(round(100*confirmation["full_tier_duty_cycle"], 2) == .31, "confirmation replay")
    check = {
        "verification": "pinned_summaries_and_protocols_not_raw_reanalysis",
        "source_snapshot_date": "2026-08-28", "validated_runs": total_count,
        "development_runs_including_calibration": development_count, "confirmation_runs": v3_count,
        "reserved_runs_planned": reserved_count, "reserved_runs_accessed_by_this_cell": 0,
        "development_g3_passed": True, "independent_confirmation_passed": False,
        "detected_controlled_event_runs": detected, "eligible_controlled_event_runs": n,
        "development_fah": v3_selected["fah"], "confirmation_fah": confirmation["fah"],
        "median_delay_seconds_among_detected_events": v3_selected["ttd"],
        "rich_tier_confirmation_replay_percent": 100*confirmation["full_tier_duty_cycle"],
        "confirmation_replay_rich_blocks": replay_rows[-1]["Rich blocks"],
        "confirmation_replay_valid_blocks": replay_rows[-1]["Valid blocks"],
        "source_sha256": manifest["bundled_sha256"],
    }
    (MANUSCRIPT_ROOT / "paper-consistency-check.json").write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
    print("Checked reported inventory, v3 outcomes, protocols, and source hashes; subgroup/figure checks follow.")
    print("Intervals assume Poisson counts or independent binary runs; no selection/dependence adjustment.")
    print("v3 passed G3 during development; independent confirmation did not pass. Reserved partition sealed.")
    print(f"Manuscript CSV and Overleaf exports: {MANUSCRIPT_ROOT}")
    export_subgroup_audit(REPO_ROOT, MANUSCRIPT_ROOT)
    return check


def export_subgroup_audit(repo_root, output_dir):
    """Current Table VIII, including its eight subgroup rows (not just old v1 table)."""
    import json
    import numpy as np
    import pandas as pd
    root, out = Path(repo_root), Path(output_dir)
    sources = root / "paper/results/manuscript/sources"
    initial = pd.read_csv(sources / "initial-checkpoints.csv")
    robust = json.loads((root / "paper/results/development/development-robust-normalization-selection.json").read_text(encoding="utf-8"))["selected"]
    v3 = json.loads((sources / "v3-development-selection.json").read_text(encoding="utf-8"))["selected"]
    rows = []

    def row(section, scope, hours, alerts, detected, total, outcome):
        rate, detection = alerts / hours, detected / total
        return {"Section": section, "Checkpoint or scope": scope, "Benign hours": hours,
                "False alerts": int(alerts), "FAH": rate, "Detected": int(detected),
                "Event runs": int(total), "DR (%)": 100 * detection,
                "Meets both research limits": rate <= 0.25 and detection >= 0.5, "Outcome": outcome}

    for item in initial.to_dict("records"):
        detected, total = map(int, item["Detected anomaly runs"].split("/"))
        outcome = "Pooled only" if item["Method"] == "Robust residual fusion" else "Outside G3"
        r = row("A. Pooled development", item["Method"], item["Benign hours"], item["False alerts"], detected, total, outcome)
        if not np.isclose(r["FAH"], item["False alerts/hour"], rtol=1e-12, atol=1e-12):
            raise ValueError("Initial checkpoint rate mismatch")
        rows.append(r)
    rows.append(row("A. Pooled development", "PRISM sequential", v3["benign_hours"], v3["false_alerts"], v3["detected"], v3["runs"], "Advance"))
    for section, report in [("B. Robust residual fusion", robust), ("C. PRISM sequential", v3)]:
        groups = [("Apple M2", report["platform_metrics"]["M2_MACOS"]),
                  ("AMD EPYC", report["platform_metrics"]["EPYC_LINUX"]),
                  ("Development fold 0", report["fold_metrics"]["0"]),
                  ("Development fold 1", report["fold_metrics"]["1"])]
        for scope, metrics in groups:
            passed = metrics["fah"] <= 0.25 and metrics["detection"] >= 0.5
            r = row(section, scope, metrics["benign_hours"], metrics["false_alerts"], metrics["detected"], metrics["runs"], "Pass" if passed else "Fail")
            if not np.isclose(r["FAH"], metrics["fah"], rtol=1e-12, atol=1e-12):
                raise ValueError("Subgroup rate mismatch")
            rows.append(r)
    table = pd.DataFrame(rows)
    table.to_csv(out / "table-viii-development-progression.csv", index=False)
    printed = pd.DataFrame({"Section": table["Section"], "Checkpoint or scope": table["Checkpoint or scope"],
                            "H (h)": table["Benign hours"].map(lambda x: f"{x:.2f}"),
                            "FAH": table["FAH"].map(lambda x: f"{x:.3f}"),
                            "Detected": table["Detected"].astype(str) + "/" + table["Event runs"].astype(str),
                            "DR": table["DR (%)"].map(lambda x: f"{x:.1f}%"), "Outcome": table["Outcome"]})
    caption = "Development progression and subgroup advancement audit."
    latex = ("\\begin{table*}[!t]\n\\centering\n\\caption{" + caption + "}\n"
             "\\label{tab:development_g3}\n{\\scriptsize\n" + printed.to_latex(index=False, escape=True)
             + "}\n\\end{table*}\n")
    (out / "table-viii-development-progression.tex").write_text(latex, encoding="utf-8")
    return table
