-- Staging: give each column its real type and repair what can be repaired.
-- No row is removed here.
select
    src.customer_id,
    src.product,
    src._row_number,
    src._loaded_at,
    try_cast(src.order_id as integer) as order_id,
    try_strptime(src.order_date, '%Y-%m-%d')::date as order_date,
    upper(left(trim(src.country), 1)) || lower(substr(trim(src.country), 2)) as country,
    try_cast(src.quantity as integer) as quantity,
    try_cast(src.unit_price as decimal(10, 2)) as unit_price
from {{ source('raw', 'orders') }} as src
