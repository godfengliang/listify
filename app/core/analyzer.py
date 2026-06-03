"""Competitor listing analyzer — analyzes competitor listings and suggests improvements."""

from openai import OpenAI
from app.config import AI_API_KEY, AI_BASE_URL, AI_MODEL

client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)


def analyze_competitor(
    your_product: str,
    competitor_title: str,
    competitor_description: str = "",
    platform: str = "amazon",
    language: str = "English",
) -> dict:
    """Analyze a competitor's listing and generate improvement suggestions."""

    platform_rules = {
        "amazon": "Amazon (title, bullets, description, A+ content)",
        "shopify": "Shopify (SEO title, product description, meta tags)",
        "temu": "Temu (title, description, selling points)",
        "tiktok_shop": "TikTok Shop (title, description, video content)",
    }

    system_prompt = f"""You are an expert e-commerce competitive analyst and listing optimizer.
You analyze competitor listings and provide actionable improvements.
Always write in {language}.
Output valid JSON only."""

    user_prompt = f"""Analyze this competitor's {platform_rules.get(platform, platform)} listing and help me create a BETTER one.

MY PRODUCT: {your_product}

COMPETITOR'S LISTING:
Title: {competitor_title}
{f'Description: {competitor_description}' if competitor_description else ''}

Generate a JSON with this structure:
{{
    "competitor_analysis": {{
        "strengths": ["what they do well"],
        "weaknesses": ["what they miss or do poorly"],
        "keyword_gaps": ["keywords they missed that I should target"],
        "score": 75
    }},
    "improved_listing": {{
        "title": "my better version of the title",
        "key_improvements": ["why my version is better"],
        "suggested_bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"],
        "description": "improved full description",
        "high_value_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    }},
    "strategy": {{
        "positioning": "how to position against this competitor",
        "price_hint": "suggested pricing strategy",
        "differentiation": "key differentiation points"
    }}
}}

Be specific and actionable. Focus on winning the buy box / search ranking."""

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    import json
    content = response.choices[0].message.content
    return json.loads(content)


def generate_seo_keywords(
    product_name: str,
    product_specs: str,
    platform: str = "amazon",
    language: str = "English",
) -> dict:
    """Generate high-value SEO keywords for a product."""

    system_prompt = f"""You are an e-commerce SEO expert specializing in keyword research for {platform}.
Always write in {language}.
Output valid JSON only."""

    user_prompt = f"""Generate high-value SEO keywords for this product:

Product: {product_name}
Specs: {product_specs}
Platform: {platform}

Generate JSON:
{{
    "primary_keywords": ["3-5 highest volume keywords"],
    "long_tail_keywords": ["8-10 specific long-tail keywords with lower competition"],
    "negative_keywords": ["keywords to avoid - too competitive or irrelevant"],
    "trending_keywords": ["3-5 rising trend keywords for this category"],
    "backend_keywords": ["for Amazon backend search terms field, comma-separated, under 250 bytes"],
    "hashtag_suggestions": ["for TikTok/Instagram, 10-15 hashtags"],
    "search_volume_estimate": {{
        "primary": "high/medium/low",
        "competition": "high/medium/low",
        "opportunity_score": 85
    }}
}}"""

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    import json
    content = response.choices[0].message.content
    return json.loads(content)
