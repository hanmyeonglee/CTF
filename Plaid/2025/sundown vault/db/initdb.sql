CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA sundown;

CREATE TABLE sundown.user (
	id text primary key,
	password text not null, -- bcrypt
	check (length(id) >= 3 and length(id) <= 32)
);

CREATE TABLE sundown.token (
	token text primary key default gen_random_uuid(),
	user_id text not null references sundown.user(id),
	created_at timestamptz not null default now()
);

CREATE TABLE sundown.secret (
	id text primary key default gen_random_uuid(),
	owner_id text not null references sundown.user(id),
	name text not null,
	secret text not null,
	reveal_at timestamptz not null,
	created_at timestamptz not null default now()
);

CREATE FUNCTION ms_to_timestamp(ms float8) RETURNS timestamptz AS $$
  SELECT to_timestamp(ms / 1000.0) AT TIME ZONE 'UTC';
$$ STRICT IMMUTABLE LANGUAGE sql;

CREATE FUNCTION timestamp_to_ms(ts timestamptz) RETURNS float8 AS $$
  SELECT extract(epoch from ts) * 1000.0;
$$ STRICT IMMUTABLE LANGUAGE sql;

------------------------------------------------------------------------------

INSERT INTO sundown.user (id, password) VALUES ('plaid', 'no-login');
INSERT INTO sundown.secret(id, owner_id, name, secret, reveal_at) VALUES ('13371337-1337-1337-1337-133713371337', 'plaid', 'Flag', 'PCTF{test_flag}', '2026-04-10 21:00:00+00');
