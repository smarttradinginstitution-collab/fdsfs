# backend/app/Services/csv_import_service.py

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple


class CsvImportService:
    """
    Servizio per processare un file CSV di trade.
    La logica chiave è raggruppare le righe per 'Trade #' per combinare
    le operazioni di entrata e uscita in un singolo record di trade.
    """

    def __init__(self, file_content: bytes, symbol: str):
        """
        Inizializza il servizio con il contenuto del file CSV.
        :param file_content: Contenuto del file in bytes.
        :param symbol: Il simbolo di trading da associare a tutti i trade importati.
        """
        self.file_content = file_content
        self.symbol = symbol

    def process_csv(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Metodo principale che orchestra il processo di importazione.
        1. Legge il CSV.
        2. Raggruppa le righe per 'Trade #'.
        3. Combina i gruppi in trade singoli e validati.
        4. Ritorna i trade processati e gli errori riscontrati.
        """
        try:
            # Usa 'utf-8-sig' per gestire correttamente i file CSV che iniziano
            # con un BOM (Byte Order Mark), un problema comune con i file
            # esportati da alcuni programmi (es. Excel).
            decoded_content = self.file_content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(decoded_content))
            # La prima riga è l'header, DictReader la usa per le chiavi
            rows = list(reader)
        except (UnicodeDecodeError, csv.Error) as e:
            return {"processed_trades": [], "errors": [{"row": 1, "error": f"Failed to parse CSV: {e}"}]}

        total_rows = len(rows)
        grouped_rows = self._group_rows_by_trade_number(rows)
        processed_trades, errors = self._combine_and_validate_groups(grouped_rows)

        return {"processed_trades": processed_trades, "errors": errors, "total_rows": total_rows}

    def _group_rows_by_trade_number(self, rows: List[Dict]) -> Dict[str, List[Dict]]:
        """Raggruppa le righe del CSV per il valore della colonna 'Trade #'."""
        grouped = {}
        for i, row in enumerate(rows):
            # Aggiungiamo il numero di riga originale per i messaggi di errore
            row["original_row_number"] = i + 2  # +2 per l'header e l'indice base 1
            trade_number = row.get("Trade #")
            if not trade_number:
                continue  # Salta righe vuote o senza Trade #

            if trade_number not in grouped:
                grouped[trade_number] = []
            grouped[trade_number].append(row)
        return grouped

    def _combine_and_validate_groups(self, grouped_rows: Dict[str, List[Dict]]) -> Tuple[List[Dict], List[Dict]]:
        """
        Itera sui gruppi di righe, li combina in trade singoli e valida i dati.
        """
        trades_to_create = []
        errors = []

        for trade_number, rows in grouped_rows.items():
            if len(rows) != 2:
                errors.append({
                    "trade_number": trade_number,
                    "error": f"Expected 2 rows (entry and exit) but found {len(rows)}.",
                    "rows": [r["original_row_number"] for r in rows]
                })
                continue

            entry_row = next((r for r in rows if "Entrata" in r.get("Tipo", "")), None)
            exit_row = next((r for r in rows if "Uscita" in r.get("Tipo", "")), None)

            if not entry_row or not exit_row:
                errors.append({
                    "trade_number": trade_number,
                    "error": "Could not find one entry and one exit row.",
                    "rows": [r["original_row_number"] for r in rows]
                })
                continue

            try:
                trade_dict = self._build_trade_from_rows(trade_number, entry_row, exit_row)
                trades_to_create.append(trade_dict)
            except (ValueError, KeyError) as e:
                errors.append({
                    "trade_number": trade_number,
                    "error": str(e),
                    "rows": [entry_row["original_row_number"], exit_row["original_row_number"]]
                })

        return trades_to_create, errors

    def _build_trade_from_rows(self, trade_number: str, entry_row: Dict, exit_row: Dict) -> Dict:
        """
        Costruisce un singolo dizionario di trade combinando i dati
        dalle righe di entrata e uscita.
        Solleva ValueError o KeyError in caso di dati mancanti o malformati.
        """
        try:
            # --- Estrazione e Conversione Dati ---
            # Data/Ora (formato atteso: 'GG.MM.AAAA HH:mm:ss')
            datetime_format = "%d.%m.%Y %H:%M:%S"
            entry_timestamp = datetime.strptime(entry_row["Data/Ora"], datetime_format)
            exit_timestamp = datetime.strptime(exit_row["Data/Ora"], datetime_format)

            # Prezzi e Quantità
            entry_price = float(entry_row["Prezzo USD"])
            exit_price = float(exit_row["Prezzo USD"])
            position_size = float(entry_row["Dimensione posizione (quantità)"])

            # P&L e altre metriche (dalla riga di uscita)
            p_l = float(exit_row["P&L Netto USD"])
            highest_price = float(exit_row["Massimale USD"])
            lowest_price = float(exit_row["Drawdown USD"])

            # Direzione (Long/Short)
            tipo_entrata = entry_row["Tipo"]
            if "long" in tipo_entrata.lower():
                direction = "Long"
            elif "short" in tipo_entrata.lower():
                direction = "Short"
            else:
                raise ValueError(f"Invalid entry type: {tipo_entrata}")

            # --- Costruzione del dizionario del Trade ---
            return {
                "external_id": trade_number,
                "symbol": self.symbol,
                "entry_timestamp": entry_timestamp,
                "exit_timestamp": exit_timestamp,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "position_size": position_size,
                "p_l": p_l,
                "direction": direction,
                "setup": exit_row.get("Segnale"),
                "highest_price_during_trade": highest_price,
                "lowest_price_during_trade": lowest_price,
                # Altri campi opzionali possono essere aggiunti qui se necessario
            }
        except KeyError as e:
            raise KeyError(f"Missing required column in CSV: {e}")
        except ValueError as e:
            raise ValueError(f"Data conversion error: {e}")
