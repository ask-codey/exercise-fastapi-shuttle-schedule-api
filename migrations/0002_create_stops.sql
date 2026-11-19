-- Migration 2: each route's stops, in the order a bus reaches them.
--   route_id  the route the stop is on: REFERENCES routes (id)
--   position  1 for the route's first stop, 2 for the next, and so on
--   name      the stop's name, such as library
CREATE TABLE stops (
    route_id TEXT NOT NULL REFERENCES routes (id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (route_id, position)
);

INSERT INTO stops (route_id, position, name) VALUES
    ('blue-loop', 1, 'library'),
    ('blue-loop', 2, 'science-hall'),
    ('blue-loop', 3, 'stadium'),
    ('blue-loop', 4, 'north-dorms'),
    ('gold-line', 1, 'library'),
    ('gold-line', 2, 'union'),
    ('gold-line', 3, 'rec-center'),
    ('gold-line', 4, 'south-dorms'),
    ('night-owl', 1, 'library'),
    ('night-owl', 2, 'union'),
    ('night-owl', 3, 'north-dorms'),
    ('night-owl', 4, 'south-dorms');
