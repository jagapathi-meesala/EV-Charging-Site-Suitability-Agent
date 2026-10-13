import argparse, json, sys
from pathlib import Path
from .scoring import build_site_suitability_report

def main() -> int:
    parser = argparse.ArgumentParser(description="Screen EV charging candidate sites.")
    parser.add_argument("input", help="JSON file containing candidate sites and optional weights")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = build_site_suitability_report(payload)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report.get("valid") else 1

if __name__ == "__main__":
    raise SystemExit(main())
