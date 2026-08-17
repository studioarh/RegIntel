from fastapi import status
from fastapi.testclient import TestClient

from apps.api.app.main import app

from apps.db.models import IngestionRun

def test_ingest_accepts_valid_fca_url(db_session, client) -> None:
    

    response = client.post(
        "/v1/documents/ingest",
        json={
            "url": "https://www.handbook.fca.org.uk/handbook/CONC/"
            }
        )

    assert response.status_code == status.HTTP_202_ACCEPTED

    payload = response.json()

    assert payload["status"] == "queued"
    assert payload["ingestion_id"]

    
    

    


def test_ingest_rejects_non_fca_url(client) -> None:
   

    response=client.post(
        "/v1/documents/ingest",
        json={
            "url": "https://www.apple.com"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    body=response.json()
    assert body['status'] == "Rejected - Not an FCA Url"
    assert body['ingestion_id'] == None


def test_ingest_rejects_malformed_url() -> None:
    client2 = TestClient(app)

    response = client2.post(
        "/v1/documents/ingest",
        params= {
            "url": "www.apple.com"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

