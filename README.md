# 🌍 BX Test – Country-based Product Search

**BX Test** is a full-stack web app that lets users select a country and search for products. It uses **OpenAI**, **country-specific proxies**, **Puppeteer** for smart scraping, and **SerpAPI** to discover regional product listings. Redis is used for caching and task coordination between services.

🟢 **Live Demo**: [https://www.temptestdomain.online/](https://www.temptestdomain.online/)

---

## 🧱 Project Structure

- **`bx-test-fe`** – Frontend (React/Next.js) for country selection and product search UI.
- **`bx-test-be`** – Backend (FastAPI) that handles search logic, scraping, and caching.
- **Redis** – Used for caching search results and managing task status.
- **OpenAI** – Used to judge product relevancy and extract search input fields 

---

## 🚀 Features

- 🌐 **Country Selector** – Select any country to localize your product search.
- 🔍 **Product Search** – Enter a keyword and get region-specific product listings.
- 🧭 **Per-Country Proxy Support** – Routes scraping via proxies located in the selected country.
- 🤖 **Puppeteer Scraping** – Browser-based scraping simulates real-user interactions.
- 🔗 **SERP API Integration** – Gets region-specific websites before scraping.
- ⚡ **Redis Caching** – Caches results and background tasks to speed up future queries.
- 🧠 **OpenAI Integration** – Enhances scraping and results via AI 

---

## 🛠️ Tech Stack

| Layer        | Technology                   |
|--------------|------------------------------|
| Frontend     | React / Next.js / TypeScript |
| Backend      | FastAPI (Python)             |
| Scraping     | Puppeteer (via Pyppeteer)    |
| Caching      | Redis                        |
| Search API   | [SerpAPI](https://serpapi.com) |
| AI API       | [OpenAI](https://openai.com) |
| Proxy Routing| Per-country Proxy Support    |

---

## 📦 Setup Instructions

### 🔧 Prerequisites

- Node.js and npm
- Python 3.9+
- Redis server
- [SERP API key](https://serpapi.com)
- [OpenAI API key](https://platform.openai.com)
- Proxy provider with OxyLabs
- Docker (optional)

---

### 🧠 Backend (`bx-test-be`)

```bash
cd bx-test-be

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export SERP_API_KEY=your_serp_api_key
export OPENAI_API_KEY=your_openai_api_key
export REDIS_URL=redis://localhost:6379

# Run FastAPI backend
uvicorn main:app --reload
