from pathlib import Path

import pandas as pd

from app.services.azure_sql_service import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CSV_DIR = PROJECT_ROOT / "data" / "raw" / "csv"


CSV_TABLE_MAP = {
    "custody_accounts.csv": "custody_accounts",
    "trade_status.csv": "trade_status",
    "settlement_exceptions.csv": "settlement_exceptions",
    "reconciliation_breaks.csv": "reconciliation_breaks",
    "case_tickets.csv": "case_tickets",
    "corporate_actions.csv": "corporate_actions",
}


def load_csv_file(csv_file: Path, table_name: str) -> dict:
    if not csv_file.exists():
        return {
            "file": csv_file.name,
            "table": table_name,
            "status": "missing",
            "rows_loaded": 0,
        }

    df = pd.read_csv(csv_file)

    engine = get_engine()

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=100,
    )

    return {
        "file": csv_file.name,
        "table": table_name,
        "status": "loaded",
        "rows_loaded": len(df),
    }


def load_all_csv_files() -> list[dict]:
    results = []

    for csv_name, table_name in CSV_TABLE_MAP.items():
        csv_file = CSV_DIR / csv_name
        result = load_csv_file(csv_file, table_name)
        results.append(result)

    return results


if __name__ == "__main__":
    results = load_all_csv_files()

    for item in results:
        print(item)