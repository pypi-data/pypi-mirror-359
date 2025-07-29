from abc import ABC, abstractmethod
from rich.console import Console

from ...data.repositories.project_repository import ProjectRepository

class BaseSectionHandler(ABC):
    def __init__(self, project_repository: ProjectRepository, console: Console):
        self.project_repository = project_repository
        self.console = console

    @abstractmethod
    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        pass

    @abstractmethod
    def get_choices(self, data: list) -> list:
        pass

    @abstractmethod
    def display_content(self, data: list):
        pass
