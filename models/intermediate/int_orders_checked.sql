-- The six quality rules from TP1 and TP2. The first rule that matches wins.
select
    *,
    case
        when customer_id is null then 'missing_customer_id'
        when order_date is null then 'invalid_date'
        when quantity is null or quantity <= 0 then 'invalid_quantity'
        -- Rule 4 - validity: price present, between 0.01 and 1000
        when unit_price is null or unit_price not between 0.01 and 1000 then 'invalid_unit_price'
        -- Rule 5 - uniqueness: one row per order_id, we keep the first one
        when row_number() over (partition by order_id order by _row_number) > 1 then 'duplicate_order_id'
        -- Rule 6 - validity: the shop only sells to these five countries
        when country not in ('France', 'Germany', 'Italy', 'Morocco', 'Tunisia') then 'unknown_country'
    end as reject_reason
from {{ ref('stg_orders') }}
