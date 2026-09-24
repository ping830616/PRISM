"""Author utility: preserve exact manuscript assets, without executing LaTeX.

Not needed by reviewers. Run with an explicit Overleaf ZIP and output directory.
Only known PNG figures and LaTeX table source are extracted (no archive paths).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def import_assets(archive: Path, destination: Path) -> dict:
    with ZipFile(archive) as source:
        main = source.read("main.tex")
        text = main.decode("utf-8")
        figures = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\s*\{(figs/[^}]+\.png)\}", text)
        tables = re.findall(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", text, re.S)
        if len(figures) != 7 or len(tables) != 9:
            raise ValueError("Expected the reviewed draft's seven figures and nine tables")
        destination.mkdir(parents=True, exist_ok=True)
        records = []
        names = ["prism_scope", "slm_capability_progression", "dice_prism_extension",
                 "parameter_provenance", "prism_experimental_setup", "development_data_quality",
                 "prism_revision_history", "development_g3", "transfer_calibration"]
        romans = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
        for index, original in enumerate(figures, 1):
            filename = f"figures/figure-{index}-{Path(original).name}"
            data = source.read(original)
            out = destination / filename
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            records.append({"kind": "figure", "number": index, "path": filename,
                            "source_member": original, "sha256": sha256(data),
                            "role": "authored_diagram" if index <= 3 else "exact_manuscript_plot_reference"})
        for number, (roman, name, table) in enumerate(zip(romans, names, tables), 1):
            if f"{{tab:{name}}}" not in table:
                raise ValueError(f"Unexpected table {number}: {name}")
            filename = f"tables/table-{roman}-{name}.tex"
            data = (table + "\n").encode()
            out = destination / filename
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            records.append({"kind": "table", "number": roman.upper(), "path": filename,
                            "label": f"tab:{name}", "sha256": sha256(data),
                            "role": "authored_table_source" if number <= 5 else "exact_manuscript_result_table_source"})
        preamble = (r"\usepackage{amsmath,amssymb,amsfonts,booktabs,array,multirow,tabularx,graphicx,xcolor,cite}" + "\n"
                    + r"\newcolumntype{Y}{>{\raggedright\arraybackslash}X}" + "\n"
                    + "\n".join(line for line in text.splitlines() if line.startswith(r"\newcommand{\cap")) + "\n")
        auxiliary = {"table-preamble.tex": preamble.encode(), "references.bib": source.read("references.bib")}
        for filename, data in auxiliary.items():
            (destination / filename).write_bytes(data)
            records.append({"kind": "support", "path": filename, "sha256": sha256(data)})
    manifest = {"schema_version": 1, "source_archive_name": archive.name,
                "source_archive_sha256": sha256(archive.read_bytes()), "source_main_tex_sha256": sha256(main),
                "scope": "Exact manuscript images and table source; preservation is not numerical regeneration",
                "artifacts": records}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = import_assets(args.zip, args.output)
    print(f"Preserved {len(manifest['artifacts'])} manuscript assets")
