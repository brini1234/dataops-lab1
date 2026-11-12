import sys

import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)
con.sql(sys.argv[1]).show()
