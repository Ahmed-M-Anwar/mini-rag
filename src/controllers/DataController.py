from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # 1MB

    def validate_uploaded_file(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_filename(self, original_filename: str, project_id: str) -> str:
        random_string = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_filename = self.get_cleaned_filename(filename=original_filename)
        new_filename = os.path.join(project_path, random_string + "_" + cleaned_filename)
        
        while os.path.exists(new_filename):
            random_string = self.generate_random_string()
            new_filename = os.path.join(project_path, random_string + "_" + cleaned_filename)

        return new_filename
        

    def get_cleaned_filename(self, filename: str) -> str:
        # Remove any characters that are not alphanumeric, underscores, hyphens, or dots
        cleaned_filename = re.sub(r'[^\w.]', '', filename.strip())
        cleaned_filename = cleaned_filename.replace(" ", "_")
        return cleaned_filename