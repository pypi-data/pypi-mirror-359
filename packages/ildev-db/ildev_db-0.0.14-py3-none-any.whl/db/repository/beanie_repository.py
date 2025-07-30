from datetime import datetime, timezone
from typing import Any, Dict, TypeVar, Generic, List, Optional, Type, Union
from beanie import PydanticObjectId, SortDirection
from pydantic import BaseModel
from db.base_doc import BaseDoc
from db.base_query_filter import BaseQueryFilter
from db.base_query_params import BaseQueryParams
from db.base_query_search import BaseQuerySearch
from db.paginated_model import PaginatedModel
from db.repository.abstract_repository import AbstractRepository

TDoc = TypeVar("TDoc", bound=BaseDoc)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TOut = TypeVar("TOut", bound=BaseModel)

class BeanieRepository(AbstractRepository[TDoc, TCreate, TUpdate, TOut], Generic[TDoc, TCreate, TUpdate, TOut]):
    def __init__(self, model: Type[TDoc], out_model: Type[TOut]):
        self.model = model
        self.out_model = out_model

    async def get_one_by_id(self, id: Union[str, PydanticObjectId]) -> Optional[TOut]:
        doc = await self.model.get(id)
        return self.out_model.model_validate(doc.model_dump()) if doc else None

    async def get_many_by_ids(self, ids: List[Union[str, PydanticObjectId]]) -> List[TOut]:
        docs = await self.model.find({"_id": {"$in": ids}}).to_list()
        return [self.out_model.model_validate(doc.model_dump()) for doc in docs]

    async def get_one(self, query_filter: Optional[BaseQueryFilter] = None) -> Optional[TOut]:
        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False
        doc = await self.model.find_one(filters)
        return self.out_model.model_validate(doc.model_dump()) if doc else None

    async def get_all(
        self,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> List[TOut]:
        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False

        cursor = self.model.find(filters)

        if query_params and query_params.sort:
            sort_fields = [
                (field, SortDirection.ASCENDING if direction.lower() == "asc" else SortDirection.DESCENDING)
                for field, direction in query_params.sort
            ]
            cursor = cursor.sort(sort_fields)

        if query_params:
            cursor = cursor.skip(query_params.skip)
            if query_params.limit is not None:
                cursor = cursor.limit(query_params.limit)

        docs = await cursor.to_list()
        return [self.out_model.model_validate(doc.model_dump()) for doc in docs]

    async def get_paginated(
        self,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> PaginatedModel[TOut]:
        query_params = query_params or BaseQueryParams()
        total = await self.count(query_filter)
        items = await self.get_all(query_params, query_filter)

        return PaginatedModel[TOut](
            data=items,
            total=total,
            skip=query_params.skip,
            limit=query_params.limit,
            count=len(items)
        )

    async def create(self, obj_in: TCreate) -> TOut:
        doc = self.model(**obj_in.model_dump())
        inserted = await doc.insert()
        return self.out_model.model_validate(inserted.model_dump())

    async def update(self, id: Union[str, PydanticObjectId], obj_in: TUpdate) -> Optional[TOut]:
        db_obj = await self.model.get(id)
        if not db_obj or db_obj.is_deleted:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        db_obj.updated_at = datetime.now(timezone.utc)
        await db_obj.save()
        return self.out_model.model_validate(db_obj.model_dump())

    async def delete(self, id: Union[str, PydanticObjectId], hard_delete: bool = False) -> bool:
        db_obj = await self.model.get(id)
        if not db_obj:
            return False

        if hard_delete:
            await db_obj.delete()
        else:
            db_obj.is_deleted = True
            await db_obj.save()
        return True

    async def undelete(self, id: Union[str, PydanticObjectId]) -> bool:
        db_obj = await self.model.get(id)
        if db_obj and db_obj.is_deleted:
            db_obj.is_deleted = False
            await db_obj.save()
            return True
        return False

    async def exists(self, query_filter: Optional[BaseQueryFilter] = None) -> bool:
        return await self.get_one(query_filter) is not None

    async def count(self, query_filter: Optional[BaseQueryFilter] = None) -> int:
        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False
        return await self.model.find(filters).count()

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return await self.model.aggregate(pipeline).to_list()

    async def text_search(
        self,
        query_search: BaseQuerySearch,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> List[TOut]:
        filters = (query_filter.filters if query_filter else {}) or {}
        filters["$text"] = {"$search": query_search.search_text}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False

        projection = (
            {field: 1 for field in query_search.projection_fields}
            if query_search.projection_fields else None
        )
        cursor = self.model.find(filters, projection=projection) if projection else self.model.find(filters)

        if query_params and query_params.sort:
            sort_fields = [
                (field, SortDirection.ASCENDING if direction.lower() == "asc" else SortDirection.DESCENDING)
                for field, direction in query_params.sort
            ]
            cursor = cursor.sort(sort_fields)

        if query_params:
            cursor = cursor.skip(query_params.skip)
            if query_params.limit is not None:
                cursor = cursor.limit(query_params.limit)

        docs = await cursor.to_list()
        return [self.out_model.model_validate(doc.model_dump()) for doc in docs]
