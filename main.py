from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "personal_expenses.db"
SQL_PATH = BASE_DIR / "sql" / "database.sql"


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database() -> None:
    with connect_db() as conn:
        conn.executescript(SQL_PATH.read_text(encoding="utf-8"))


def read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Errore: il valore non può essere vuoto.")


def read_positive_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
            if value <= 0:
                print("Errore: l'importo deve essere maggiore di zero.")
                continue
            return value
        except ValueError:
            print("Errore: inserire un importo numerico valido.")


def read_date(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Errore: usare il formato YYYY-MM-DD.")


def read_month(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            print("Errore: usare il formato YYYY-MM.")


def get_category_id(conn: sqlite3.Connection, name: str) -> int | None:
    row = conn.execute(
        "SELECT id FROM categories WHERE LOWER(name) = LOWER(?)", (name,)
    ).fetchone()
    return row[0] if row else None


def manage_categories() -> None:
    name = read_non_empty("Nome della categoria: ")
    with connect_db() as conn:
        if get_category_id(conn, name) is not None:
            print("La categoria esiste già.")
            return
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            print("Categoria inserita correttamente.")
        except sqlite3.IntegrityError as exc:
            print(f"Errore durante l'inserimento della categoria: {exc}")


def insert_expense() -> None:
    expense_date = read_date("Data (YYYY-MM-DD): ")
    amount = read_positive_float("Importo: ")
    category_name = read_non_empty("Nome della categoria: ")
    description = input("Descrizione facoltativa: ").strip() or None

    with connect_db() as conn:
        category_id = get_category_id(conn, category_name)
        if category_id is None:
            print("Errore: la categoria non esiste.")
            return
        try:
            conn.execute(
                """
                INSERT INTO expenses (expense_date, amount, category_id, description)
                VALUES (?, ?, ?, ?)
                """,
                (expense_date, amount, category_id, description),
            )
            print("Spesa inserita correttamente.")
        except sqlite3.IntegrityError as exc:
            print(f"Errore durante l'inserimento della spesa: {exc}")


def define_budget() -> None:
    month = read_month("Mese (YYYY-MM): ")
    category_name = read_non_empty("Nome della categoria: ")
    amount = read_positive_float("Importo del budget: ")

    with connect_db() as conn:
        category_id = get_category_id(conn, category_name)
        if category_id is None:
            print("Errore: la categoria non esiste.")
            return
        conn.execute(
            """
            INSERT INTO budgets (month, category_id, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(month, category_id)
            DO UPDATE SET amount = excluded.amount
            """,
            (month, category_id, amount),
        )
        print("Budget mensile salvato correttamente.")


def report_totals_by_category() -> None:
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT c.name, COALESCE(SUM(e.amount), 0) AS total_spent
            FROM categories c
            LEFT JOIN expenses e ON e.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name
            """
        ).fetchall()
    print("\nCategoria                 Totale Speso")
    print("----------------------------------------")
    for name, total in rows:
        print(f"{name:<25} {total:>10.2f}")


def report_monthly_vs_budget() -> None:
    month = read_month("Mese da visualizzare (YYYY-MM): ")
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT c.name,
                   b.amount AS budget,
                   COALESCE(SUM(e.amount), 0) AS spent
            FROM budgets b
            JOIN categories c ON c.id = b.category_id
            LEFT JOIN expenses e
              ON e.category_id = b.category_id
             AND substr(e.expense_date, 1, 7) = b.month
            WHERE b.month = ?
            GROUP BY c.id, c.name, b.amount
            ORDER BY c.name
            """,
            (month,),
        ).fetchall()

    if not rows:
        print("Nessun budget definito per il mese indicato.")
        return

    print(f"\nMese: {month}")
    for category, budget, spent in rows:
        status = "SUPERAMENTO BUDGET" if spent > budget else "NEL BUDGET"
        print(f"Categoria: {category}")
        print(f"Budget: {budget:.2f}")
        print(f"Speso: {spent:.2f}")
        print(f"Stato: {status}")
        print("-")


def report_all_expenses() -> None:
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT e.expense_date, c.name, e.amount, COALESCE(e.description, '')
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            ORDER BY e.expense_date ASC, e.id ASC
            """
        ).fetchall()

    print("\nData        Categoria                 Importo  Descrizione")
    print("----------------------------------------------------------------")
    for expense_date, category, amount, description in rows:
        print(f"{expense_date:<11} {category:<25} {amount:>8.2f}  {description}")


def reports_menu() -> None:
    while True:
        print("""
-------------------------
 MENU DEI REPORT
-------------------------
1. Totale spese per categoria
2. Spese mensili vs budget
3. Elenco completo delle spese ordinate per data
4. Ritorna al menu principale
-------------------------""")
        choice = input("Inserisci la tua scelta: ").strip()
        match choice:
            case "1":
                report_totals_by_category()
            case "2":
                report_monthly_vs_budget()
            case "3":
                report_all_expenses()
            case "4":
                return
            case _:
                print("Scelta non valida. Riprovare.")


def main() -> None:
    initialize_database()
    print("Benvenuto nel Sistema di Gestione delle Spese Personali e del Budget!")

    while True:
        print("""
-------------------------
 SISTEMA SPESE PERSONALI
-------------------------
1. Gestione Categorie
2. Inserisci Spesa
3. Definisci Budget Mensile
4. Visualizza Report
5. Esci
-------------------------""")
        choice = input("Inserisci la tua scelta: ").strip()
        match choice:
            case "1":
                manage_categories()
            case "2":
                insert_expense()
            case "3":
                define_budget()
            case "4":
                reports_menu()
            case "5":
                print("Arrivederci!")
                break
            case _:
                print("Scelta non valida. Riprovare.")


if __name__ == "__main__":
    main()
