-- Enable RLS for all tables
-- 008_asset_markets.sql

-- 1. Create asset_markets table
CREATE TABLE public.asset_markets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Add foreign key column to assets table
ALTER TABLE public.assets
ADD COLUMN asset_market_id UUID;

-- 3. Insert a default 'Unknown' market
INSERT INTO public.asset_markets (name) VALUES ('Unknown');

-- 4. Update existing assets to point to the 'Unknown' market
UPDATE public.assets
SET asset_market_id = (SELECT id FROM public.asset_markets WHERE name = 'Unknown')
WHERE asset_market_id IS NULL;

-- 5. Add foreign key constraint
ALTER TABLE public.assets
ADD CONSTRAINT assets_asset_market_id_fkey
FOREIGN KEY (asset_market_id) REFERENCES public.asset_markets(id);

-- 6. Set the column to NOT NULL
ALTER TABLE public.assets
ALTER COLUMN asset_market_id SET NOT NULL;


-- 7. RLS Policies for asset_markets
ALTER TABLE public.asset_markets ENABLE ROW LEVEL SECURITY;

-- Grant all access to admin users
CREATE POLICY "Allow all access to admin"
ON public.asset_markets
FOR ALL
TO service_role
USING (
  (SELECT rolname FROM pg_roles WHERE oid = session_user::regrole) = 'service_role'
);

-- Grant read-only access to authenticated users
CREATE POLICY "Allow read access to authenticated users"
ON public.asset_markets
FOR SELECT
TO authenticated
USING (true);