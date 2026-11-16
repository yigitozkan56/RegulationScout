# ⚖️ RegulationScout

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)
![Legal Data Flow](https://img.shields.io/badge/Data%20Flow-Official%20EUR--Lex%20%26%20Gazette-success)

**RegulationScout** tracks public regulatory updates across **KVKK**, **GDPR**, and the **EU AI Act**, translating legal articles into simplified, actionable engineering checklists for software developers and SaaS teams.

---

## ⚖️ Legal Data Architecture & Compliance

- **Official Legislative Sources Only:** Relies strictly on public legislative repositories (EUR-Lex ELI endpoints, Official Gazette / Resmi Gazete public notices, and official data protection authority bulletins).
- **Zero Unauthorized Scraping:** Does not scrape commercial legal commentaries or proprietary compliance databases.
- **Local SQLite Persistence:** Caches regulatory triggers and engineering checklists locally in `regulationscout_cache.db`.

---

## 📊 Sample Output

```text
⚖️ RegulationScout Technical Audit for: ai, personal-data, saas
----------------------------------------------------------------------------------------
[1] [EU AI Act | EU-AI-ACT-2024-1689] ☐ Disclose AI-generated content clearly to end users via UI badge or API metadata header.
[2] [KVKK | KVKK-6698-CROSSBORDER]    ☐ Provide an automated user data export (JSON/CSV) and right-to-erasure (DELETE /api/user) endpoint.
[3] [GDPR | GDPR-ART-25-32]           ☐ Encrypt PII at rest (AES-256) and in transit (TLS 1.3+).
```

| Framework | Regulation ID | Developer Action Item |
| :--- | :--- | :--- |
| **EU AI Act** | `EU-AI-ACT-2024-1689` | ☐ Disclose AI-generated content clearly via UI badge or API header. |
| **KVKK** | `KVKK-6698-CROSSBORDER` | ☐ Provide automated user data export and right-to-erasure (`DELETE /api/user`). |
| **GDPR** | `GDPR-ART-25-32` | ☐ Encrypt PII at rest (AES-256) and in transit (TLS 1.3+). |

---

## 🚀 Step-by-Step Installation

```bash
git clone https://github.com/yigitozkan56/RegulationScout.git
cd RegulationScout
cp .env.example .env
pip install -r requirements.txt
```

---

## 💻 Usage Examples

### CLI Mode
```bash
# Audit your application features for KVKK, GDPR, and EU AI Act technical controls
python app.py audit --features "ai,llm,saas,personal-data,cloud"
```

### Web Dashboard & REST API Mode
```bash
python app.py serve --port 8003
```
Open `http://127.0.0.1:8003` or query `GET http://127.0.0.1:8003/api/checklist?features=ai,gdpr`.

### Running Unit Tests
```bash
pytest tests/
```

---

## 🗺️ Roadmap

- [x] KVKK, GDPR, and EU AI Act technical checklist generator
- [x] Feature-tag trigger engine with SQLite cache
- [x] FastAPI interactive compliance table & JSON API
- [ ] Export compliance checklist as GitHub Issues / Markdown PR template
- [ ] Automated EUR-Lex RSS diff notifier
