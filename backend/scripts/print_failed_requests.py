from datetime import datetime
from sqlalchemy import select

from src.storage.db import SessionLocal
from src.models.db_models import Request


def main():
    with SessionLocal() as session:
        stmt = select(Request).order_by(Request.updated_at.desc()).limit(50)
        rows = session.execute(stmt).scalars().all()
        for r in rows:
            if r.status.name == "FAILED":
                print("ID:", r.id)
                print("Status:", r.status)
                print("Detail:", r.detail)
                print("Updated:", r.updated_at)
                print("---")


if __name__ == "__main__":
    main()
