-- Migration 1: the shuttle's routes, one row for each.
--   id             the route's id in addresses, such as blue-loop (TEXT PRIMARY KEY)
--   name           the name riders see, such as Blue Loop
--   every_minutes  how often a bus comes, in minutes
--   first_bus      the first bus of the day, as text, such as 7:00
--   last_bus       the last bus of the day, as text, such as 22:50
CREATE TABLE routes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    every_minutes INTEGER NOT NULL,
    first_bus TEXT NOT NULL,
    last_bus TEXT NOT NULL
);

INSERT INTO routes (id, name, every_minutes, first_bus, last_bus) VALUES
    ('blue-loop', 'Blue Loop', 10, '7:00', '22:50'),
    ('gold-line', 'Gold Line', 15, '7:00', '22:45'),
    ('night-owl', 'Night Owl', 20, '19:00', '1:40');
