import json
from pathlib import Path
from core.scoring import validate_site_candidates, score_charging_sites, build_site_suitability_report

def sample():
    return json.loads(Path("examples/candidate_sites.json").read_text())

def test_sample_candidates_valid():
    assert validate_site_candidates(sample()["candidates"])["valid"]

def test_scores_sorted_descending():
    result = score_charging_sites(sample()["candidates"], sample()["weights"])
    assert result["valid"]
    scores = [x["suitability_score"] for x in result["ranked_sites"]]
    assert scores == sorted(scores, reverse=True)

def test_invalid_score_rejected():
    sites = sample()["candidates"]
    sites[0]["demand_score"] = 120
    assert not validate_site_candidates(sites)["valid"]

def test_duplicate_id_rejected():
    sites = sample()["candidates"]
    sites[1]["site_id"] = sites[0]["site_id"]
    assert not validate_site_candidates(sites)["valid"]

def test_zero_weights_rejected():
    result = score_charging_sites(sample()["candidates"], {k: 0 for k in ("demand_score","access_score","grid_readiness_score","cost_score","constraint_score")})
    assert not result["valid"]

def test_custom_weights_normalized():
    result = score_charging_sites(sample()["candidates"], {"demand_score": 2, "access_score": 2, "grid_readiness_score": 0, "cost_score": 0, "constraint_score": 0})
    assert result["valid"]
    assert abs(sum(result["weights"].values()) - 1.0) < 1e-9

def test_low_constraint_flag():
    result = score_charging_sites(sample()["candidates"])
    site_c = next(x for x in result["ranked_sites"] if x["site_id"] == "SITE-C")
    assert site_c["constraint_review_required"]

def test_report_has_limits_and_next_steps():
    report = build_site_suitability_report(sample())
    assert report["valid"]
    assert report["limitations"] and report["recommended_next_steps"]
