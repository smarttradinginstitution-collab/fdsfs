# backend/tests/controllers/test_trades_controller.py

import pytest
from httpx import AsyncClient
import uuid
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models import Broker, Playbook
from app.Models.rules_group_playbook import RulesGroupPlaybook
from app.Models.rule_playbook import RulePlaybook

pytestmark = pytest.mark.anyio

async def setup_broker(db_session: AsyncSession) -> str:
    """Helper to create a broker and return its ID."""
    broker = Broker(name=f"Test Broker {uuid.uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return str(broker.id)

async def setup_trading_account(client: AsyncClient, db_session: AsyncSession) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    await client.post("/api/v1/general-accounts/")
    broker_id = await setup_broker(db_session)
    response = await client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": "Test Trading Account",
            "broker_id": broker_id,
            "initial_balance": 100000,
            "currency": "USD"
        }
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]

async def test_create_trade_fails_without_trading_account(async_client: AsyncClient):
    """Testa che la creazione di un trade fallisca se il trading account non esiste."""
    response = await async_client.post(
        "/api/v1/trades/",
        json={"trading_account_id": str(uuid.uuid4()), "symbol_snapshot": "EURUSD", "status": "closed", "direction": "LONG"}
    )
    assert response.status_code == 404

async def test_create_and_get_trade(async_client: AsyncClient, db_session: AsyncSession):
    """Testa la creazione e il recupero di un trade semplice."""
    trading_account_id = await setup_trading_account(async_client, db_session)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "BTCUSD",
        "direction": "LONG",
        "status": "closed",
        "entry_price": 50000,
        "exit_price": 51000,
        "p_l": 1000
    }

    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    trade_id = created_data["id"]

    assert created_data["symbol_snapshot"] == "BTCUSD"

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == trade_id

    list_response = await async_client.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1

async def test_create_trade_with_related_entities_by_name(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa la creazione di un trade con entità correlate (tags, mistakes, playbook)
    passando i loro nomi come stringhe, come farebbe il frontend.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "ETHUSD",
        "status": "closed",
        "direction": "SHORT",
        "tags": ["Good Entry", "News-Driven"],
        "mistakes": ["FOMO"],
        "playbook": "Opening Range Breakout"
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_trade = create_response.json()

    assert len(created_trade["tags"]) == 2
    returned_tags = {tag['name'] for tag in created_trade['tags']}
    assert returned_tags == {"Good Entry", "News-Driven"}

    assert len(created_trade["mistakes"]) == 1
    assert created_trade["mistakes"][0]["name"] == "FOMO"

    assert created_trade["playbook"] is not None
    assert created_trade["playbook"]["title"] == "Opening Range Breakout"

    trade_payload_2 = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "SOLUSD",
        "tags": ["Good Entry"],
        "status": "closed",
        "direction": "LONG"
    }
    create_response_2 = await async_client.post("/api/v1/trades/", json=trade_payload_2)
    assert create_response_2.status_code == 201
    created_trade_2 = create_response_2.json()
    assert len(created_trade_2["tags"]) == 1

    good_entry_tag_from_trade1 = next(t for t in created_trade['tags'] if t['name'] == 'Good Entry')
    good_entry_tag_from_trade2 = created_trade_2['tags'][0]

    assert good_entry_tag_from_trade2['id'] == good_entry_tag_from_trade1['id']


async def test_delete_trade(async_client: AsyncClient, db_session: AsyncSession):
    """Testa l'eliminazione di un trade."""
    trading_account_id = await setup_trading_account(async_client, db_session)
    trade_payload = {"trading_account_id": trading_account_id, "symbol_snapshot": "ADAUSD", "status": "closed", "direction": "LONG"}
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/trades/{trade_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404

async def test_list_trades_with_date_filter(async_client: AsyncClient, db_session: AsyncSession):
    """Testa che il filtro per data sull'endpoint di elenco dei trade funzioni correttamente."""
    trading_account_id = await setup_trading_account(async_client, db_session)
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Crea tre trade in giorni diversi
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "YESTERDAY_TRADE", "entry_timestamp": yesterday.isoformat(), "status": "closed", "direction": "LONG"})
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "TODAY_TRADE", "entry_timestamp": today.isoformat(), "status": "closed", "direction": "LONG"})
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "TOMORROW_TRADE", "entry_timestamp": tomorrow.isoformat(), "status": "closed", "direction": "LONG"})

    # 1. Testa con il filtro per data (solo oggi)
    response_filtered = await async_client.get(
        f"/api/v1/trades/by-trading-account/{trading_account_id}",
        params={"start_date": today.isoformat(), "end_date": today.isoformat()}
    )
    assert response_filtered.status_code == 200
    filtered_data = response_filtered.json()
    assert len(filtered_data) == 1
    assert filtered_data[0]["symbol_snapshot"] == "TODAY_TRADE"

    # 2. Testa senza filtro per data (tutti i trade)
    response_unfiltered = await async_client.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert response_unfiltered.status_code == 200
    unfiltered_data = response_unfiltered.json()
    assert len(unfiltered_data) == 3


async def test_get_trade_with_correctly_calculated_metrics(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa che il recupero di un singolo trade tramite API includa le metriche
    (trade_risk, net_roi, r_multiple) calcolate correttamente, verificando
    che il problema di data-loading sia risolto.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    # Dati del trade che causava l'errore, con PNL e SL/TP
    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "ESZ23",
        "direction": "SHORT",
        "status": "closed",
        "p_l": 1575.00,
        "entry_price": 24841.50,
        "exit_price": 24832.75,
        "stop_loss_price": 24846.00,
    }

    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    # Azione: Recupera il trade tramite l'endpoint GET
    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    trade_details = get_response.json()

    # Valori attesi (basati sulla logica di calcolo corretta)
    # initial_balance dal setup è 100000
    # trade_risk = abs(1575 / (24832.75 - 24841.50)) * abs(24841.50 - 24846.00) = 810
    # net_roi = (1575 / 100000) * 100 = 1.575
    # r_multiple = 1575 / 810 = 1.9444...

    # Verifica: Assicurati che i campi calcolati non siano None o 0.0
    assert trade_details["trade_risk"] is not None
    assert trade_details["net_roi"] is not None
    assert trade_details["r_multiple"] is not None

    # Converte i valori in float per la comparazione, risolvendo il TypeError
    trade_risk_float = float(trade_details["trade_risk"])
    net_roi_float = float(trade_details["net_roi"])
    r_multiple_float = float(trade_details["r_multiple"])

    assert trade_risk_float > 0
    assert net_roi_float > 0
    assert r_multiple_float > 0

    # Verifica: Controlla che i valori calcolati siano corretti
    assert trade_risk_float == pytest.approx(810.0)
    assert net_roi_float == pytest.approx(1.575)
    assert r_multiple_float == pytest.approx(1.9444, abs=1e-4)


async def test_get_recent_trades_succeeds(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa che l'endpoint per ottenere gli ultimi trade recenti funzioni correttamente
    senza sollevare errori di validazione Pydantic, specialmente dopo la rimozione
    di campi obsoleti come `rules_followed`.
    """
    # Setup: Crea un account e alcuni trade
    trading_account_id = await setup_trading_account(async_client, db_session)
    for i in range(5):
        await async_client.post(
            "/api/v1/trades/",
            json={
                "trading_account_id": trading_account_id,
                "symbol_snapshot": f"TRADE_{i}",
                "p_l": 100 + i,
                "status": "closed",
                "direction": "LONG"
            }
        )

    # Azione: Chiama l'endpoint dei trade recenti
    response = await async_client.get("/api/v1/trades/recent")

    # Verifica
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "symbol_snapshot" in data[0]
    # Verifica implicitamente che non ci sia stato un ValidationError


async def test_update_trade_rules(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa l'aggiornamento delle regole 'seguite' per un trade, verificando
    che la persistenza nel database funzioni correttamente.
    """
    # 1. Setup: Crea un trade e un playbook con regole
    trading_account_id = await setup_trading_account(async_client, db_session)

    # Crea un playbook
    playbook = Playbook(title="Test Playbook for Rules", description="", general_account_id=uuid.uuid4()) # L'ID qui non è cruciale per questo test
    db_session.add(playbook)
    await db_session.commit()

    # Crea un gruppo di regole
    rules_group = RulesGroupPlaybook(playbook_id=playbook.id, name_group="Entry Rules")
    db_session.add(rules_group)
    await db_session.commit()

    # Crea 3 regole
    rule1 = RulePlaybook(rules_groups_playbook_id=rules_group.id, rule="Rule 1")
    rule2 = RulePlaybook(rules_groups_playbook_id=rules_group.id, rule="Rule 2")
    rule3 = RulePlaybook(rules_groups_playbook_id=rules_group.id, rule="Rule 3")
    db_session.add_all([rule1, rule2, rule3])
    await db_session.commit()

    # Crea un trade
    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "RULES_TEST",
        "playbook_id": str(playbook.id),
        "status": "closed",
        "direction": "LONG",
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    # 2. Azione: Aggiorna le regole del trade (selezionane 2 su 3)
    rule_ids_to_set = [str(rule1.id), str(rule3.id)]
    update_response = await async_client.put(
        f"/api/v1/trades/{trade_id}/rules",
        json=rule_ids_to_set
    )
    assert update_response.status_code == 200

    # 3. Verifica: La risposta dovrebbe contenere il trade aggiornato
    updated_trade = update_response.json()
    assert updated_trade["id"] == trade_id
    followed_rule_ids = {rule["id"] for rule in updated_trade["rules_followed"]}
    assert followed_rule_ids == set(rule_ids_to_set)

    # 4. Verifica extra: Ricarica il trade e controlla le regole associate
    await db_session.commit() # Assicura che la transazione sia chiusa
    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    trade_details = get_response.json()

    assert "rules_followed" in trade_details
    assert len(trade_details["rules_followed"]) == 2
    followed_rule_ids = {rule["id"] for rule in trade_details["rules_followed"]}
    assert followed_rule_ids == set(rule_ids_to_set)


async def test_update_trade_review_status(async_client: AsyncClient, db_session: AsyncSession):
    """Testa l'aggiornamento dello stato 'is_reviewed' di un trade tramite l'endpoint PATCH dedicato."""
    # 1. Setup: Crea un account di trading e un trade
    trading_account_id = await setup_trading_account(async_client, db_session)
    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "REVIEW_TEST",
        "is_reviewed": False  # Stato iniziale
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_trade = create_response.json()
    trade_id = created_trade["id"]
    assert not created_trade["is_reviewed"]

    # 2. Azione: Aggiorna lo stato a True
    patch_response_true = await async_client.patch(
        f"/api/v1/trades/{trade_id}/review",
        json={"is_reviewed": True}
    )

    # 3. Verifica 1
    assert patch_response_true.status_code == 200
    updated_trade_true = patch_response_true.json()
    assert updated_trade_true["is_reviewed"] is True

    # 4. Azione: Aggiorna lo stato a False
    patch_response_false = await async_client.patch(
        f"/api/v1/trades/{trade_id}/review",
        json={"is_reviewed": False}
    )

    # 5. Verifica 2
    assert patch_response_false.status_code == 200
    updated_trade_false = patch_response_false.json()
    assert updated_trade_false["is_reviewed"] is False

    # 6. Verifica 3 (Consistenza DB)
    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    final_trade_state = get_response.json()
    assert final_trade_state["is_reviewed"] is False