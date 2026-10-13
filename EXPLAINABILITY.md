# Explainability

## Inputs
The agent accepts a list of candidate site records with scores for demand, accessibility, grid readiness, cost attractiveness, and constraint suitability, plus optional scoring weights.

## Decision
It validates each score, normalizes configured weights, calculates a weighted average, and sorts valid candidates by score. Missing fields and constraint concerns remain visible in the report.

## Limits
The agent does not fetch maps, forecast charging demand, inspect parcels, verify grid capacity, or determine permitting status. Results are preliminary and depend on user-supplied data and weights.

## Tool: validate-site-candidates

### Inputs and Data Sources
A list of candidate site objects supplied by the user.

### Decision and Reasoning
Checks required fields, unique IDs, score ranges, and basic types.

### Outputs and Evidence
Returns validation errors, warnings, and valid candidate IDs.

### Limits and Constraints
It cannot verify whether input data matches real-world conditions.

### Failure Handling
Invalid records are reported instead of silently repaired.

### Human Review
Confirm site data and provenance before using it for planning.

## Tool: score-charging-sites

### Inputs and Data Sources
Validated candidate records and optional weights.

### Decision and Reasoning
Calculates weighted averages from five explicitly named 0–100 scores; weights are normalized to sum to one.

### Outputs and Evidence
Returns per-site scores, component contributions, and score order.

### Limits and Constraints
Weights encode planning priorities and do not establish actual utilization or feasibility.

### Failure Handling
Invalid weights or invalid candidates return structured errors.

### Human Review
Have transport, utility, property, and planning specialists review shortlisted sites.

## Tool: build-site-suitability-report

### Inputs and Data Sources
Candidate records and optional weights.

### Decision and Reasoning
Combines validation, scoring, constraints, missing-data flags, and recommended due diligence.

### Outputs and Evidence
Produces a JSON-compatible report with ranked candidates and limitations.

### Limits and Constraints
The report is a screening aid, not a final site-selection decision.

### Failure Handling
Validation errors are included and prevent invalid candidates from being scored.

### Human Review
Conduct site visits, utility interconnection review, permitting checks, and financial analysis before deployment.
