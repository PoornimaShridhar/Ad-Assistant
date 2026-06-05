from typing import Dict, List

TARGET_CPL = 20.0
CTR_THRESHOLD = 2.0

def generate_recommendations(metrics: List[Dict]) -> List[Dict]:
    """
    Rule engine that converts metrics → recommendations
    """
    recommendations = []

    for m in metrics:
        campaign_id = m["campaign_id"]
        cpl = m["cpl"]
        ctr = m["ctr"]

        # Rule 1: High CPL
        if cpl > TARGET_CPL * 1.5:
            recommendations.append({
                "campaign_id": campaign_id,
                "type": "high_cpl",
                "action": "reduce_budget",
                "reason": f"CPL {cpl} is significantly above target {TARGET_CPL}",
                "cpl": cpl,
                "target_cpl": TARGET_CPL,
                "ctr": ctr,
            })

        # Rule 2: Strong campaign
        elif cpl < TARGET_CPL * 0.8:
            recommendations.append({
                "campaign_id": campaign_id,
                "type": "strong_campaign",
                "action": "increase_budget",
                "reason": f"CPL {cpl} is well below target {TARGET_CPL}",
                "cpl": cpl,
                "target_cpl": TARGET_CPL,
                "ctr": ctr,
            })

        # Rule 3: Low CTR
        if ctr < CTR_THRESHOLD:
            recommendations.append({
                "campaign_id": campaign_id,
                "type": "low_ctr",
                "action": "review_ad_copy",
                "reason": f"CTR {ctr}% is below threshold {CTR_THRESHOLD}%",
                "cpl": cpl,
                "target_cpl": TARGET_CPL,
                "ctr": ctr,
            })

    return recommendations