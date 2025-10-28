insert into public.products (sku,name,description,price_cents,images,category) values
('TSHIRT-M-001','T-Shirt Unisex','Katun combed 30s',75000,'["/img/tshirt1.jpg"]','apparel')
on conflict (sku) do nothing;

insert into public.products (sku,name,description,price_cents,images,category) values
('TSHIRT-M-002','T-Shirt Oversize','Loose fit',85000,'["/img/tshirt2.jpg"]','apparel')
on conflict (sku) do nothing;

insert into public.inventory (product_id,variant,stock)
select id, 'M', 20 from public.products where sku='TSHIRT-M-001'
on conflict do nothing;

insert into public.inventory (product_id,variant,stock)
select id, 'L', 12 from public.products where sku='TSHIRT-M-001'
on conflict do nothing;

insert into public.inventory (product_id,variant,stock)
select id, 'All', 15 from public.products where sku='TSHIRT-M-002'
on conflict do nothing;

insert into public.store_info (id,name,address,city_id,phone,open_hours)
values (1,'Toko Eben','Jl. Mawar No. 1, Sleman', 501, '0812-xxxx-xxxx', 'Sen-Sab 09:00-17:00')
on conflict (id) do update set name=excluded.name;
