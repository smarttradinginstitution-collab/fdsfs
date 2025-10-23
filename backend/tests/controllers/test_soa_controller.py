# backend/tests/controllers/test_soa_controller.py
import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import date
from unittest.mock import patch, AsyncMock
import uuid
from app.main import app
from app.Router.dependencies import get_current_general_account_id

# Lo useremo per il test end-to-end
@pytest.mark.asyncio
async def test_get_soa_analysis_endpoint(
    async_client: AsyncClient,
):
    # Applica l'override della dipendenza solo per questo test
    async def override_get_current_general_account_id():
        return uuid.uuid4()
    app.dependency_overrides[get_current_general_account_id] = override_get_current_general_account_id
    # Mock del servizio per evitare chiamate reali al DB e logica complessa
    mock_soa_result = {
        "clusters_summary": {},
        "causal_analysis": {
            "playbook": [], "tag": [], "mistake": [], "psychology": [], "news": [], "rule": []
        },
        "parametric_optimization": {},
        "predictive_metrics": {},
        "drawdown_z_score": {
            "z_score": 0.0, "current_drawdown_usd": 0.0, "average_drawdown_usd": 0.0, "stddev_drawdown_usd": 0.0
        },
        "trade_details": []
    }

    with patch('app.Services.analytics_service.AnalyticsService.get_soa_analysis', new_callable=AsyncMock) as mock_get_soa:
        mock_get_soa.return_value = mock_soa_result

        # Dati fittizi per la richiesta
        trading_account_id = uuid.uuid4()
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)

        # Effettua la richiesta all'endpoint
        response = await async_client.get(
            f"/analytics/{trading_account_id}/soa",
            params={"start_date": str(start_date), "end_date": str(end_date)}
        )

        # Verifica della risposta
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "clusters_summary" in data
        assert "causal_analysis" in data
        assert "drawdown_z_score" in data
        assert data["drawdown_z_score"]["z_score"] == 0.0

    # Ripristina le dipendenze originali
    app.dependency_overrides = {}

# Aggiungere test per casi di errore (es. 404 Not Found)
@pytest.mark.asyncio
async def test_get_soa_analysis_endpoint_no_data(async_client: AsyncClient):
    # Applica l'override della dipendenza solo per questo test
    async def override_get_current_general_account_id():
        return uuid.uuid4()
    app.dependency_overrides[get_current_general_account_id] = override_get_current_general_account_id

    with patch('app.Services.analytics_service.AnalyticsService.get_soa_analysis', new_callable=AsyncMock) as mock_get_soa:
        mock_get_soa.return_value = None # Simula il caso in cui non ci sono dati

        trading_account_id = uuid.uuid4()
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)

        response = await async_client.get(
            f"/analytics/{trading_account_id}/soa",
            params={"start_date": str(start_date), "end_date": str(end_date)}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No data available for the selected period or user unauthorized." in response.json()['detail']

    # Ripristina le dipendenze originali
    app.dependency_overrides = {}
