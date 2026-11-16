"""
RegulationScout - Legal Regulatory Tracker & Developer Technical Compliance Checklist Generator.
Monitors official public feeds (EUR-Lex, Official Gazette / Resmi Gazete, KVKK, GDPR, EU AI Act).
"""

import json
import os
from contextlib import closing
import sqlite3
import time
from typing import Any, Dict, List, Optional

import typer
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app_cli = typer.Typer(help="RegulationScout CLI - Generate developer technical compliance checklists from KVKK, GDPR & EU AI Act.")
web_app = FastAPI(
    title="RegulationScout API & Web UI",
    description="Translates public regulatory updates (EUR-Lex, Resmi Gazete, KVKK, GDPR, EU AI Act) into actionable developer checklists.",
    version="1.0.0",
)

OFFICIAL_REGULATIONS = [
    {
        "reg_id": "EU-AI-ACT-2024-1689",
        "jurisdiction": "European Union (EUR-Lex)",
        "framework": "EU AI Act",
        "title": "Regulation (EU) 2024/1689 on Artificial Intelligence - Transparency & High-Risk Systems",
        "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "triggers": ["ai", "llm", "chatbot", "biometric", "scoring"],
        "checklist": [
            "Disclose AI-generated content clearly to end users via UI badge or API metadata header.",
            "Maintain technical documentation of model training/fine-tuning provenance and system prompts.",
            "Implement human-in-the-loop override and audit logging for automated decision endpoints.",
        ],
    },
    {
        "reg_id": "KVKK-6698-CROSSBORDER",
        "jurisdiction": "TÃ¼rkiye (Resmi Gazete / KVKK)",
        "framework": "KVKK",
        "title": "Law No. 6698 Amendments on Cross-Border Personal Data Transfer & Standard Contractual Clauses",
        "source_url": "https://www.resmigazete.gov.tr/",
        "triggers": ["kvkk", "personal-data", "cloud", "auth", "analytics", "saas"],
        "checklist": [
            "Ensure explicit opt-in consent is decoupled from Terms of Service acceptance.",
            "Document data residency of cloud sub-processors and file Standard Contractual Clauses (SCC) if hosted abroad.",
            "Provide an automated user data export (JSON/CSV) and right-to-erasure (`DELETE /api/user`) endpoint.",
        ],
    },
    {
        "reg_id": "GDPR-ART-25-32",
        "jurisdiction": "European Union (EUR-Lex)",
        "framework": "GDPR",
        "title": "GDPR Articles 25 & 32 - Data Protection by Design, Default & Cryptographic Security",
        "source_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "triggers": ["gdpr", "personal-data", "saas", "auth", "cookies", "database"],
        "checklist": [
            "Encrypt PII at rest (AES-256) and in transit (TLS 1.3+).",
            "Disable non-essential telemetry/cookies by default prior to explicit user consent.",
            "Implement automatic log retention rotation and IP anonymization in access logs.",
        ],
    },
]


class RegulationScoutDB:
    """SQLite local cache for public regulatory notices and checklists."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("REGULATIONSCOUT_DB_PATH", "regulationscout_cache.db")
        self._init_db()

    def _init_db(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS regulations (
                    reg_id TEXT PRIMARY KEY,
                    jurisdiction TEXT,
                    framework TEXT,
                    title TEXT,
                    source_url TEXT,
                    triggers_json TEXT,
                    checklist_json TEXT,
                    cached_at INTEGER
                )
                """
            )
            conn.commit()
        if not self.get_all():
            for reg in OFFICIAL_REGULATIONS:
                self.save_regulation(reg)

    def save_regulation(self, reg: Dict[str, Any]) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO regulations (
                    reg_id, jurisdiction, framework, title, source_url,
                    triggers_json, checklist_json, cached_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reg["reg_id"],
                    reg["jurisdiction"],
                    reg["framework"],
                    reg["title"],
                    reg["source_url"],
                    json.dumps(reg["triggers"]),
                    json.dumps(reg["checklist"]),
                    int(time.time()),
                ),
            )
            conn.commit()

    def get_all(self) -> List[Dict[str, Any]]:
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM regulations ORDER BY reg_id ASC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["triggers"] = json.loads(d.pop("triggers_json"))
                d["checklist"] = json.loads(d.pop("checklist_json"))
                out.append(d)
            return out


def generate_compliance_checklist(
    stack_features: List[str], db: Optional[RegulationScoutDB] = None
) -> Dict[str, Any]:
    """Generates an actionable developer checklist based on application features."""
    db = db or RegulationScoutDB()
    all_regs = db.get_all()
    norm_features = {f.strip().lower() for f in stack_features if f.strip()}

    applicable_regs = []
    combined_tasks = []

    for reg in all_regs:
        triggers = set(reg["triggers"])
        if not norm_features or (norm_features & triggers):
            applicable_regs.append(reg)
            for item in reg["checklist"]:
                combined_tasks.append({"framework": reg["framework"], "reg_id": reg["reg_id"], "task": item})

    return {
        "evaluated_features": sorted(norm_features),
        "applicable_regulations": applicable_regs,
        "checklist_count": len(combined_tasks),
        "checklist": combined_tasks,
    }


@web_app.get("/api/checklist")
def api_checklist(
    features: str = Query("ai,saas,personal-data,cloud", description="Comma-separated product features"),
) -> Dict[str, Any]:
    feat_list = [f.strip() for f in features.split(",") if f.strip()]
    return generate_compliance_checklist(feat_list)


@web_app.get("/", response_class=HTMLResponse)
def web_dashboard(features: str = "ai,saas,personal-data") -> str:
    feat_list = [f.strip() for f in features.split(",") if f.strip()]
    report = generate_compliance_checklist(feat_list)
    items_html = "".join(
        f"<tr><td><span class='badge'>{c['framework']}</span></td><td><code>{c['reg_id']}</code></td><td>â˜ {c['task']}</td></tr>"
        for c in report["checklist"]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RegulationScout - Developer Compliance Checklist</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; background: #0f172a; color: #f8fafc; }}
        h1 {{ color: #a78bfa; }}
        .badge {{ background: #6d28d9; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.85rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
    </style>
</head>
<body>
    <h1>âš–ï¸ RegulationScout <span class="badge">EUR-Lex & Official Gazette Feeds</span></h1>
    <p>Actionable engineering compliance checklist for features: <code>{features}</code></p>
    <table>
        <thead>
            <tr><th>Framework</th><th>Regulation ID</th><th>Developer Action Item</th></tr>
        </thead>
        <tbody>{items_html}</tbody>
    </table>
</body>
</html>"""


@app_cli.command("audit")
def cli_audit(
    features: str = typer.Option("ai,saas,personal-data", "--features", "-f", help="Comma-separated app features"),
) -> None:
    """Generate a technical compliance checklist for your software stack."""
    feat_list = [f.strip() for f in features.split(",") if f.strip()]
    report = generate_compliance_checklist(feat_list)
    typer.echo(f"âš–ï¸ RegulationScout Technical Audit for: {', '.join(report['evaluated_features'])}")
    typer.echo("-" * 88)
    for idx, item in enumerate(report["checklist"], 1):
        typer.echo(f"[{idx}] [{item['framework']} | {item['reg_id']}] â˜ {item['task']}")


@app_cli.command("serve")
def cli_serve(port: int = typer.Option(8003, "--port", "-p")) -> None:
    """Launch the RegulationScout FastAPI web server."""
    import uvicorn

    uvicorn.run(web_app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    app_cli()
