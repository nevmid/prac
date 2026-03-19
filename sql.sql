with order_materials_cost as (
	select
	oi.id_order, oi.id_product, oi.count, oi.price_at_order as sale_price,
	SUM(si.consumption_rate * m.current_price * oi.count) as total_material_cost
	from order_items oi
	JOIN specifications s ON oi.id_product = s.id_product
	JOIN specification_items si on s.id_specification = si.id_specification
	JOIN materials m on m.id_material = si.id_material
	GROUP BY oi.id_order, oi.id_product, oi.count, oi.price_at_order
),
order_sum as (
	select o.id_order, o.order_number, o.order_date, c.name as customer,
	SUM(oi.count) as products_count,
	SUM(oi.count * oi.price_at_order) as total_amount,
	SUM(omc.total_material_cost) as total_material_cost
	from orders o
	join customers c ON o.id_customer = c.id_customer
	join order_items oi ON oi.id_order = o.id_order
	join order_materials_cost omc ON oi.id_order = omc.id_order AND oi.id_product = omc.id_product
	GROUP BY o.id_order, o.order_number, o.order_date, c.name
)

SELECT id_order, order_number, order_date, customer, products_count, total_amount,
	total_material_cost
FROM order_sum