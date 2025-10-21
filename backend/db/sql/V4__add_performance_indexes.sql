-- V4__add_performance_indexes.sql
-- Questo script aggiunge indici critici per migliorare le performance delle query
-- legate all'analisi dei trade e al caricamento dei dati correlati.

-- Indice sulla colonna trading_account_id nella tabella trades
-- per velocizzare il filtro dei trade per conto di trading.
CREATE INDEX IF NOT EXISTS idx_trades_trading_account_id ON public.trades (trading_account_id);

-- Indice sulla colonna entry_timestamp nella tabella trades
-- per velocizzare il filtro dei trade per intervallo di date.
CREATE INDEX IF NOT EXISTS idx_trades_entry_timestamp ON public.trades (entry_timestamp);

-- Indice sulla colonna trade_id nella tabella images
-- per velocizzare il recupero delle immagini associate a un singolo trade.
CREATE INDEX IF NOT EXISTS idx_images_trade_id ON public.images (trade_id);

-- Indici sulle chiavi esterne delle tabelle associative per ottimizzare le join.
CREATE INDEX IF NOT EXISTS idx_trades_tags_trade_id ON public.trades_tags (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_tags_tag_id ON public.trades_tags (tag_id);

CREATE INDEX IF NOT EXISTS idx_trades_mistakes_trade_id ON public.trades_mistakes (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_mistakes_mistake_id ON public.trades_mistakes (mistake_id);

CREATE INDEX IF NOT EXISTS idx_trades_news_impacts_trade_id ON public.trades_news_impacts (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_news_impacts_news_impact_id ON public.trades_news_impacts (news_impact_id);

CREATE INDEX IF NOT EXISTS idx_trades_psychology_trade_id ON public.trades_psychology (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_psychology_psychology_id ON public.trades_psychology (psychology_id);

CREATE INDEX IF NOT EXISTS idx_trades_rules_trade_id ON public.trades_rules (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_rules_rule_id ON public.trades_rules (rule_id);

-- Indice su playbook_id in trades per accelerare le aggregazioni per playbook
CREATE INDEX IF NOT EXISTS idx_trades_playbook_id ON public.trades (playbook_id);

-- Indice su general_account_id in playbooks per accelerare il recupero dei playbook per utente
CREATE INDEX IF NOT EXISTS idx_playbooks_general_account_id ON public.playbooks (general_account_id);

-- Indici per ottimizzare la query delle statistiche delle regole
CREATE INDEX IF NOT EXISTS idx_rules_groups_playbook_playbook_id ON public.rules_groups_playbook (playbook_id);
CREATE INDEX IF NOT EXISTS idx_rules_playbook_rules_groups_playbook_id ON public.rules_playbook (rules_groups_playbook_id);
-- Nota: idx_trades_rules_trade_id e idx_trades_rules_rule_id sono già stati aggiunti in uno script precedente
-- ma li includiamo qui con IF NOT EXISTS per sicurezza e completezza.
CREATE INDEX IF NOT EXISTS idx_trades_rules_trade_id ON public.trades_rules (trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_rules_rule_id ON public.trades_rules (rule_id);

-- Indice su user_id in general_accounts per accelerare il recupero dell'account per utente (eseguito su ogni richiesta API protetta)
CREATE INDEX IF NOT EXISTS idx_general_accounts_user_id ON public.general_accounts (user_id);
