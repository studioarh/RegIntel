from fastapi.testclient import TestClient
from fastapi import status

from apps.api.app.main import app

def test_ingest_accepts_valid_fca_url() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/documents/ingest",
        params={
            "url": "https://www.handbook.fca.org.uk/handbook/CONC/"
            }
        )

    assert response.status_code == status.HTTP_202_ACCEPTED

    body = response.json()
    assert body["status"] == "Queued"
    assert body['ingestion_id'] != None


def test_ingest_rejects_non_fca_url() -> None:
    client = TestClient(app)

    response=client.post(
        "/v1/documents/ingest",
        params= {
            "url": "https://www.apple.com"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    body=response.json()
    assert body['status'] == "Rejected - Not an FCA Url"
    assert body['ingestion_id'] == None


def test_ingest_rejects_malformed_url() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/documents/ingest",
        params= {
            "url": "www.apple.com"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

