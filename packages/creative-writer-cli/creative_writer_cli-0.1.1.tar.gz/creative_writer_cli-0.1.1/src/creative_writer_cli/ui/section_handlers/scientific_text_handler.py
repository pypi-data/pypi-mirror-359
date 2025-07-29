from .base_section_handler import BaseSectionHandler
from ..display.views import display_text_content
from ..wizards.generic_wizards import get_simple_text_input
import questionary

class ScientificTextHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_text_content(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        if not data or not data[0]: # If no content or empty string
            choices.insert(0, "Add Content")
        else:
            choices.insert(0, "Edit Content")
            choices.insert(1, "Delete Content")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Content":
            new_content = get_simple_text_input("Enter content:")
            if new_content:
                data = [new_content] # Overwrite existing or set new content
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Content added.[/green]")
        elif action == "Edit Content":
            if not data:
                self.console.print("[yellow]No content to edit.[/yellow]")
                return
            new_content = get_simple_text_input("Edit content:", default_value=data[0] if data else "")
            if new_content:
                data = [new_content]
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Content updated.[/green]")
        elif action == "Delete Content":
            if not data:
                self.console.print("[yellow]No content to delete.[/yellow]")
                return
            if questionary.confirm("Are you sure you want to delete the content?").ask():
                data = []
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Content deleted.[/green]")
