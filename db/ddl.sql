--psql -h localhost -p 5433 -U postgres -d postgres -f db/ddl.sql
CREATE EXTENSION if not exists "uuid-ossp";


DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
user_id UUID PRIMARY KEY DEFAULT public.uuid_generate_v4(),
username VARCHAR(255) UNIQUE NOT NULL,
name VARCHAR(255) NOT NULL,
surname VARCHAR(255) NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
hashed_password VARCHAR(255) UNIQUE NOT NULL,
roles VARCHAR(50) ARRAY NOT NULL DEFAULT '{ROLE_USER}',
is_active BOOLEAN DEFAULT false
);