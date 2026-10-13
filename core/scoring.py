from typing import Any

SCORE_FIELDS = ("demand_score", "access_score", "grid_readiness_score", "cost_score", "constraint_score")
DEFAULT_WEIGHTS = {
    "demand_score": 0.30,
    "access_score": 0.20,
    "grid_readiness_score": 0.20,
    "cost_score": 0.15,
    "constraint_score": 0.15,
}

def validate_site_candidates(candidates: Any) -> dict[str, Any]:
    errors, warnings, valid_ids = [], [], []
    if not isinstance(candidates, list) or not candidates:
        return {"valid": False, "errors": ["candidates must be a non-empty list."], "warnings": [], "valid_site_ids": []}
    seen = set()
    for i, site in enumerate(candidates):
        if not isinstance(site, dict):
            errors.append(f"candidates[{i}]: expected an object.")
            continue
        site_id = site.get("site_id")
        if not isinstance(site_id, str) or not site_id.strip():
            errors.append(f"candidates[{i}].site_id: required non-empty string.")
        elif site_id in seen:
            errors.append(f"candidates[{i}].site_id: duplicate ID {site_id!r}.")
        else:
            seen.add(site_id)
        site_errors = []
        for field in SCORE_FIELDS:
            value = site.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
                site_errors.append(f"candidates[{i}].{field}: expected a number from 0 to 100.")
        if site_errors:
            errors.extend(site_errors)
        else:
            valid_ids.append(site_id)
        if site.get("constraint_score", 100) < 40:
            warnings.append(f"{site_id or 'candidate '+str(i)}: low constraint score; verify land-use, permitting, environmental, and access restrictions.")
        if "notes" not in site:
            warnings.append(f"{site_id or 'candidate '+str(i)}: no provenance notes supplied.")
    return {"valid": not errors, "errors": errors, "warnings": warnings, "valid_site_ids": valid_ids}

def _weights(weights: Any) -> dict[str, float]:
    if weights is None:
        return dict(DEFAULT_WEIGHTS)
    if not isinstance(weights, dict):
        raise ValueError("weights must be an object.")
    unknown = set(weights) - set(SCORE_FIELDS)
    if unknown:
        raise ValueError("unknown weight keys: " + ", ".join(sorted(unknown)))
    result = {key: float(weights.get(key, DEFAULT_WEIGHTS[key])) for key in SCORE_FIELDS}
    if any(value < 0 for value in result.values()):
        raise ValueError("weights must be non-negative.")
    total = sum(result.values())
    if total <= 0:
        raise ValueError("at least one weight must be greater than zero.")
    return {key: value / total for key, value in result.items()}

def score_charging_sites(candidates: Any, weights: Any = None) -> dict[str, Any]:
    validation = validate_site_candidates(candidates)
    if not validation["valid"]:
        return {"valid": False, "errors": validation["errors"], "warnings": validation["warnings"], "ranked_sites": []}
    try:
        normalized = _weights(weights)
    except (ValueError, TypeError) as exc:
        return {"valid": False, "errors": [str(exc)], "warnings": validation["warnings"], "ranked_sites": []}
    ranked = []
    for site in candidates:
        contributions = {field: round(float(site[field]) * normalized[field], 4) for field in SCORE_FIELDS}
        ranked.append({
            "site_id": site["site_id"],
            "suitability_score": round(sum(contributions.values()), 2),
            "component_scores": {field: site[field] for field in SCORE_FIELDS},
            "weighted_contributions": contributions,
            "constraint_review_required": site["constraint_score"] < 40,
            "notes": site.get("notes")
        })
    ranked.sort(key=lambda row: (-row["suitability_score"], row["site_id"]))
    return {"valid": True, "errors": [], "warnings": validation["warnings"], "weights": normalized, "ranked_sites": ranked,
            "method": "Weighted average of five supplied 0–100 scores; weights normalized to sum to 1."}

def build_site_suitability_report(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"valid": False, "status": "invalid_input", "errors": ["payload must be an object."]}
    candidates = payload.get("candidates")
    validation = validate_site_candidates(candidates)
    scoring = score_charging_sites(candidates, payload.get("weights"))
    findings = [{"type": "data_warning", "detail": w} for w in validation["warnings"]]
    for row in scoring.get("ranked_sites", []):
        if row["constraint_review_required"]:
            findings.append({"type": "constraint_review", "site_id": row["site_id"], "detail": "Low constraint score requires specific due diligence."})
    return {
        "agent": "ev-charging-site-suitability-agent",
        "valid": validation["valid"] and scoring["valid"],
        "status": "needs_input_correction" if not validation["valid"] or not scoring["valid"] else "preliminary_screening",
        "validation": validation,
        "scoring": scoring,
        "findings": findings,
        "limitations": [
            "Scores are based only on user-supplied data and configurable weights.",
            "No maps, traffic counts, grid capacity, parcel boundaries, permits, or charging demand were independently verified.",
            "A high score does not guarantee technical, legal, financial, or environmental feasibility."
        ],
        "recommended_next_steps": [
            "Verify demand assumptions using local EV registrations, traffic, and charging utilization data.",
            "Request a utility interconnection and capacity assessment.",
            "Check property rights, access, zoning, permits, environmental constraints, and accessibility.",
            "Complete site survey and financial analysis before a deployment decision."
        ]
    }
