# EV Charging Site Suitability Agent

A deterministic, portable screening agent that compares candidate EV charging sites using user-supplied attributes. It produces transparent weighted scores, constraint flags, and a report of missing data.

## Capabilities
- Validate candidate IDs and numeric input fields.
- Score demand, accessibility, grid readiness, cost attractiveness, and constraint suitability on a 0–100 scale.
- Apply configurable weights and disclose the scoring method.
- Flag incomplete inputs and hard constraints for human review.
- Generate JSON output for a dashboard or planning workflow.

## Scope and safeguards
This is an early-stage screening tool, not a substitute for a site survey, utility interconnection study, traffic analysis, land-use review, permitting, or financial feasibility assessment. Scores are only as reliable as the input data and the stated weights. Do not use example data as a real investment recommendation.

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 verification/readiness_audit.py
python3 -m core.cli examples/candidate_sites.json
```

## Candidate fields
Each candidate has `site_id`, `demand_score`, `access_score`, `grid_readiness_score`, `cost_score`, and `constraint_score`, each score from 0 to 100. Optional `notes` can record provenance or unresolved issues.

## OpenGAP
Manifest targets OpenGAP v0.1.0. If the official CLI is installed, run `opengap validate`.
