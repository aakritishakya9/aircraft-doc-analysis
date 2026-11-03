import sqlite3
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """
    Manages SQLite configuration tracking for aircraft components,
    revision history, and engineering review audit trails.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "data", "fleet_inventory.db")
        else:
            self.db_path = db_path
            
        if self.db_path != ":memory:" and os.path.dirname(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        if self.db_path == ":memory:":
            if not hasattr(self, "_memory_conn") or self._memory_conn is None:
                self._memory_conn = sqlite3.connect(":memory:")
                self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Components table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                component_id TEXT PRIMARY KEY,
                component_name TEXT NOT NULL,
                ata_chapter TEXT NOT NULL,
                current_revision TEXT NOT NULL,
                status TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Document Revisions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_ref TEXT NOT NULL,
                revision TEXT NOT NULL,
                pub_date TEXT,
                component_id TEXT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (component_id) REFERENCES components(component_id)
            )
            """)

            # Engineering Changes table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS engineering_changes (
                change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                previous_spec TEXT,
                updated_spec TEXT,
                severity TEXT NOT NULL,
                doc_impact TEXT,
                review_status TEXT DEFAULT 'Pending Review',
                reviewer_name TEXT,
                review_comments TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (component_id) REFERENCES components(component_id)
            )
            """)

            # Fleet Aircraft table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fleet_aircraft (
                tail_number TEXT PRIMARY KEY,
                msn INTEGER NOT NULL,
                aircraft_model TEXT NOT NULL,
                engine_type TEXT NOT NULL,
                total_hours INTEGER NOT NULL,
                total_cycles INTEGER NOT NULL,
                base_hub TEXT NOT NULL
            )
            """)

            # Part Interchangeability table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS part_interchangeability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id TEXT NOT NULL,
                previous_pn TEXT,
                updated_pn TEXT,
                interchangeability_class TEXT NOT NULL,
                action_required TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # ERP Outbox table for MRO synchronization (AMOS / SAP / Maximo)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS erp_outbox (
                dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                eco_number TEXT NOT NULL,
                target_erp TEXT NOT NULL,
                sync_status TEXT NOT NULL,
                transaction_id TEXT,
                payload_json TEXT,
                dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Seed default fleet components if table is empty
            cursor.execute("SELECT COUNT(*) FROM components")
            if cursor.fetchone()[0] == 0:
                sample_components = [
                    ("HYD-001", "Hydraulic Pump", "ATA 29", "Rev 01", "Updated"),
                    ("LG-002", "Landing Gear Actuator", "ATA 32", "Rev 01", "Under Review"),
                    ("FUEL-003", "Main Tank Fuel Pump", "ATA 28", "Rev 03", "Updated"),
                    ("ENG-004", "FADEC Electronic Controller", "ATA 73", "Rev 02", "Compliant"),
                    ("FLT-005", "Elevator Power Control Unit", "ATA 27", "Rev 01", "Under Review")
                ]
                cursor.executemany("""
                INSERT INTO components (component_id, component_name, ata_chapter, current_revision, status)
                VALUES (?, ?, ?, ?, ?)
                """, sample_components)
            conn.commit()

    def get_all_components(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM components ORDER BY component_id", conn)

    def update_component_status(self, component_id: str, new_revision: str, new_status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO components (component_id, component_name, ata_chapter, current_revision, status, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(component_id) DO UPDATE SET
                current_revision = excluded.current_revision,
                status = excluded.status,
                last_updated = CURRENT_TIMESTAMP
            """, (component_id, "Aircraft Component", "ATA General", new_revision, new_status))
            conn.commit()

    def log_document_revision(self, doc_ref: str, revision: str, pub_date: str, component_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO document_revisions (doc_ref, revision, pub_date, component_id)
            VALUES (?, ?, ?, ?)
            """, (doc_ref, revision, pub_date, component_id))
            conn.commit()

    def log_engineering_changes(self, change_items: List[Dict[str, Any]]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for item in change_items:
                cursor.execute("""
                INSERT INTO engineering_changes 
                (component_id, parameter_name, previous_spec, updated_spec, severity, doc_impact, review_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get("component_id", "GEN-001"),
                    item.get("affected_parameter", "General Spec"),
                    item.get("previous_specification", "N/A"),
                    item.get("updated_specification", "N/A"),
                    item.get("severity", "MEDIUM"),
                    item.get("potential_doc_impact", "AMM / IPC"),
                    item.get("review_status", "Pending Review")
                ))
            conn.commit()

    def get_engineering_changes(self, component_id: Optional[str] = None) -> pd.DataFrame:
        with self._get_connection() as conn:
            if component_id:
                query = "SELECT * FROM engineering_changes WHERE component_id = ? ORDER BY change_id DESC"
                return pd.read_sql_query(query, conn, params=(component_id,))
            else:
                query = "SELECT * FROM engineering_changes ORDER BY change_id DESC"
                return pd.read_sql_query(query, conn)

    def update_review_signoff(self, change_id: int, review_status: str, reviewer_name: str, comments: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE engineering_changes
            SET review_status = ?, reviewer_name = ?, review_comments = ?, timestamp = CURRENT_TIMESTAMP
            WHERE change_id = ?
            """, (review_status, reviewer_name, comments, change_id))
            conn.commit()

    def get_summary_metrics(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM document_revisions")
            total_docs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM engineering_changes")
            total_changes = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM engineering_changes WHERE review_status = 'Pending Review'")
            pending_reviews = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT component_id) FROM engineering_changes")
            components_affected = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM engineering_changes WHERE severity = 'HIGH' OR severity = 'CRITICAL'")
            critical_changes = cursor.fetchone()[0]

            return {
                "total_docs_processed": total_docs,
                "revisions_detected": total_docs,
                "changes_identified": total_changes,
                "components_affected": components_affected,
                "pending_reviews": pending_reviews,
                "critical_changes": critical_changes
            }

    def log_erp_dispatch(self, eco_number: str, target_erp: str, status: str, transaction_id: str, payload_json: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO erp_outbox (eco_number, target_erp, sync_status, transaction_id, payload_json)
            VALUES (?, ?, ?, ?, ?)
            """, (eco_number, target_erp, status, transaction_id, payload_json))
            conn.commit()

    def get_erp_dispatches(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM erp_outbox ORDER BY dispatch_id DESC", conn)
