# Listify — AI 多平台 Listing 一键生成器

> 跨境电商卖家的 AI Listing 助手。一次输入，自动生成 Amazon、Shopify、Temu、TikTok Shop 四大平台的完整 Listing。

## ✨ 功能

- 🔄 **一键多平台** — 一个产品，同时生成 Amazon / Shopify / Temu / TikTok Shop Listing
- 🌍 **多语言** — 支持 English、中文、日本語、Deutsch、Français、Español
- 🔍 **SEO 优化** — 自动生成关键词、搜索词、Meta 标签
- 🎬 **视频脚本** — TikTok Shop 专属短视频脚本建议
- 📋 **一键复制** — 每个字段独立复制，直接粘贴到平台后台
- 💾 **历史记录** — 所有生成的 Listing 永久保存
- 🆓 **免费 3 次** — 注册即送 3 次免费生成

## 🎯 目标用户

- 跨境电商卖家（Amazon、Temu、TikTok Shop）
- Shopify 独立站店主
- 跨境电商运营人员
- 代运营公司

## 🚀 部署

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📦 技术栈

- **Backend**: Python + FastAPI
- **Frontend**: HTML / CSS / JavaScript
- **AI**: DeepSeek API (OpenAI-compatible)
- **Database**: SQLite
- **Payment**: Lemon Squeezy
