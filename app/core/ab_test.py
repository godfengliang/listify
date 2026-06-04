"""A/B testing suggestions for listings — Pro feature."""

from openai import OpenAI
from app.config import AI_API_KEY, AI_BASE_URL, AI_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        if not AI_API_KEY:
            raise RuntimeError("AI_API_KEY not configured")
        _client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
    return _client


def generate_ab_variants(
    product_name: str,
    original_title: str,
    original_description: str,
    platform: str = "amazon",
    language: str = "English",
) -> dict:
    """Generate A/B test variants for a listing."""

    system_prompt = f"""You are an e-commerce conversion optimization expert.
You create A/B test variants that test different psychological triggers.
Always write in {language}.
Output valid JSON only."""

    user_prompt = f"""Generate 3 A/B test variants for this {platform} listing.

Product: {product_name}

ORIGINAL TITLE: {original_title}
ORIGINAL DESCRIPTION: {original_description}

Create 3 variants that test different strategies:
- Variant A: Emotional appeal (fear of missing out, desire for status)
- Variant B: Data-driven (numbers, statistics, comparisons)
- Variant C: Storytelling (relatable scenario, customer journey)

Generate JSON:
{{
    "original": {{
        "title": "{original_title}",
        "analysis": "what the current listing does well and what it lacks"
    }},
    "variants": [
        {{
            "name": "Emotional Appeal",
            "title": "...",
            "description": "...",
            "why_this_works": "psychological principle behind it",
            "expected_improvement": "+15-25% CTR"
        }},
        {{
            "name": "Data-Driven",
            "title": "...",
            "description": "...",
            "why_this_works": "why numbers increase trust",
            "expected_improvement": "+10-20% conversion"
        }},
        {{
            "name": "Storytelling",
            "title": "...",
            "description": "...",
            "why_this_works": "why stories create connection",
            "expected_improvement": "+20-30% engagement"
        }}
    ],
    "testing_plan": {{
        "duration_days": 14,
        "sample_size_per_variant": 500,
        "primary_metric": "conversion_rate",
        "secondary_metrics": ["click_through_rate", "time_on_page", "add_to_cart_rate"]
    }}
}}"""

    response = _get_client().chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    import json
    return json.loads(response.choices[0].message.content)


def optimize_for_platform(
    product_name: str,
    product_specs: str,
    platform: str = "amazon",
    language: str = "English",
) -> dict:
    """Generate platform-specific optimization tips."""

    platform_tips = {
        "amazon": "Focus on A9 algorithm ranking factors, bullet point optimization, backend keywords, and review strategy",
        "shopify": "Focus on Google SEO, page speed, structured data, and conversion rate optimization",
        "temu": "Focus on price-value positioning, visual hierarchy, and impulse purchase triggers",
        "tiktok_shop": "Focus on video-first presentation, social proof, and trend alignment",
    }

    system_prompt = f"""You are an expert at optimizing {platform} listings for maximum conversion.
Always write in {language}.
Output valid JSON only."""

    user_prompt = f"""Give me specific, actionable optimization tips for this product on {platform}.

Product: {product_name}
Specs: {product_specs}

{platform_tips.get(platform, '')}

Generate JSON:
{{
    "overall_score": 0-100,
    "critical_fixes": [
        {{"issue": "...", "fix": "...", "impact": "high/medium/low"}}
    ],
    "optimization_tips": [
        {{"area": "...", "current": "...", "recommended": "...", "reason": "..."}}
    ],
    "competitor_benchmarks": {{
        "avg_title_length": "...",
        "avg_bullet_count": "...",
        "common_keywords": ["..."],
        "avg_price_range": "..."
    }},
    "checklist": [
        "checklist item 1",
        "checklist item 2"
    ]
}}"""

    response = _get_client().chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=2500,
        response_format={"type": "json_object"},
    )

    import json
    return json.loads(response.choices[0].message.content)
