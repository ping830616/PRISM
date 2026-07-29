#!/usr/bin/env python3
"""Validate a completed PRISM run and refresh validation.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prism_slm.collection import dump_json, validate_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    result = validate_run(args.run_dir, verify_hashes=True)
    dump_json(args.run_dir / "validation.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
