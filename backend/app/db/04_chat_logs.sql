create table if not exists public.chat_logs (
  id bigserial primary key,
  wa_user text not null,
  direction text not null check (direction in ('in','out')),
  message text not null,
  intent text,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);
