import os

import pytest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("SECRET_KEY", "test-only-signing-key-for-sou-api-tests-0001")
os.environ.setdefault("POSTGRES_PASSWORD", "test-only-postgres-password")
os.environ.setdefault("SEED_ADMIN_EMAIL", "admin@silveroakuni.ac.in")
os.environ.setdefault("SEED_ADMIN_PASSWORD", "Admin@SOU2026")
os.environ.setdefault("SEED_ADMIN_NAME", "Campus Super Admin")
os.environ.setdefault("SEED_FACULTY_EMAIL", "faculty@silveroakuni.ac.in")
os.environ.setdefault("SEED_FACULTY_PASSWORD", "Faculty@SOU2026")
os.environ.setdefault("SEED_FACULTY_NAME", "Dr. Meera Shah (Faculty)")
os.environ.setdefault("SEED_STUDENT_EMAIL", "student@silveroakuni.ac.in")
os.environ.setdefault("SEED_STUDENT_PASSWORD", "Student@SOU2026")
os.environ.setdefault("SEED_STUDENT_NAME", "Test Student")

from app.db.init_db import init_database
from app.db.base import Base
from app.db.session import async_engine


@pytest.fixture(autouse=True)
async def setup_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await init_database()
