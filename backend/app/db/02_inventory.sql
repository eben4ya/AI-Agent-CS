create table if not exists public.inventory (
  product_id uuid references public.products(id) on delete cascade,
  variant text default 'default',
  stock integer not null default 0,
  primary key (product_id, variant)
);
