import pytest
import logging
from db.sqlite_database import SQLiteDatabase
from log.base_log import BaseLog

DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"

@pytest.mark.asyncio
async def test_db_connection():
    """Test database session creation."""
    log_folder = "../logs"
    log_file = "tests.log"
    logger = BaseLog(log_folder, log_file, logging.DEBUG)
    db = SQLiteDatabase(DATABASE_URL, logger)

    await db.initialize()

    async for session in db.get_db_session():
        assert session is not None
