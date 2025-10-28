create table if not exists public.store_info (
  id smallint primary key default 1,
  name text not null,
  address text,
  city_id integer,
  phone text,
  open_hours text
);
