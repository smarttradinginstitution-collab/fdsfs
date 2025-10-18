-- Drop the old discipline_rules table and related daily instances
DROP TABLE IF EXISTS "public"."daily_rule_instances";
DROP TABLE IF EXISTS "public"."discipline_rules";

-- Create the new discipline_settings table
CREATE TABLE "public"."discipline_settings" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "general_account_id" uuid NOT NULL,
    "trading_days" _int4 NOT NULL DEFAULT '{1,2,3,4,5}',
    "start_day_by" time NULL,
    "link_trades_to_playbook_threshold" int4 NULL,
    "trade_has_stop_loss_threshold" int4 NULL,
    "max_loss_per_trade_type" text NULL,
    "max_loss_per_trade_value" float8 NULL,
    "max_loss_per_day" float8 NULL,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT "discipline_settings_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "discipline_settings_general_account_id_fkey" FOREIGN KEY ("general_account_id") REFERENCES "public"."general_accounts"("id") ON DELETE CASCADE,
    CONSTRAINT "discipline_settings_general_account_id_key" UNIQUE ("general_account_id")
);

-- Create the new manual_rules table
CREATE TABLE "public"."manual_rules" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "general_account_id" uuid NOT NULL,
    "name" text NOT NULL,
    "frequency" _int4 NOT NULL,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT "manual_rules_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "manual_rules_general_account_id_fkey" FOREIGN KEY ("general_account_id") REFERENCES "public"."general_accounts"("id") ON DELETE CASCADE
);

-- Recreate the daily_rule_instances table to be simpler for now
-- This will now only track manual rules completion
CREATE TABLE "public"."daily_rule_instances" (
    "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "manual_rule_id" uuid NOT NULL,
    "trading_account_id" uuid NOT NULL,
    "daily_journal_id" uuid NOT NULL,
    "date" date NOT NULL,
    "status" text NOT NULL DEFAULT 'pending', -- e.g., 'pending', 'completed', 'missed'
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT "daily_rule_instances_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "daily_rule_instances_manual_rule_id_fkey" FOREIGN KEY ("manual_rule_id") REFERENCES "public"."manual_rules"("id") ON DELETE CASCADE,
    CONSTRAINT "daily_rule_instances_trading_account_id_fkey" FOREIGN KEY ("trading_account_id") REFERENCES "public"."trading_accounts"("id") ON DELETE CASCADE,
    CONSTRAINT "daily_rule_instances_manual_rule_id_date_trading_account_id_key" UNIQUE ("manual_rule_id", "date", "trading_account_id", "daily_journal_id")
);

-- Enable RLS
ALTER TABLE "public"."discipline_settings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."manual_rules" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."daily_rule_instances" ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable ALL for users based on general_account_id" ON "public"."discipline_settings"
AS PERMISSIVE FOR ALL
TO authenticated
USING ((EXISTS ( SELECT 1
   FROM general_accounts
  WHERE ((general_accounts.id = discipline_settings.general_account_id) AND (general_accounts.user_id = auth.uid())))));

CREATE POLICY "Enable ALL for users based on general_account_id" ON "public"."manual_rules"
AS PERMISSIVE FOR ALL
TO authenticated
USING ((EXISTS ( SELECT 1
   FROM general_accounts
  WHERE ((general_accounts.id = manual_rules.general_account_id) AND (general_accounts.user_id = auth.uid())))));

CREATE POLICY "Enable ALL for users based on trading_account_id" ON "public"."daily_rule_instances"
AS PERMISSIVE FOR ALL
TO authenticated
USING ((EXISTS ( SELECT 1
   FROM trading_accounts
  WHERE ((trading_accounts.id = daily_rule_instances.trading_account_id) AND (EXISTS ( SELECT 1
           FROM general_accounts
          WHERE ((general_accounts.id = trading_accounts.general_account_id) AND (general_accounts.user_id = auth.uid()))))))));