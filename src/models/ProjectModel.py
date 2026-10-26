from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: Object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project):
        project_dict = project.dict(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(project_dict)
        project._id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        project = await self.get_project(project_id)
        if project is None:
            new_project = Project(project_id=project_id)
            project = await self.create_project(new_project)
        return project

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        total_projects = await self.collection.count_documents({})
        total_pages = total_projects // page_size
        if total_projects % page_size != 0:
            total_pages += 1

        skip = (page - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        projects = []
        async for project in cursor:
            projects.append(Project(**project))
        return projects, total_pages

    async def get_project(self, project_id: str):
        project = await self.collection.find_one({"project_id": project_id})
        if project:
            return Project(**project)
        return None

    async def update_project(self, project_id: str, updated_project: Project):
        updated_project_dict = updated_project.dict(exclude_unset=True)
        result = await self.collection.update_one(
            {"project_id": project_id}, {"$set": updated_project_dict}
        )
        return result.modified_count

    async def delete_project(self, project_id: str):
        result = await self.collection.delete_one({"project_id": project_id})
        return result.deleted_count