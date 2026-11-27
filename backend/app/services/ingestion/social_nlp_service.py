"""Crowdsourced and social media NLP distress report processing service."""

import re
from typing import Dict, Any


class SocialNLPService:
    """Parses emergency alerts and social posts for crisis cues, hazards, and locations."""

    KEYWORDS = {
        "flood": ["water entering house", "drowning", "river broke banks", "submerged", "stranded on roof", "flood"],
        "wildfire": ["smoke", "flames", "fire spreading", "burn", "wildfire", "ash falling"],
        "landslide": ["mudslide", "landslide", "rocks falling", "road collapsed", "hill caved"],
        "cyclone": ["cyclone", "hurricane", "tin roof blown", "gale winds", "squall"],
        "heatwave": ["heat stroke", "dehydration", "scorching heat", "sunstroke"],
        "drought": ["wells dry", "crop failure", "no water supply", "parched soil"]
    }

    URGENCY_TOKENS = ["sos", "help", "emergency", "trapped", "dying", "urgent", "children", "elderly"]

    @classmethod
    def analyze_report(cls, text: str) -> Dict[str, Any]:
        """Analyzes textual report and extracts disaster type, urgency score, and tags."""
        text_lower = text.lower()
        matched_disaster = "unknown"
        for disaster, words in cls.KEYWORDS.items():
            if any(w in text_lower for w in words):
                matched_disaster = disaster
                break

        urgency = 0.3
        for token in cls.URGENCY_TOKENS:
            if token in text_lower:
                urgency += 0.2
        urgency = min(1.0, round(urgency, 2))

        return {
            "disaster_type": matched_disaster,
            "urgency_score": urgency,
            "requires_immediate_dispatch": urgency >= 0.7,
            "extracted_keywords": [w for w in cls.URGENCY_TOKENS if w in text_lower]
        }
