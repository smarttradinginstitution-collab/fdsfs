# backend/tests/controllers/test_notebook_controller.py

import pytest
from httpx import AsyncClient
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models import Broker, TradingAccount, Trade, PsychologyState, Note, NotebookFolder

pytestmark = pytest.mark.anyio

# Fixture per creare le entità di base necessarie per i test
@pytest.fixture(scope="function")
async def setup_entities(async_client: AsyncClient, db_session: AsyncSession):
    # 1. Crea un General Account, che è una dipendenza per la creazione di cartelle.
    # Se esiste già (es. da un test precedente), un 409 Conflict è accettabile.
    ga_response = await async_client.post("/api/v1/general-accounts/")
    assert ga_response.status_code in [201, 409]

    # 2. Crea un Broker
    broker = Broker(name=f"Test Broker for Notes {uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)

    # 3. Crea un Trading Account
    trading_account = TradingAccount(
        label="Test Trading Account for Notes",
        broker_id=broker.id,
        initial_balance=10000,
        currency="USD",
        general_account_id=UUID(
            (await async_client.get("/api/v1/auth/me")).json()["sub"]
        ),
    )
    db_session.add(trading_account)
    await db_session.commit()
    await db_session.refresh(trading_account)

    # 4. Crea un Psychology State
    psych_state = PsychologyState(
        name="Confident", general_account_id=trading_account.general_account_id
    )
    db_session.add(psych_state)
    await db_session.commit()
    await db_session.refresh(psych_state)

    # 5. Crea un Trade e associalo allo stato psicologico
    trade = Trade(
        trading_account_id=trading_account.id,
        symbol_snapshot="EURUSD",
        status="closed",
        direction="LONG",
    )
    trade.psychology_states.append(psych_state)
    db_session.add(trade)
    await db_session.commit()
    await db_session.refresh(trade)

    # 6. Crea una Notebook Folder
    folder_payload = {"name": "Trade Analysis"}
    response = await async_client.post("/api/v1/notebook/folders", json=folder_payload)
    assert response.status_code == 201
    folder = response.json()

    # 7. Crea una Nota e associala al trade e alla cartella
    note = Note(
        title="Analysis of EURUSD Trade",
        content={"type": "doc", "content": [{"type": "paragraph"}]},
        folder_id=UUID(folder["id"]),
        trade_id=trade.id,
        general_account_id=trading_account.general_account_id,
    )
    db_session.add(note)
    await db_session.commit()
    await db_session.refresh(note)

    return {
        "folder_id": folder["id"],
        "trade_id": str(trade.id),
        "psych_state_name": psych_state.name,
    }


async def test_get_notes_for_folder_with_trade_and_psychology_state(
    async_client: AsyncClient, setup_entities
):
    """
    Verifica che il recupero delle note per una cartella funzioni correttamente
    quando una nota è collegata a un trade che ha uno stato psicologico.
    Questo test valida che lo schema di risposta utilizzi 'name' e non 'state'
    per PsychologyStateRead, risolvendo il ResponseValidationError.
    """
    folder_id = setup_entities["folder_id"]
    expected_psych_state_name = setup_entities["psych_state_name"]

    # Azione: Chiama l'endpoint per ottenere le note della cartella
    response = await async_client.get(f"/api/v1/notebook/folders/{folder_id}/notes")

    # Verifica: La richiesta deve avere successo
    assert response.status_code == 200, response.text

    # Verifica: La risposta deve contenere una lista di note
    notes = response.json()
    assert isinstance(notes, list)
    assert len(notes) > 0

    # Verifica: La nota deve contenere i dettagli del trade
    note = notes[0]
    assert "trade" in note
    assert note["trade"] is not None
    assert note["trade"]["id"] == setup_entities["trade_id"]

    # Verifica: Il trade deve contenere gli stati psicologici
    trade_details = note["trade"]
    assert "psychology_states" in trade_details
    assert isinstance(trade_details["psychology_states"], list)
    assert len(trade_details["psychology_states"]) > 0

    # Verifica cruciale: Lo stato psicologico deve avere il campo 'name'
    psych_state = trade_details["psychology_states"][0]
    assert "name" in psych_state
    assert psych_state["name"] == expected_psych_state_name

    # Verifica di sicurezza: Assicurati che il vecchio campo 'state' non esista
    assert "state" not in psych_state