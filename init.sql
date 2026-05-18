-- AI ERP Database Initialization Script
-- Creates extensions and initial schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enum types
DO $$ BEGIN
    CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE emission_category AS ENUM (
        'mobile_combustion',
        'stationary_combustion',
        'electricity',
        'refrigerants',
        'waste',
        'water',
        'business_travel',
        'employee_commuting',
        'purchased_goods',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE fuel_type AS ENUM (
        'diesel', 'gasoline', 'lpg', 'natural_gas',
        'coal', 'electricity', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
