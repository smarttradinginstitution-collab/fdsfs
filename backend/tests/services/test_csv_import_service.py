# backend/tests/services/test_csv_import_service.py

import pytest
from backend.app.Services.csv_import_service import CsvImportService

# Dati di esempio per i test
VALID_CSV_CONTENT = """Trade #,Tipo,Data/Ora,Segnale,Prezzo USD,Dimensione posizione (quantità),Dimensione posizione (valore),P&L Netto USD,P&L Netto %,Massimale USD,Massimale %,Drawdown USD,Drawdown %,P&L cumulativo USD,P&L cumulativo %
1,Entrata long,2023-01-01 10:00,SignalA,150.00,10,1500.00,50.00,3.33,60.00,4.00,-10.00,-0.67,50.00,3.33
1,Uscita long,2023-01-01 11:00,SignalA,155.00,10,1550.00,50.00,3.33,60.00,4.00,-10.00,-0.67,50.00,3.33
2,Entrata short,2023-01-02 14:00,SignalB,200.00,5,1000.00,-25.00,-2.50,5.00,0.50,-30.00,-3.00,25.00,1.25
2,Uscita short,2023-01-02 15:00,SignalB,195.00,5,975.00,-25.00,-2.50,5.00,0.50,-30.00,-3.00,25.00,1.25
"""

INCOMPLETE_TRADE_CSV = """Trade #,Tipo,Data/Ora,Segnale,Prezzo USD,Dimensione posizione (quantità),Dimensione posizione (valore),P&L Netto USD,P&L Netto %,Massimale USD,Massimale %,Drawdown USD,Drawdown %,P&L cumulativo USD,P&L cumulativo %
3,Entrata long,2023-03-01 10:00,SignalC,100.00,1,100.00,0,0,0,0,0,0,25.00,1.25
"""

MALFORMED_DATA_CSV = """Trade #,Tipo,Data/Ora,Segnale,Prezzo USD,Dimensione posizione (quantità),Dimensione posizione (valore),P&L Netto USD,P&L Netto %,Massimale USD,Massimale %,Drawdown USD,Drawdown %,P&L cumulativo USD,P&L cumulativo %
4,Entrata long,04.01.2023 10:00:00,SignalD,100.00,1,100.00,10,1,10,1,-5,-0.5,35,1.5
4,Uscita long,not-a-date,SignalD,not-a-price,1,100.00,10,1,10,1,-5,-0.5,35,1.5
"""

class TestCsvImportService:
    def test_process_valid_csv(self):
        # Arrange
        symbol = "TEST_SYMBOL"
        service = CsvImportService(file_content=VALID_CSV_CONTENT.encode("utf-8"), symbol=symbol)

        # Act
        result = service.process_csv()

        # Assert
        assert len(result["errors"]) == 0
        assert len(result["processed_trades"]) == 2
        assert result["total_rows"] == 4

        # Controlla il primo trade
        trade1 = result["processed_trades"][0]
        assert trade1["external_id"] == "1"
        assert trade1["symbol"] == symbol
        assert trade1["direction"] == "Long"
        assert trade1["entry_price"] == 150.00
        assert trade1["exit_price"] == 155.00
        assert trade1["p_l"] == 50.00

        # Controlla il secondo trade
        trade2 = result["processed_trades"][1]
        assert trade2["external_id"] == "2"
        assert trade2["symbol"] == symbol
        assert trade2["direction"] == "Short"
        assert trade2["entry_price"] == 200.00
        assert trade2["exit_price"] == 195.00
        assert trade2["p_l"] == -25.00

    def test_process_csv_with_incomplete_trade(self):
        # Arrange
        service = CsvImportService(file_content=INCOMPLETE_TRADE_CSV.encode("utf-8"), symbol="TEST")

        # Act
        result = service.process_csv()

        # Assert
        assert len(result["processed_trades"]) == 0
        assert len(result["errors"]) == 1
        error = result["errors"][0]
        assert error["trade_number"] == "3"
        assert "Expected 2 rows" in error["error"]

    def test_process_csv_with_malformed_data(self):
        # Arrange
        service = CsvImportService(file_content=MALFORMED_DATA_CSV.encode("utf-8"), symbol="TEST")

        # Act
        result = service.process_csv()

        # Assert
        assert len(result["processed_trades"]) == 0
        assert len(result["errors"]) == 1
        error = result["errors"][0]
        assert error["trade_number"] == "4"
        assert "Data conversion error" in error["error"]

    def test_process_empty_csv(self):
        # Arrange
        service = CsvImportService(file_content=b"Trade #,Tipo\n", symbol="TEST")

        # Act
        result = service.process_csv()

        # Assert
        assert len(result["processed_trades"]) == 0
        assert len(result["errors"]) == 0
        assert result["total_rows"] == 0
