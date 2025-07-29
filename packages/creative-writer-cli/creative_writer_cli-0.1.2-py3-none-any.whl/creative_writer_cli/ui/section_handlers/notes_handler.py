from .base_section_handler import BaseSectionHandler
from ..display.tables import display_notes_table
from ..display.views import view_details
from ..wizards.novel_wizards import get_note_idea_input
import questionary

class NotesHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_notes_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Note/Idea")
        if data:
            choices.insert(1, "Edit Note/Idea")
            choices.insert(2, "Delete Note/Idea")
            choices.insert(3, "View Note/Idea Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Note/Idea":
            new_item_data = get_note_idea_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Note/Idea added.[/green]")
        elif action == "Edit Note/Idea":
            if not data:
                self.console.print("[yellow]No notes/ideas to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select note/idea to edit:", choices=[item.get("title", f"Note/Idea {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_note_idea_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Note/Idea updated.[/green]")
        elif action == "Delete Note/Idea":
            if not data:
                self.console.print("[yellow]No notes/ideas to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select note/idea to delete:", choices=[item.get("title", f"Note/Idea {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("title") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Note/Idea deleted.[/green]")
        elif action == "View Note/Idea Details":
            view_details(data, "title")
