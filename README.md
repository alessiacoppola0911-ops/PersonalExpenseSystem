# PersonalExpenseSystem

Sistema console per la gestione di spese personali e budget mensili, sviluppato in Python con database relazionale SQLite.

## Requisiti

- Python 3.10 o successivo
- Nessuna libreria esterna: `sqlite3`, `datetime` e `pathlib` fanno parte della libreria standard di Python

## Struttura

```text
PersonalExpenseSystem/
├── src/
│   └── main.py
├── sql/
│   └── database.sql
├── demo/
│   └── demo_video.mp4
└── README.md
```

## Esecuzione

Dalla cartella principale del progetto eseguire:

```bash
python3 src/main.py
```

Su Windows, se il comando `python3` non è disponibile:

```bash
python src/main.py
```

Al primo avvio il programma crea automaticamente il database `personal_expenses.db` e carica lo schema SQL e i dati di esempio.

## Funzioni disponibili

1. Gestione categorie
2. Inserimento di una spesa
3. Definizione o aggiornamento del budget mensile
4. Report:
   - totale spese per categoria
   - spese mensili vs budget
   - elenco completo delle spese ordinate per data
5. Uscita

## Database

Lo schema SQL include esplicitamente i vincoli richiesti:

- `PRIMARY KEY`
- `FOREIGN KEY`
- `CHECK`
- `UNIQUE`
- `NOT NULL`

## Nota sul menu

Poiché il progetto è realizzato in Python, `print()` e `input()` svolgono il ruolo di output/input testuale, mentre `match/case` (Python 3.10+) svolge il ruolo della selezione multi-caso equivalente allo `switch` mostrato nella traccia.
