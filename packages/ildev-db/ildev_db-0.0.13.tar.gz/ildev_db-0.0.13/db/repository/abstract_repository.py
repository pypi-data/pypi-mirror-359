from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, List, Optional

from db.base_query_filter import BaseQueryFilter
from db.base_query_params import BaseQueryParams
from db.base_query_search import BaseQuerySearch
from db.paginated_model import PaginatedModel

T = TypeVar("T")

class AbstractRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_one_by_id(self, id) -> Optional[T]: ...

    @abstractmethod
    async def get_many_by_ids(self, ids: List) -> List[T]: ...

    @abstractmethod
    async def get_one(self, query_filter: Optional[BaseQueryFilter] = None) -> Optional[T]: ...

    @abstractmethod
    async def get_all(self, query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None) -> List[T]: ...

    @abstractmethod
    async def get_paginated(self, query_params: Optional[BaseQueryParams] = None, query_filter: Optional[BaseQueryFilter] = None) -> PaginatedModel[T]: ...

    @abstractmethod
    async def create(self, obj_in) -> T: ...

    @abstractmethod
    async def update(self, id, obj_in) -> Optional[T]: ...

    @abstractmethod
    async def delete(self, id, hard_delete: bool = False) -> bool: ...
    
    @abstractmethod
    async def undelete(self, id) -> bool: ...

    @abstractmethod
    async def exists(self, query_filter: Optional[BaseQueryFilter] = None) -> bool: ...

    @abstractmethod
    async def count(self, query_filter: Optional[BaseQueryFilter] = None) -> int: ...

    @abstractmethod
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def text_search(self, query_search: BaseQuerySearch, query_params: Optional[BaseQueryParams] = None, query_filter: Optional[BaseQueryFilter] = None
    ) -> List[T]: ...
