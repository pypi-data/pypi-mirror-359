from datetime import datetime, timezone
from typing import Any, Callable, Dict, Type, TypeVar, Generic, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import ColumnElement, Select, asc, desc, func, literal_column, or_
from db.base_model import BaseModel
from db.base_query_filter import BaseQueryFilter
from db.base_query_params import BaseQueryParams
from db.base_query_search import BaseQuerySearch
from db.exception import handle_db_exceptions
from db.paginated_model import PaginatedModel
from db.repository.abstract_repository import AbstractRepository

T = TypeVar("T", bound=BaseModel)

class SQLAlchemyRepository(AbstractRepository[T], Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    @handle_db_exceptions(allow_return=True)
    async def get_one_by_id(self, id: int | str) -> Optional[T]:
        stmt = select(self.model).filter_by(id=id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    @handle_db_exceptions(allow_return=True)
    async def get_many_by_ids(self, ids: List[int | str]) -> List[T]:
        if not ids:
            return []
        stmt = select(self.model).filter(self.model.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    @handle_db_exceptions(allow_return=True)
    async def get_one(self, query_filter: Optional[BaseQueryFilter] = None) ->  Optional[T]:
        filters = (query_filter.filters if query_filter else {}) or {}
    
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False
    
        stmt = select(self.model).filter_by(**filters)
    
        result = await self.session.execute(stmt)
        return result.scalars().first()


    @handle_db_exceptions(allow_return=True, return_data=[])
    async def get_all(
        self,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> List[T]:

        stmt: Select = select(self.model)

        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False

        if filters:
            stmt = stmt.filter_by(**filters)

        if query_params and query_params.sort:
            for field_name, direction in query_params.sort:
                col = getattr(self.model, field_name, None)
                if col is not None:
                    stmt = stmt.order_by(asc(col) if direction.lower() == "asc"     else desc(col))

        if query_params:
            stmt = stmt.offset(query_params.skip)
            if query_params.limit is not None:
                stmt = stmt.limit(query_params.limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_paginated(
        self,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> PaginatedModel[T]:
        query_params = query_params or BaseQueryParams()
        total = await self.count(query_filter)
        items = await self.get_all(query_params, query_filter)

        return PaginatedModel[T](
            data=items,
            total=total,
            skip=query_params.skip,
            limit=query_params.limit,
            count=len(items)
        )

    @handle_db_exceptions()
    async def create(self, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    @handle_db_exceptions()
    async def update(self, id: int | str, obj_in: dict) -> Optional[T]:
        db_obj = await self.get_one_by_id(id=id)
        if not db_obj:
            return None
        
        for k, v in obj_in.items():
            setattr(db_obj, k, v)

        db_obj.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    @handle_db_exceptions()
    async def delete(self, id: int | str, hard_delete: bool = False) -> bool:
        db_obj = await self.get_one_by_id(id=id)
        if not db_obj:
            return False
        
        if hard_delete:
            await self.session.delete(db_obj)
            await self.session.flush()
        else:
            db_obj.is_deleted = True
            await self.session.flush()
            await self.session.refresh(db_obj)       
        
        return True
    
    async def undelete(self, id: int | str) -> bool:
        db_obj = await self.get_one_by_id(id)
        if db_obj and db_obj.is_deleted:
            db_obj.is_deleted = False
            await self.session.flush()
            await self.session.refresh(db_obj)
            return True
        return False
    
    async def exists(self, query_filter: Optional[BaseQueryFilter] = None) -> bool:        
        return await self.get_one(query_filter) is not None
    
    async def count(self, query_filter: Optional[BaseQueryFilter] = None) -> int:
        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False
        stmt = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or 0
    
    @handle_db_exceptions(allow_return=True)
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str,     Any]]:
        group_by = None
        filters = []
        order_by = []
        projections = []
        skip = None
        limit = None
        label_map = {}
    
        for stage in pipeline:
            if "$match" in stage:
                match_filters = stage["$match"]
                for field, value in match_filters.items():
                    column = getattr(self.model, field, None)
                    if column is None:
                        raise AttributeError(f"Model {self.model.__name__} has no   field '{field}'")
                    filters.append(column == value)
    
            elif "$group" in stage:
                group_stage = stage["$group"]
                group_key = group_stage.get("_id")
                if group_key is None:
                    raise ValueError("Missing '_id' in $group stage")
                if isinstance(group_key, str) and group_key.startswith("$"):
                    group_key = group_key[1:]
                group_by = getattr(self.model, group_key, None)
                if group_by is None:
                    raise ValueError(f"Invalid group_by field: {group_key}")
    
                projections.append(group_by.label(group_key))
                label_map[group_key] = group_by.label(group_key)
    
                for alias, expr in group_stage.items():
                    if alias == "_id":
                        continue
                    for op, field in expr.items():
                        col = getattr(self.model, field, None)
                        if col is None:
                            raise AttributeError(f"Model {self.model.__name__} has  no field '{field}'")
                        if op == "$sum":
                            agg_col = func.sum(col).label(alias)
                        elif op == "$avg":
                            agg_col = func.avg(col).label(alias)
                        elif op == "$count":
                            agg_col = func.count(col).label(alias)
                        elif op == "$min":
                            agg_col = func.min(col).label(alias)
                        elif op == "$max":
                            agg_col = func.max(col).label(alias)
                        else:
                            raise ValueError(f"Unsupported aggregation operation:   {op}")
                        projections.append(agg_col)
                        label_map[alias] = agg_col
    
            elif "$project" in stage:
                project_stage = stage["$project"]
                new_projections = []
                for alias, include in project_stage.items():
                    if include != 1:
                        continue
                    if alias in label_map:
                        new_projections.append(label_map[alias])
                    elif hasattr(self.model, alias):
                        new_projections.append(getattr(self.model, alias))
                    else:
                        raise ValueError(f"Field {alias} not found in projections   or model")
                projections = new_projections
                if not projections:
                    raise ValueError("No projections defined after $project")
    
            elif "$sort" in stage:
                sort_stage = stage["$sort"]
                for field, direction in sort_stage.items():
                    col = label_map.get(field, getattr(self.model, field, None))
                    if col is None:
                        raise AttributeError(f"Cannot sort by unknown field '{field}    '")
                    order_by.append(asc(col) if direction == 1 else desc(col))
    
            elif "$skip" in stage:
                skip = stage["$skip"]
    
            elif "$limit" in stage:
                limit = stage["$limit"]
    
        # Finalize select statement
        if projections:
            stmt = select(*projections)
        else:
            stmt = select(self.model)
    
        if filters:
            stmt = stmt.filter(*filters)
        if group_by is not None:
            stmt = stmt.group_by(group_by)
        if order_by:
            stmt = stmt.order_by(*order_by)
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
    
        result = await self.session.execute(stmt)
        return [dict(row._mapping) for row in result.fetchall()]



    @handle_db_exceptions(allow_return=True, return_data=[])
    async def text_search(
        self,
        query_search: BaseQuerySearch,
        query_params: Optional[BaseQueryParams] = None,
        query_filter: Optional[BaseQueryFilter] = None
    ) -> List[T]:
        filters = (query_filter.filters if query_filter else {}) or {}
        if not (query_filter and query_filter.include_deleted):
            filters["is_deleted"] = False
    
        # Base query
        stmt = select(self.model).filter_by(**filters)
    
        # Build simple LIKE filter over multiple fields
        if query_search.search_text and query_search.projection_fields:
            search_text = f"%{query_search.search_text.lower()}%"
            like_conditions = [
                getattr(self.model, field).ilike(search_text)
                for field in query_search.projection_fields
                if hasattr(self.model, field)
            ]
            if like_conditions:
                stmt = stmt.where(or_(*like_conditions))
    
        # Sorting
        if query_params and query_params.sort:
            for field, direction in query_params.sort:
                col = getattr(self.model, field, None)
                if col is not None:
                    stmt = stmt.order_by(asc(col) if direction.lower() == "asc"     else desc(col))
    
        # Pagination
        if query_params:
            stmt = stmt.offset(query_params.skip)
            if query_params.limit is not None:
                stmt = stmt.limit(query_params.limit)
    
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
