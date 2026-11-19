-- Migration 3: the drivers who sign in to report delays.
--   username       the name a driver signs in with, such as ana: UNIQUE
--   password_hash  the driver's password, hashed with Argon2 by pwdlib, never the password itself
-- The demo driver is ana, whose made-up password is correct-horse-staple.
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

INSERT INTO drivers (username, password_hash) VALUES
    ('ana', '$argon2id$v=19$m=65536,t=3,p=4$wbO2fq56DDIn6wf0+WmJ6g$yIX5GLEJWHk9ygZIZ72+n8/e26Tk+1aR89nyAHAp4c4');
