-- 004_snaptrade_tables.sql

-- Create the profiles table to store user-specific application data
CREATE TABLE public.profiles (
    id uuid NOT NULL,
    snaptrade_user_secret text NULL,
    CONSTRAINT profiles_pkey PRIMARY KEY (id),
    CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Add comments to the table and columns
COMMENT ON TABLE public.profiles IS 'Stores user-specific application data, extending the auth.users table.';
COMMENT ON COLUMN public.profiles.id IS 'Foreign key to auth.users.id.';
COMMENT ON COLUMN public.profiles.snaptrade_user_secret IS 'The unique secret provided by SnapTrade to identify the user.';

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see their own profile
CREATE POLICY "Allow users to see their own profile"
ON public.profiles
FOR SELECT
USING (auth.uid() = id);

-- Create policy to allow users to insert their own profile
-- This is needed so that we can create a profile for a new user.
-- A trigger on the auth.users table will handle the creation.
CREATE POLICY "Allow users to insert their own profile"
ON public.profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

-- Create policy to allow users to update their own profile
CREATE POLICY "Allow users to update their own profile"
ON public.profiles
FOR UPDATE
USING (auth.uid() = id);

-- This function will be triggered when a new user signs up.
-- It creates a corresponding row in the public.profiles table.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (id)
  VALUES (new.id);
  RETURN new;
END;
$$;

-- Trigger the function every time a new user is created.
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();


-- Create the brokerage_connections table
CREATE TABLE public.brokerage_connections (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    user_id uuid NOT NULL,
    snaptrade_connection_id text NOT NULL,
    brokerage_name text NOT NULL,
    status text NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT brokerage_connections_pkey PRIMARY KEY (id),
    CONSTRAINT brokerage_connections_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Add comments to the table and columns
COMMENT ON TABLE public.brokerage_connections IS 'Stores information about each broker connection for a user.';
COMMENT ON COLUMN public.brokerage_connections.user_id IS 'Foreign key to auth.users.id.';
COMMENT ON COLUMN public.brokerage_connections.snaptrade_connection_id IS 'The unique ID for the connection from SnapTrade.';
COMMENT ON COLUMN public.brokerage_connections.status IS 'e.g., "active", "sync_error", "disconnected"';

-- Enable Row Level Security
ALTER TABLE public.brokerage_connections ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see their own connections
CREATE POLICY "Allow users to see their own connections"
ON public.brokerage_connections
FOR SELECT
USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own connections
CREATE POLICY "Allow users to insert their own connections"
ON public.brokerage_connections
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to update their own connections
CREATE POLICY "Allow users to update their own connections"
ON public.brokerage_connections
FOR UPDATE
USING (auth.uid() = user_id);

-- Create policy to allow users to delete their own connections
CREATE POLICY "Allow users to delete their own connections"
ON public.brokerage_connections
FOR DELETE
USING (auth.uid() = user_id);
