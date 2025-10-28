create index if not exists chat_logs_user_time_idx on public.chat_logs (wa_user, created_at desc);
