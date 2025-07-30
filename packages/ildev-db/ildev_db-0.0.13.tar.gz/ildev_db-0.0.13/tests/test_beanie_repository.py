from pydantic import BaseModel
import pytest
from typing import List
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from db.base_doc import BaseDoc
from db.base_query_filter import BaseQueryFilter
from db.base_query_params import BaseQueryParams
from db.base_query_search import BaseQuerySearch
from db.paginated_model import PaginatedModel
from db.repository.beanie_repository import BeanieRepository

# Define test document
class TestBeanieModel(BaseDoc):
    name: str
    quantity: int
    price: float = 0.0
    tags: List[str] = []

    class Settings(BaseDoc.Settings):
        name = "test_beanie_models"
        indexes = [
            [("name", "text")],
        ]

# ✅ Fixture for initializing Beanie
@pytest.fixture()
async def init_beanie_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client.get_database("test_db"),
        document_models=[TestBeanieModel]
    )
    yield
    # Cleanup: drop collection after the test
    await TestBeanieModel.get_motor_collection().drop()

# ✅ Repository fixture
@pytest.fixture()
async def beanie_repository(init_beanie_db) -> BeanieRepository[TestBeanieModel]:
    return BeanieRepository(TestBeanieModel)

# ✅ Fixture with initial data
@pytest.fixture()
async def beanie_repository_with_data(beanie_repository):
    test_data = [
    {"name": "Apple", "quantity": 2, "price": 3.5},
    {"name": "Banana", "quantity": 5, "price": 1.2},
    {"name": "Orange", "quantity": 3, "price": 2.5},
    {"name": "Mango", "quantity": 2, "price": 5.0},
    ]
    for item in test_data:
        await beanie_repository.create(TestBeanieModel(**item))
    return beanie_repository


@pytest.mark.asyncio
async def test_get_one_by_id(beanie_repository):
    created = await beanie_repository.create(TestBeanieModel(name="Get by ID", quantity=5))
    found = await beanie_repository.get_one_by_id(created.id)
    assert found is not None
    assert found.id == created.id

@pytest.mark.asyncio
async def test_get_many_by_ids(beanie_repository):
    a = await beanie_repository.create(TestBeanieModel(name="A", quantity=1))
    b = await beanie_repository.create(TestBeanieModel(name="B", quantity=2))
    ids = [a.id, b.id]
    results = await beanie_repository.get_many_by_ids(ids)
    assert len(results) == 2
    assert all(item.id in ids for item in results)

@pytest.mark.asyncio
async def test_create_and_get_one(beanie_repository):
    obj = TestBeanieModel(name="Item 1", quantity=5)
    created = await beanie_repository.create(obj)
    assert created.name == obj.name

    filter_by_name = BaseQueryFilter(filters={"name": "Item 1"})
    found = await beanie_repository.get_one(query_filter=filter_by_name)
    assert found is not None
    assert found.name == "Item 1"

@pytest.mark.asyncio
async def test_get_all(beanie_repository_with_data):
    query_params = BaseQueryParams()
    result = await beanie_repository_with_data.get_all(query_params=query_params)
    assert isinstance(result, list)
    assert len(result) >= 2

@pytest.mark.asyncio
async def test_get_all_with_limit(beanie_repository_with_data):
    query_params = BaseQueryParams(limit=1)
    result = await beanie_repository_with_data.get_all(query_params=query_params)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_get_all_with_filter(beanie_repository_with_data):
    query_params = BaseQueryParams()
    query_filter = BaseQueryFilter(filters={"quantity": 2}, include_deleted=False)
    result = await beanie_repository_with_data.get_all(
        query_params=query_params, query_filter=query_filter
    )
    assert len(result) == 2

@pytest.mark.asyncio
async def test_get_paginated(beanie_repository_with_data):
    query_params = BaseQueryParams(skip=0, limit=2)
    paginated = await beanie_repository_with_data.get_paginated(query_params=query_params)
    assert isinstance(paginated, PaginatedModel)
    assert len(paginated.data) <= 2
    assert paginated.total >= len(paginated.data)
    assert paginated.count == len(paginated.data)

@pytest.mark.asyncio
async def test_update(beanie_repository):
    created = await beanie_repository.create(TestBeanieModel(name="To Update", quantity=20))
    
    class UpdateModel(BaseModel):
        quantity: int

    updated = await beanie_repository.update(id=created.id, obj_in=UpdateModel(quantity=50))
    assert updated.quantity == 50

@pytest.mark.asyncio
async def test_delete(beanie_repository):
    created = await beanie_repository.create(TestBeanieModel(name="To Delete", quantity=1))
    result = await beanie_repository.delete(id=created.id)
    assert result is True

    filter_by_id = BaseQueryFilter(filters={"_id": created.id})
    deleted = await beanie_repository.get_one(query_filter=filter_by_id)
    assert deleted is None


@pytest.mark.asyncio
async def test_undelete(beanie_repository):
    created = await beanie_repository.create(TestBeanieModel(name="Soft Delete", quantity=9))
    await beanie_repository.delete(created.id)
    undeleted = await beanie_repository.undelete(created.id)
    assert undeleted is True
    found = await beanie_repository.get_one_by_id(created.id)
    assert found is not None
    assert found.is_deleted is False

@pytest.mark.asyncio
async def test_exists(beanie_repository):
    await beanie_repository.create(TestBeanieModel(name="ToExist", quantity=99))
    exists = await beanie_repository.exists(BaseQueryFilter(filters={"name": "ToExist"}))
    assert exists is True


@pytest.mark.asyncio
async def test_aggregate_match_only(beanie_repository_with_data):
    pipeline = [{"$match": {"quantity": {"$eq": 2}}}]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert all(doc["quantity"] == 2 for doc in result)

@pytest.mark.asyncio
async def test_aggregate_group_sum(beanie_repository_with_data):
    pipeline = [
        {"$group": {"_id": None, "total_quantity": {"$sum": "$quantity"}}}
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert "total_quantity" in result[0]

@pytest.mark.asyncio
async def test_aggregate_project_fields(beanie_repository_with_data):
    pipeline = [
        {"$project": {"name": 1, "price": 1, "_id": 0}}
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    for doc in result:
        assert "name" in doc
        assert "price" in doc
        assert "_id" not in doc

@pytest.mark.asyncio
async def test_aggregate_sort(beanie_repository_with_data):
    pipeline = [{"$sort": {"price": -1}}]
    result = await beanie_repository_with_data.aggregate(pipeline)
    prices = [doc["price"] for doc in result]
    assert prices == sorted(prices, reverse=True)

@pytest.mark.asyncio
async def test_aggregate_limit(beanie_repository_with_data):
    pipeline = [{"$limit": 2}]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert len(result) == 2

@pytest.mark.asyncio
async def test_aggregate_unwind(beanie_repository_with_data):
    # Assuming one document has a list field: {"tags": ["fruit", "fresh"]}
    await beanie_repository_with_data.create({"name": "Tagged", "tags": ["fruit", "fresh"], "quantity": 1, "price": 1.0})
    pipeline = [
        {"$match": {"name": "Tagged"}},
        {"$unwind": "$tags"},
        {"$project": {"tags": 1, "_id": 0}}
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert all("tags" in doc for doc in result)
    assert len(result) == 2  # Because of 2 tags

@pytest.mark.asyncio
async def test_aggregate_facet(beanie_repository_with_data):
    pipeline = [
        {
            "$facet": {
                "cheap": [{"$match": {"price": {"$lt": 3}}}],
                "expensive": [{"$match": {"price": {"$gte": 3}}}]
            }
        }
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert "cheap" in result[0]
    assert "expensive" in result[0]

@pytest.mark.asyncio
async def test_aggregate_count(beanie_repository_with_data):
    pipeline = [
        {"$match": {"quantity": {"$gte": 1}}},
        {"$count": "total_items"}
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert "total_items" in result[0]

@pytest.mark.asyncio
async def test_aggregate_add_fields(beanie_repository_with_data):
    pipeline = [
        {"$addFields": {"total_price": {"$multiply": ["$quantity", "$price"]}}},
        {"$project": {"total_price": 1, "_id": 0}}
    ]
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert all("total_price" in doc for doc in result)

@pytest.mark.asyncio
async def test_aggregate_pipeline_empty(beanie_repository_with_data):
    pipeline = []
    result = await beanie_repository_with_data.aggregate(pipeline)
    assert isinstance(result, list)  # Should return all documents

@pytest.mark.asyncio
async def test_aggregate_invalid_stage(beanie_repository_with_data):
    pipeline = [{"$invalidStage": {"key": "value"}}]
    with pytest.raises(Exception):
        await beanie_repository_with_data.aggregate(pipeline)

@pytest.mark.asyncio
async def test_text_search(beanie_repository):
    # Make sure text index is created in Settings.indexes
    await beanie_repository.create(TestBeanieModel(name="searchable text", quantity=5))
    query_search = BaseQuerySearch(search_text="searchable")
    query_params = BaseQueryParams()
    query_filter = BaseQueryFilter()
    results = await beanie_repository.text_search(query_search, query_params, query_filter)
    assert isinstance(results, list)
    assert any("searchable" in doc.name for doc in results)
