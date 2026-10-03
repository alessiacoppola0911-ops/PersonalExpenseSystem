PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK (TRIM(name) <> '')
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT NOT NULL
        CHECK (
            length(expense_date) = 10
            AND substr(expense_date, 5, 1) = '-'
            AND substr(expense_date, 8, 1) = '-'
        ),
    amount REAL NOT NULL CHECK (amount > 0),
    category_id INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL
        CHECK (
            length(month) = 7
            AND substr(month, 5, 1) = '-'
        ),
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    UNIQUE (month, category_id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Dati di esempio
INSERT OR IGNORE INTO categories (name) VALUES
('Alimentari'),
('Trasporti'),
('Salute'),
('Svago');

INSERT INTO expenses (expense_date, amount, category_id, description)
SELECT '2026-10-01', 25.00, id, 'Pranzo' FROM categories WHERE name = 'Alimentari'
AND NOT EXISTS (SELECT 1 FROM expenses WHERE expense_date='2026-10-01' AND amount=25.00 AND description='Pranzo');

INSERT INTO expenses (expense_date, amount, category_id, description)
SELECT '2026-10-02', 42.50, id, 'Spesa supermercato' FROM categories WHERE name = 'Alimentari'
AND NOT EXISTS (SELECT 1 FROM expenses WHERE expense_date='2026-10-02' AND amount=42.50 AND description='Spesa supermercato');

INSERT INTO expenses (expense_date, amount, category_id, description)
SELECT '2026-10-02', 12.00, id, 'Biglietto autobus' FROM categories WHERE name = 'Trasporti'
AND NOT EXISTS (SELECT 1 FROM expenses WHERE expense_date='2026-10-02' AND amount=12.00 AND description='Biglietto autobus');

INSERT OR IGNORE INTO budgets (month, category_id, amount)
SELECT '2026-10', id, 300.00 FROM categories WHERE name='Alimentari';

INSERT OR IGNORE INTO budgets (month, category_id, amount)
SELECT '2026-10', id, 100.00 FROM categories WHERE name='Trasporti';
