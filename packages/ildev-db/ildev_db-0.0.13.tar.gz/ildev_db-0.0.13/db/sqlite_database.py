from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from db.base_database import BaseDatabase
from log.base_log import BaseLog

class SQLiteDatabase(BaseDatabase):
    def __init__(self, database_url: str, logger: BaseLog):
        super().__init__(logger)
        self.database_url = database_url
        self.engine = None
        self.session_factory = None

    async def initialize(self):
        """Initialize the engine and session factory."""
        self.logger.info(f"Creating SQLite engine for {self.database_url}")
        self.engine = create_async_engine(self.database_url, echo=False)
        self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provides an async database session generator."""
        async def get_db() -> AsyncGenerator[AsyncSession, None]:
            if self.session_factory is None:
                raise RuntimeError("Session factory is not initialized. Call 'initialize()' before using the database.")
            async with self.session_factory() as session:
                self.logger.debug("Creating new SQLite session")
                try:
                    yield session
                except Exception as e:
                    self.logger.error(f"Error in SQLite session: {e}")
                    raise
                finally:
                    self.logger.debug("Closing SQLite session")
        return get_db()
