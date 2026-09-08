CREATE TABLE medication_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    elder_name TEXT NOT NULL,
    medication_status TEXT NOT NULL,
    notes TEXT
);