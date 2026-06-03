"""AI-powered listing generator."""

from openai import OpenAI
from app.config import AI_API_KEY, AI_BASE_URL, AI_MODEL

client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)

PLATFORM_PROMPTS = {
    "amazon": {
        "name": "Amazon",
        "rules": [
            "标题：200字符以内，品牌名 + 核心卖点 + 关键词",
            "5个 Bullet Points：每个开头大写，突出核心卖点",
            "产品描述：1000-2000字符，包含关键词，突出使用场景",
            "Search Terms（后台关键词）：不超过250字节，不要重复标题词",
            "语言风格：专业、有说服力、关键词密集但自然",
        ],
    },
    "shopify": {
        "name": "Shopify",
        "rules": [
            "SEO标题：60字符以内，包含核心关键词",
            "产品描述：500-1000字，HTML格式，段落清晰",
            "Meta Description：155字符以内，吸引点击",
            "URL Handle：小写+连字符，简洁",
            "语言风格：讲故事，突出品牌调性和生活方式",
        ],
    },
    "temu": {
        "name": "Temu",
        "rules": [
            "标题：简短有力，突出价格优势和核心卖点",
            "产品描述：简洁明了，突出性价比",
            "卖点列表：3-5个核心卖点，简单直接",
            "语言风格：接地气、强调性价比、吸引冲动消费",
        ],
    },
    "tiktok_shop": {
        "name": "TikTok Shop",
        "rules": [
            "标题：简短抓眼球，适合短视频场景",
            "产品描述：口语化、有感染力",
            "视频脚本建议：15-30秒短视频脚本，包含hook、展示、CTA",
            "语言风格：年轻化、潮流感、有互动性",
        ],
    },
}


def generate_listings(
    product_name: str,
    product_specs: str,
    target_audience: str = "",
    key_selling_points: str = "",
    language: str = "English",
) -> dict:
    """Generate optimized listings for all platforms."""

    system_prompt = f"""You are an expert e-commerce listing copywriter with deep knowledge of Amazon, Shopify, Temu, and TikTok Shop.
You understand each platform's algorithm, ranking factors, and buyer psychology.
Always write in {language}.
Output valid JSON only, no markdown."""

    user_prompt = f"""Generate optimized product listings for the following product:

Product Name: {product_name}
Specifications: {product_specs}
Target Audience: {target_audience or 'General consumers'}
Key Selling Points: {key_selling_points or 'Auto-detect from specs'}

Generate a JSON object with this exact structure:
{{
    "amazon": {{
        "title": "...",
        "bullet_points": ["...", "...", "...", "...", "..."],
        "description": "...",
        "search_terms": "..."
    }},
    "shopify": {{
        "seo_title": "...",
        "description": "...",
        "meta_description": "...",
        "url_handle": "..."
    }},
    "temu": {{
        "title": "...",
        "description": "...",
        "selling_points": ["...", "...", "..."]
    }},
    "tiktok_shop": {{
        "title": "...",
        "description": "...",
        "video_script": {{
            "hook": "...",
            "body": "...",
            "cta": "..."
        }}
    }},
    "seo_keywords": ["keyword1", "keyword2", "..."],
    "suggested_tags": ["tag1", "tag2", "..."]
}}

Platform-specific requirements:
{chr(10).join(f"- {p['name']}: {', '.join(p['rules'][:2])}" for p in PLATFORM_PROMPTS.values())}

Make every listing compelling, keyword-rich, and conversion-optimized for its platform."""

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    import json

    content = response.choices[0].message.content
    return json.loads(content)
