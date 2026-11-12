import pandera.pandas as pa

MAX_UNIT_PRICE = 1000
MIN_PLAUSIBLE_PRICES = 0.80


def _mostly_plausible(prices):
    """At least 80 % of the prices must be between 0.01 and MAX_UNIT_PRICE."""
    return prices.between(0.01, MAX_UNIT_PRICE).mean() >= MIN_PLAUSIBLE_PRICES


RAW_ORDERS = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False),
        "order_date": pa.Column(str),
        "customer_id": pa.Column(str, nullable=True),
        "country": pa.Column(str),
        "product": pa.Column(str),
        "quantity": pa.Column(int),
        "unit_price": pa.Column(
            float,
            pa.Check(_mostly_plausible, error="more than 20 % of the prices are implausible"),
        ),
    },
    strict=True,
    coerce=True,
)
