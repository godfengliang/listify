"""API routes for Listify — auth, generation, analysis, and history."""

import json
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from app.core.generator import generate_listings
from app.core.analyzer import analyze_competitor, generate_seo_keywords
from app.auth import (
    create_user, verify_user, get_user,
    decrement_free_generations, save_listing,
    get_user_listings, get_listing,
)

router = APIRouter()
_sessions: dict[str, dict] = {}


def _get_session(request: Request) -> dict | None:
    token = request.cookies.get("session_token")
    return _sessions.get(token) if token else None


# ─── Auth ───

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/api/register")
async def api_register(req: RegisterRequest, response: Response):
    if len(req.password) < 6:
        raise HTTPException(400, "密码至少6位")
    user = create_user(req.email, req.password, req.name)
    if not user:
        raise HTTPException(400, "邮箱已注册")
    token = _create_session(user)
    response.set_cookie("session_token", token, httponly=True, max_age=86400 * 30)
    return {"ok": True, "user": {"id": user["id"], "email": user["email"], "plan": user["plan"]}}


@router.post("/api/login")
async def api_login(req: LoginRequest, response: Response):
    user = verify_user(req.email, req.password)
    if not user:
        raise HTTPException(401, "邮箱或密码错误")
    token = _create_session(user)
    response.set_cookie("session_token", token, httponly=True, max_age=86400 * 30)
    return {"ok": True, "user": {"id": user["id"], "email": user["email"], "plan": user["plan"]}}


@router.post("/api/logout")
async def api_logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token and token in _sessions:
        del _sessions[token]
    response.delete_cookie("session_token")
    return {"ok": True}


@router.get("/api/me")
async def api_me(request: Request):
    session = _get_session(request)
    if not session:
        raise HTTPException(401, "未登录")
    user = get_user(session["user_id"])
    return {"id": user["id"], "email": user["email"], "name": user["name"],
            "plan": user["plan"], "free_generations_left": user["free_generations_left"]}


def _create_session(user: dict) -> str:
    import secrets
    token = secrets.token_hex(32)
    _sessions[token] = {"user_id": user["id"], "email": user["email"], "plan": user["plan"]}
    return token


def _check_auth_and_quota(request: Request) -> tuple[dict, dict]:
    session = _get_session(request)
    if not session:
        raise HTTPException(401, "请先登录")
    allowed = decrement_free_generations(session["user_id"])
    if not allowed:
        user = get_user(session["user_id"])
        raise HTTPException(403, f"免费次数已用完，请升级到 Pro 计划。剩余次数：{user['free_generations_left']}")
    return session, user


# ─── Listing generation ───

class ListingRequest(BaseModel):
    product_name: str
    product_specs: str
    target_audience: str = ""
    key_selling_points: str = ""
    language: str = "English"


@router.post("/api/generate")
async def api_generate_listings(req: ListingRequest, request: Request):
    session, _ = _check_auth_and_quota(request)
    if not req.product_name.strip():
        raise HTTPException(400, "产品名称不能为空")

    try:
        result = generate_listings(
            product_name=req.product_name,
            product_specs=req.product_specs,
            target_audience=req.target_audience,
            key_selling_points=req.key_selling_points,
            language=req.language,
        )
        result_json = json.dumps(result, ensure_ascii=False)
        save_listing(session["user_id"], req.product_name, req.product_specs, req.language, result_json)
        user = get_user(session["user_id"])
        result["_meta"] = {
            "generations_left": user["free_generations_left"] if user["plan"] == "free" else "∞",
            "plan": user["plan"],
        }
        return result
    except Exception as e:
        raise HTTPException(500, f"生成失败：{str(e)}")


# ─── Competitor Analysis ───

class CompetitorRequest(BaseModel):
    your_product: str
    competitor_title: str
    competitor_description: str = ""
    platform: str = "amazon"
    language: str = "English"


@router.post("/api/analyze-competitor")
async def api_analyze_competitor(req: CompetitorRequest, request: Request):
    session, _ = _check_auth_and_quota(request)

    try:
        result = analyze_competitor(
            your_product=req.your_product,
            competitor_title=req.competitor_title,
            competitor_description=req.competitor_description,
            platform=req.platform,
            language=req.language,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"分析失败：{str(e)}")


# ─── SEO Keywords ───

class KeywordRequest(BaseModel):
    product_name: str
    product_specs: str
    platform: str = "amazon"
    language: str = "English"


@router.post("/api/seo-keywords")
async def api_seo_keywords(req: KeywordRequest, request: Request):
    session, _ = _check_auth_and_quota(request)

    try:
        result = generate_seo_keywords(
            product_name=req.product_name,
            product_specs=req.product_specs,
            platform=req.platform,
            language=req.language,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"生成失败：{str(e)}")


# ─── History ───

@router.get("/api/listings")
async def api_listings(request: Request):
    session = _get_session(request)
    if not session:
        raise HTTPException(401, "未登录")
    return get_user_listings(session["user_id"])


@router.get("/api/listings/{listing_id}")
async def api_get_listing(listing_id: int, request: Request):
    session = _get_session(request)
    if not session:
        raise HTTPException(401, "未登录")
    listing = get_listing(listing_id, session["user_id"])
    if not listing:
        raise HTTPException(404, "未找到")
    return json.loads(listing["result_json"])


@router.get("/api/health")
async def health():
    return {"status": "ok", "service": "Listify API"}
