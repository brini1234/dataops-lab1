select
    product,
    round(sum(quantity * unit_price), 2) as revenue
from {{ ref('orders_clean') }}
group by product
order by product
