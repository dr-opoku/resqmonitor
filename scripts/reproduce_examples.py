"""Regenerate the synthetic reports, or compare them without writing."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from resqmonitor.demo import SCENARIOS, demo
from resqmonitor.report import as_json, as_text, as_html


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for scenario in SCENARIOS:
        report = demo(scenario)
        for extension, render in (("json", as_json), ("txt", as_text), ("html", as_html)):
            target = ROOT / "examples" / f"{scenario}.{extension}"
            expected = render(report)
            if args.check:
                if not target.exists() or target.read_text(encoding="utf-8") != expected:
                    mismatches.append(str(target.relative_to(ROOT)))
            else:
                target.write_text(expected, encoding="utf-8")
    if mismatches:
        print("Stale examples: " + ", ".join(mismatches), file=sys.stderr)
        return 1
    print("Synthetic examples match the current implementation." if args.check else "Synthetic examples regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
