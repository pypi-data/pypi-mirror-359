from .base_section_handler import BaseSectionHandler
from ..display.tables import display_chapters_table
from ..display.views import view_details
from ..wizards.scientific_wizards import get_chapter_input
import questionary

class ChapterHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_chapters_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Chapter Content")
        if data:
            choices.insert(1, "Edit Chapter Content")
            choices.insert(2, "Delete Chapter Content")
            choices.insert(3, "View Chapter Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Chapter Content":
            new_item_data = get_chapter_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Chapter Content added.[/green]")
        elif action == "Edit Chapter Content":
            if not data:
                self.console.print("[yellow]No chapter content to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select chapter to edit:", choices=[item.get("chapter_title", f"Chapter {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("chapter_title") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_chapter_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Chapter Content updated.[/green]")
        elif action == "Delete Chapter Content":
            if not data:
                self.console.print("[yellow]No chapter content to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select chapter to delete:", choices=[item.get("chapter_title", f"Chapter {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("chapter_title") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Chapter Content deleted.[/green]")
        elif action == "View Chapter Details":
            view_details(data, "chapter_title")
