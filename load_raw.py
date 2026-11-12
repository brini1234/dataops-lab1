import sys

import duckdb
import pandas as pd
import pandera.errors

from pipeline.schema import RAW_ORDERS

WAREHOUSE = "warehouse.duckdb"


def main(path):
    """Extract + Load: copy the raw file into the warehouse, exactly as it is."""
    try:
        RAW_ORDERS.validate(pd.read_csv(path), lazy=True)
    except pandera.errors.SchemaErrors as error:
        print(f"REFUSED: {path} does not match the expected schema")
        print(error.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
        sys.exit(1)

    con = duckdb.connect(WAREHOUSE)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(
        f"""
        CREATE OR REPLACE TABLE raw.orders AS
        SELECT
            *,
            row_number() OVER () AS _row_number,
            '{path}' AS _source_file,
            current_timestamp AS _loaded_at
        FROM read_csv('{path}', all_varchar = true)
        """
    )
    n = con.execute("SELECT count(*) FROM raw.orders").fetchone()[0]
    print(f"Loaded {n} rows from {path} into raw.orders")
    con.close()


if __name__ == "__main__":
    main(sys.argv[1])
