# app/database/database.py

# ══════════════════════════════════════════════════════════════
# DATABASE SCHEMA REFERENCE
# ══════════════════════════════════════════════════════════════
#
# TABLE: employees
#   employee_id       TEXT  PRIMARY KEY
#   first_name        TEXT  NOT NULL
#   last_name         TEXT  NOT NULL
#   email             TEXT  UNIQUE NOT NULL
#   department_id     INT   FK → departments.department_id
#   vacation_allocated INT  DEFAULT 0
#   vacation_used      INT  DEFAULT 0
#   sick_allocated     INT  DEFAULT 0
#   sick_used          INT  DEFAULT 0
#
# TABLE: departments
#   department_id     INT   PRIMARY KEY AUTOINCREMENT
#   department_name   TEXT  UNIQUE NOT NULL
#
# TABLE: schedules
#   shift_id          INT   PRIMARY KEY AUTOINCREMENT
#   employee_id       TEXT  FK → employees.employee_id
#   shift_date        TEXT  (ISO format: YYYY-MM-DD)
#   start_time        TEXT  (HH:MM)
#   end_time          TEXT  (HH:MM)
#
# TABLE: audit_logs
#   log_id            INT   PRIMARY KEY AUTOINCREMENT
#   timestamp         TEXT  NOT NULL
#   employee_id       TEXT  FK → employees.employee_id (nullable)
#   user_message      TEXT  NOT NULL
#   classified_intent TEXT  NOT NULL
#   confidence_score  REAL  NOT NULL
#   final_response    TEXT  NOT NULL
#
# RELATIONSHIPS:
#   employees  ── schedules    (one employee → many shifts)
#   departments ── employees   (one department → many employees)
#   employees  ── audit_logs   (one employee → many log entries)
# ══════════════════════════════════════════════════════════════

import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class EmployeeNotFoundError(Exception):
    """Raised when a query targets an employee_id that does not exist in the database."""


class DatabaseClient:
    """
    Manages queries against the HR SQLite database.
    All methods open and close their own connections via context managers.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = (
            str(Path(db_path).resolve())
            if db_path
            else str(Path(__file__).resolve().parent / "hr_database.db")
        )

    # ── Public query interface ─────────────────────────────────────────────────

    def fetch_leave_data(self, employee_id: str) -> Tuple[int, int, int, int]:
        """
        Returns (vacation_left, vacation_allocated, sick_left, sick_allocated).

        Raises:
            EmployeeNotFoundError: If no record exists for the given employee_id.
            sqlite3.Error: On any database failure.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    (vacation_allocated - vacation_used) AS vacation_left,
                    vacation_allocated,
                    (sick_allocated    - sick_used)      AS sick_left,
                    sick_allocated
                FROM employees
                WHERE employee_id = ?
                """,
                (employee_id,),
            )
            row = cursor.fetchone()

        if row is None:
            raise EmployeeNotFoundError(
                f"database.py DB-001 error: No leave record found for employee_id: {employee_id}"
            )
        return row

    def fetch_schedule_data(self, employee_id: str) -> List[Tuple[str, str, str]]:
        """
        Returns a list of (shift_date, start_time, end_time) ordered by date ascending.
        Returns an empty list if the employee has no scheduled shifts.

        Raises:
            sqlite3.Error: On any database failure.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT shift_date, start_time, end_time
                FROM schedules
                WHERE employee_id = ?
                ORDER BY shift_date ASC
                """,
                (employee_id,),
            )
            return cursor.fetchall()

    def fetch_all_employees(self) -> List[Tuple[str, str, str, str]]:
        """
        Returns all employees as (employee_id, first_name, last_name, department_name).
        JOINs departments to resolve department_id → department_name.

        Raises:
            sqlite3.Error: On any database failure.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    e.employee_id,
                    e.first_name,
                    e.last_name,
                    d.department_name
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                ORDER BY e.last_name ASC, e.first_name ASC
                """
            )
            return cursor.fetchall()

    def get_table_names(self) -> List[str]:
        """
        Returns the names of all tables in the database.
        Useful for connectivity checks and diagnostics.

        Raises:
            sqlite3.Error: On any database failure.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]


# ── Standalone test runner ─────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    db = DatabaseClient()

    tables = db.get_table_names()
    logger.info(f"Tables ({len(tables)}): {tables}")

    employee_id = "EMP-101"
    try:
        leave = db.fetch_leave_data(employee_id)
        logger.info(f"Leave data for {employee_id}: {leave}")
    except EmployeeNotFoundError as e:
        logger.warning(f"database.py DB-002 error: {str(e)}")

    schedule = db.fetch_schedule_data(employee_id)
    logger.info(f"Schedule for {employee_id}: {schedule}")

    employees = db.fetch_all_employees()
    for emp in employees:
        logger.info(f"  {emp[0]} | {emp[1]} {emp[2]} | {emp[3]}")