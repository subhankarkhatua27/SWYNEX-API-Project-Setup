import json
import logging
from pathlib import Path
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from .db import SessionLocal, init_db
    from .tables import User
except ImportError:
    try:
        from app.db import SessionLocal, init_db
        from app.tables import User
    except ImportError:
        from db import SessionLocal, init_db
        from tables import User

logger = logging.getLogger("swynex_api")

DEFAULT_SAMPLE_USERS = [
    {"name": "Alex Mercer", "email": "alex.mercer@example.com"},
    {"name": "Beatriz Santos", "email": "beatriz.santos@example.com"},
    {"name": "Carlos Chen", "email": "carlos.chen@example.com"},
    {"name": "Diana Prince", "email": "diana.prince@example.com"},
    {"name": "Ethan Hunt", "email": "ethan.hunt@example.com"},
    {"name": "Fiona Gallagher", "email": "fiona.gallagher@example.com"},
]


def load_sample_users() -> List[dict]:
    """Attempts to load sample users from sample_data.json, fallback to defaults."""
    candidate_paths = [
        Path(__file__).parent.parent / "sample_data.json",
        Path(__file__).parent.parent.parent / "sample_data.json",
        Path("sample_data.json"),
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception as e:
                logger.warning(f"Could not parse sample data from {p}: {e}")
    return DEFAULT_SAMPLE_USERS


def seed_database(db: Session) -> Dict[str, int]:
    """
    Populates database with sample users idempotently.
    Users with emails that already exist are skipped.
    """
    sample_users = load_sample_users()
    created_count = 0

    for item in sample_users:
        name = item.get("name", "").strip()
        email = item.get("email", "").strip().lower()
        if not name or not email:
            continue

        existing = db.scalars(select(User).where(User.email == email)).first()
        if not existing:
            new_user = User(name=name, email=email)
            db.add(new_user)
            created_count += 1

    if created_count > 0:
        db.commit()

    total_count = db.query(User).count()
    return {"users_created": created_count, "total_users": total_count}


def run_seed():
    """CLI runner for database seeding."""
    init_db()
    with SessionLocal() as db:
        stats = seed_database(db)
        print(f"[SUCCESS] Database seeding complete!")
        print(f" - Newly created users : {stats['users_created']}")
        print(f" - Total users in database: {stats['total_users']}")


if __name__ == "__main__":
    run_seed()

