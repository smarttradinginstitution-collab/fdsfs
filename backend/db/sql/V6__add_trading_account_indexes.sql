create index IF not exists idx_ta_ga on public.trading_accounts using btree (general_account_id) TABLESPACE pg_default;

create index IF not exists idx_ta_broker on public.trading_accounts using btree (broker_id) TABLESPACE pg_default;