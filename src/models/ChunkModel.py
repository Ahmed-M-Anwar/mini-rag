from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: Object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        chunk_dict = chunk.dict(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(chunk_dict)
        chunk._id = result.inserted_id
        return chunk

    async def get_chunks_by_project_id(self, project_id: str):
        cursor = self.collection.find({"chunk_project_id": project_id}).sort("chunk_order", 1)
        chunks = []
        async for chunk in cursor:
            chunks.append(DataChunk(**chunk))
        return chunks

    async def delete_chunks_by_project_id(self, project_id: str):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

    async def delete_chunk(self, chunk_id: str):
        result = await self.collection.delete_one({"_id": chunk_id})
        return result.deleted_count

    async def update_chunk(self, chunk_id: str, updated_chunk: DataChunk):
        updated_chunk_dict = updated_chunk.dict(by_alias=True, exclude_unset=True)
        result = await self.collection.update_one({"_id": chunk_id}, {"$set": updated_chunk_dict})
        return result.modified_count

    async def get_chunk(self, chunk_id: str):
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if chunk:
            return DataChunk(**chunk)
        return None

    async def get_chunks(self, page: int = 1, page_size: int = 10):
        total_chunks = await self.collection.count_documents({})
        total_pages = total_chunks // page_size
        if total_chunks % page_size != 0:
            total_pages += 1

        skip = (page - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        chunks = []
        async for chunk in cursor:
            chunks.append(DataChunk(**chunk))
        return chunks, total_pages

    async def get_all_chunks(self, project_id: str, page: int = 1, page_size: int = 10):
        total_chunks = await self.collection.count_documents({"chunk_project_id": project_id})
        total_pages = total_chunks // page_size
        if total_chunks % page_size != 0:
            total_pages += 1

        skip = (page - 1) * page_size
        cursor = self.collection.find({"chunk_project_id": project_id}).skip(skip).limit(page_size)
        chunks = []
        async for chunk in cursor:
            chunks.append(DataChunk(**chunk))
        return chunks, total_pages

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
            await self.collection.bulk_write(operations)

        return len(chunks)

    