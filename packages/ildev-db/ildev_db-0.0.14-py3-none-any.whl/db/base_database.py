from abc import ABC, abstractmethod
from log.base_log import BaseLog

class BaseDatabase(ABC):
    def __init__(self, logger: BaseLog):
        self.logger = logger

    @abstractmethod
    async def initialize(self):
        """Initialize the database connection and related setup."""
        pass
