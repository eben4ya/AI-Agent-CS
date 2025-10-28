create extension if not exists "pgcrypto";

create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  sku text unique not null,
  name text not null,
  description text,
  price_cents integer not null check (price_cents >= 0),
  images jsonb default '[]'::jsonb,
  category text,
  created_at timestamptz default now()
);
