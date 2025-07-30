import pytest
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from db.base_query_filter import BaseQueryFilter
from db.repository.sqlalchemy_repository import SQLAlchemyRepository
from db.base_model import BaseModel
from db.base_query_params import BaseQueryParams
from db.exception import BaseRepositoryError

from sqlalchemy.orm import Mapped, mapped_column

class AggregatableModel(BaseModel):
    __tablename__ = "aggregatable_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quantity: Mapped[float] = mapped_column()
    unit_price: Mapped[float] = mapped_column()
    total: Mapped[float] = mapped_column()
    product_id: Mapped[int] = mapped_column(index=True)
    basket_id = Column(Integer)
    
class TestModel(BaseModel):
    __tablename__ = "test_models"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)


# --- Fixtures ---

@pytest.fixture()
def test_repository(test_db: AsyncSession):
    return SQLAlchemyRepository(TestModel, test_db)

@pytest.fixture()
def aggregatable_repository(test_db: AsyncSession):
    return SQLAlchemyRepository(AggregatableModel, test_db)

# --- Tests ---

@pytest.mark.asyncio
async def test_get_one_by_id(test_repository: SQLAlchemyRepository):
    obj = await test_repository.create({"id": 1, "name": "Test Object"})
    retrieved = await test_repository.get_one_by_id(1)
    assert retrieved is not None
    assert retrieved.id == obj.id
    assert retrieved.name == obj.name

@pytest.mark.asyncio
async def test_get_many_by_ids(test_repository: SQLAlchemyRepository):
    for i in range(3):
        await test_repository.create({"id": i, "name": f"Item {i}"})
    result = await test_repository.get_many_by_ids([0, 2])
    assert len(result) == 2
    ids = [r.id for r in result]
    assert 0 in ids and 2 in ids

@pytest.mark.asyncio
async def test_get_one(test_repository: SQLAlchemyRepository):
    await test_repository.create({"id": 1, "name": "Test Object"})
    query_filter = BaseQueryFilter(filters={"name": "Test Object"})
    retrieved = await test_repository.get_one(query_filter)
    assert retrieved is not None
    assert retrieved.name == "Test Object"

@pytest.mark.asyncio
async def test_get_all(test_repository: SQLAlchemyRepository):
    for i in range(10):
        await test_repository.create({"id": i, "name": f"Test Object {i}"})
    result = await test_repository.get_all(BaseQueryParams())
    assert len(result) == 10

@pytest.mark.asyncio
async def test_get_all_limited(test_repository: SQLAlchemyRepository):
    for i in range(10):
        await test_repository.create({"id": i, "name": f"Test Object {i}"})
    params = BaseQueryParams(limit=5)
    result = await test_repository.get_all(params)
    assert len(result) == 5

@pytest.mark.asyncio
async def test_get_all_filtered(test_repository: SQLAlchemyRepository):
    await test_repository.create({"id": 1, "name": "Match Me"})
    query_filter = BaseQueryFilter(filters={"name": "Match Me"})
    result = await test_repository.get_all(query_filter=query_filter)
    assert len(result) == 1
    assert result[0].name == "Match Me"

@pytest.mark.asyncio
async def test_get_paginated(test_repository: SQLAlchemyRepository):
    for i in range(15):
        await test_repository.create({"id": i, "name": f"Object {i}"})
    params = BaseQueryParams(skip=5, limit=5)
    paginated = await test_repository.get_paginated(query_params=params)
    assert paginated.total == 15
    assert len(paginated.data) == 5

@pytest.mark.asyncio
async def test_exists(test_repository: SQLAlchemyRepository):
    await test_repository.create({"id": 1, "name": "Exists"})
    query_filter = BaseQueryFilter(filters={"name": "Exists"})
    assert await test_repository.exists(query_filter) is True

@pytest.mark.asyncio
async def test_undelete(test_repository: SQLAlchemyRepository):
    obj = await test_repository.create({"id": 10, "name": "To Restore"})
    await test_repository.delete(obj.id)
    assert await test_repository.undelete(obj.id) is True

@pytest.mark.asyncio
async def test_aggregate_sum(aggregatable_repository: SQLAlchemyRepository):
    await aggregatable_repository.create({"id": 1, "quantity": 2.0, "unit_price": 10.0, "total": 20.0, "product_id": 1})
    pipeline = [
        {"$group": {"_id": "product_id", "sum_total": {"$sum": "total"}}},
        {"$project": {"sum_total": 1}},
    ]
    result = await aggregatable_repository.aggregate(pipeline)
    assert len(result) == 1
    assert "sum_total" in result[0]

import pytest

@pytest.mark.asyncio
async def test_aggregate_group_sort_limit(aggregatable_repository: SQLAlchemyRepository):
    data = [
        {"id": 1, "quantity": 2.0, "unit_price": 100.0, "total": 200.0, "product_id": 1},
        {"id": 2, "quantity": 1.0, "unit_price": 50.0, "total": 50.0, "product_id": 2},
        {"id": 3, "quantity": 1.5, "unit_price": 50.0, "total": 75.0, "product_id": 2},
        {"id": 4, "quantity": 5.0, "unit_price": 20.0, "total": 100.0, "product_id": 3},
    ]

    for item in data:
        await aggregatable_repository.create(item)

    pipeline = [
        {
            "$group": {
                "_id": "product_id",
                "sum_quantity": {"$sum": "quantity"}
            }
        },
        {
            "$sort": {
                "sum_quantity": -1
            }
        },
        {
            "$limit": 2
        }
    ]

    result = await aggregatable_repository.aggregate(pipeline)

    assert isinstance(result, list)
    assert len(result) == 2
    for row in result:
        assert "product_id" in row  # updated from "_id"
        assert "sum_quantity" in row

