#!/usr/bin/env python3
"""Referenz-Implementierung: Persistenz + Journal + Self-Healing fuer den
DSF-Agenten-Schwarm.

Umsetzung des State-Contract (siehe STATE_CONTRACT.md):

- Boot-/State-Datei als JSON (klein, menschenlesbar, 1 Schreiber).
- Append-only Journal in SQLite (mehr-schreiber-sicher via WAL + busy_timeout),
  weil mehrere Agenten gleichzeitig schreiben - eine gemeinsame JSON-Datei
  wuerde hier Races/Korruption erzeugen.
- Self-Healing: beim Start Journal lesen, letzten unfertigen/fehlgeschlagenen
  Schritt erkennen und ab dem letzten verifizierten Checkpoint fortsetzen.

Nur Standardbibliothek (json, sqlite3, ...). Keine Secrets - nur Referenzen.

Ausfuehren:
    python journal.py --selftest      # demonstriert den kompletten Ablauf
    python journal.py --show          # zeigt aktuellen Zustand + Journal
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE / "journal.db"
DEFAULT_STATE = HERE / "session-state.json"

TERMINAL_OK = {"done", "recovered"}
NEEDS_RECOVERY = {"in_progress", "failed"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Journal:
    """Append-only Ereignis-Journal in SQLite (mehr-schreiber-tauglich)."""

    def __init__(self, db_path: Path = DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # WAL + busy_timeout: mehrere Agenten koennen gefahrlos gleichzeitig
        # schreiben; SQLite serialisiert die Schreibzugriffe selbst.
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS journal (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts            TEXT NOT NULL,
                    session_id    TEXT NOT NULL,
                    agent         TEXT NOT NULL,
                    model         TEXT,
                    model_version TEXT,
                    action        TEXT NOT NULL,
                    inputs_ref    TEXT,
                    result        TEXT,
                    verified_by   TEXT,
                    status        TEXT NOT NULL,
                    checkpoint    INTEGER NOT NULL DEFAULT 0,
                    error         TEXT,
                    next_step     TEXT
                );
                """
            )

    def append(self, session_id: str, agent: str, action: str, status: str,
               *, model: str = "", model_version: str = "", inputs_ref: str = "",
               result: str = "", verified_by: str = "", checkpoint: bool = False,
               error: str = "", next_step: str = "") -> int:
        """Ein Ereignis anhaengen. Gibt die Journal-ID zurueck."""
        if status not in (TERMINAL_OK | NEEDS_RECOVERY):
            raise ValueError(f"ungueltiger status: {status}")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO journal (ts, session_id, agent, model, model_version,
                    action, inputs_ref, result, verified_by, status, checkpoint,
                    error, next_step)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (_now(), session_id, agent, model, model_version, action,
                 inputs_ref, result, verified_by, status, 1 if checkpoint else 0,
                 error, next_step),
            )
            return int(cur.lastrowid)

    def last(self, session_id: str) -> sqlite3.Row | None:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM journal WHERE session_id=? ORDER BY id DESC LIMIT 1",
                (session_id,),
            )
            return cur.fetchone()

    def last_good_checkpoint(self, session_id: str) -> sqlite3.Row | None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT * FROM journal
                WHERE session_id=? AND checkpoint=1 AND status IN ('done','recovered')
                ORDER BY id DESC LIMIT 1
                """,
                (session_id,),
            )
            return cur.fetchone()

    def entries(self, session_id: str) -> list[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM journal WHERE session_id=? ORDER BY id ASC",
                (session_id,),
            )
            return list(cur.fetchall())


def load_state(path: Path = DEFAULT_STATE) -> dict:
    if Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0",
        "session_id": str(uuid.uuid4()),
        "created_at": _now(),
        "updated_at": _now(),
        "commander": {"human": True, "name": "DSF Commander"},
        "last_good_checkpoint": "",
        "agents": [],
        "journal": [],
    }


def save_state(state: dict, path: Path = DEFAULT_STATE) -> None:
    state["updated_at"] = _now()
    Path(path).write_text(json.dumps(state, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def recover(journal: Journal, session_id: str) -> dict:
    """Self-Healing-Entscheidung fuer den Start eines Agenten.

    Gibt zurueck, ob fortgesetzt werden kann und ab welchem Checkpoint.
    """
    last = journal.last(session_id)
    if last is None:
        return {"action": "start_fresh", "reason": "kein Journal vorhanden"}

    if last["status"] in TERMINAL_OK:
        return {"action": "continue", "reason": "letzter Schritt sauber abgeschlossen",
                "from_id": last["id"]}

    # in_progress oder failed -> auf letzten verifizierten Checkpoint zuruecksetzen
    cp = journal.last_good_checkpoint(session_id)
    if cp is None:
        return {"action": "restart", "reason": "kein sicherer Checkpoint gefunden",
                "failed_status": last["status"]}
    return {
        "action": "resume_from_checkpoint",
        "reason": f"letzter Schritt '{last['status']}' -> Wiederaufsetzen",
        "checkpoint_id": cp["id"],
        "checkpoint_result": cp["result"],
        "next_step": cp["next_step"],
    }


# --------------------------------------------------------------------------
# Selbsttest: demonstriert Persistenz, Zero-Trust-Verifikation und Self-Healing
# --------------------------------------------------------------------------
def selftest() -> int:
    db = HERE / "journal.selftest.db"
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(db) + suffix)
        if p.exists():
            p.unlink()

    j = Journal(db)
    sid = str(uuid.uuid4())
    print(f"[selftest] session_id = {sid}")

    # 1) Recherche-Agent liefert (unverifiziert)
    j.append(sid, "researcher", "Recherche DSGVO-Kriterien", "done",
             model="gemini-3.1-pro", model_version="gemini-3.1-pro-2026-07",
             result="5 Kriterien vorgeschlagen",
             next_step="durch Commander verifizieren")

    # 2) Zero-Trust: Commander verifiziert -> Checkpoint
    j.append(sid, "dsf-commander", "Verifikation gegen Primaerquellen", "recovered",
             model="claude-opus-4-6", model_version="claude-opus-4-6-20260501",
             result="3/5 belegt, 2 verworfen", verified_by="dsf-commander",
             checkpoint=True, error="2 Kriterien ohne Quelle (Halluzination)",
             next_step="worker: belegte Kriterien umsetzen")

    # 3) Worker faengt an ... und stuerzt ab (in_progress bleibt haengen)
    j.append(sid, "worker", "Umsetzung Kriterien (GPU)", "in_progress",
             model="qwen-32b", model_version="qwen2.5-32b-instruct",
             next_step="Schritt 1/3")
    print("[selftest] Absturz simuliert (worker haengt auf 'in_progress').")

    # 4) Neustart -> Self-Healing
    decision = recover(j, sid)
    print("[selftest] Recovery-Entscheidung:")
    print(json.dumps(decision, indent=2, ensure_ascii=False))

    ok = (decision["action"] == "resume_from_checkpoint"
          and decision.get("next_step") == "worker: belegte Kriterien umsetzen")
    print(f"[selftest] {'OK' if ok else 'FEHLER'}: "
          f"Wiederaufsetzen ab letztem verifizierten Checkpoint.")

    # aufraeumen
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(db) + suffix)
        if p.exists():
            p.unlink()
    return 0 if ok else 1


def show(session_id: str | None) -> int:
    j = Journal()
    state = load_state()
    sid = session_id or state.get("session_id", "")
    print(f"session_id = {sid}")
    for e in j.entries(sid):
        cp = " [CP]" if e["checkpoint"] else ""
        print(f"  #{e['id']} {e['ts']} {e['agent']:<14} {e['status']:<12}{cp} "
              f"{e['action']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="DSF State/Journal/Self-Healing Referenz")
    ap.add_argument("--selftest", action="store_true",
                    help="kompletten Ablauf demonstrieren")
    ap.add_argument("--show", action="store_true", help="Zustand + Journal zeigen")
    ap.add_argument("--session", help="session_id fuer --show")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.show:
        return show(args.session)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
