import sys

import duckdb


def main(expected=None):
    """Print the report as a Markdown table, and stop if the total is not the expected one."""
    con = duckdb.connect("warehouse.duckdb", read_only=True)
    rows = con.sql("select country, revenue from revenue_by_country order by country").fetchall()
    total = round(sum(float(revenue) for _, revenue in rows), 2)
    print("| Country | Revenue |")
    print("| --- | ---: |")
    for country, revenue in rows:
        print(f"| {country} | {float(revenue):.2f} |")
    print(f"\n**Total: {total:.2f}**")
    if expected is not None and total != expected:
        print(f"\nREGRESSION: expected {expected:.2f}, got {total:.2f}")
        sys.exit(1)


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else None)
