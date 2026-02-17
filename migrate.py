"""
One-time migration script to add new columns to existing SQLite tables.
Run: python migrate.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "avenir.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- user_profiles ---
    profile_cols = [
        ("income_range", "VARCHAR(40) DEFAULT 'prefer_not_to_say'"),
        ("additional_info", "TEXT"),
        ("has_vehicle", "BOOLEAN DEFAULT 0"),
        ("has_elderly", "BOOLEAN DEFAULT 0"),
        ("has_children", "BOOLEAN DEFAULT 0"),
        ("profile_picture", "TEXT"),
    ]
    for col_name, col_type in profile_cols:
        try:
            c.execute(f"ALTER TABLE user_profiles ADD COLUMN {col_name} {col_type}")
            print(f"  + Added {col_name} to user_profiles")
        except Exception as e:
            print(f"  ~ Skipping user_profiles.{col_name}: {e}")

    # --- infrastructure_data ---
    infra_cols = [
        ("gym_count", "INTEGER DEFAULT 0"),
        ("bar_count", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_type in infra_cols:
        try:
            c.execute(f"ALTER TABLE infrastructure_data ADD COLUMN {col_name} {col_type}")
            print(f"  + Added {col_name} to infrastructure_data")
        except Exception as e:
            print(f"  ~ Skipping infrastructure_data.{col_name}: {e}")

    conn.commit()
    conn.close()
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate()
