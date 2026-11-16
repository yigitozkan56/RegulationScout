import os
import tempfile

from fastapi.testclient import TestClient

from app import RegulationScoutDB, generate_compliance_checklist, web_app


def test_generate_compliance_checklist_ai_and_kvkk():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = RegulationScoutDB(db_path=os.path.join(tmpdir, "reg.db"))
        report = generate_compliance_checklist(["ai", "kvkk"], db=db)
        frameworks = {r["framework"] for r in report["applicable_regulations"]}
        assert "EU AI Act" in frameworks
        assert "KVKK" in frameworks
        assert report["checklist_count"] >= 6


def test_web_and_api_checklist():
    client = TestClient(web_app)
    resp = client.get("/api/checklist?features=gdpr,auth")
    assert resp.status_code == 200
    data = resp.json()
    assert data["checklist_count"] >= 3
    html = client.get("/")
    assert html.status_code == 200
    assert "RegulationScout" in html.text
