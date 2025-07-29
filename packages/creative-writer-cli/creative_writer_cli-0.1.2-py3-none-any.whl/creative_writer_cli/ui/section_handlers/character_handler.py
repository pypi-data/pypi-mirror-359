from .base_section_handler import BaseSectionHandler
from ..display.tables import display_character_table
from ..display.views import view_details
from ..wizards.novel_wizards import get_character_input
import questionary

class CharacterHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_character_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Character")
        if data: # Only show edit/delete/view if there's data
            choices.insert(1, "Edit Character")
            choices.insert(2, "Delete Character")
            choices.insert(3, "View Character Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Character":
            new_item_data = get_character_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Character added.[/green]")
        elif action == "Edit Character":
            if not data:
                self.console.print("[yellow]No characters to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select character to edit:", choices=[item.get("name", f"Character {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_character_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Character updated.[/green]")
        elif action == "Delete Character":
            if not data:
                self.console.print("[yellow]No characters to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select character to delete:", choices=[item.get("name", f"Character {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Character deleted.[/green]")
        elif action == "View Character Details":
            view_details(data, "Name")
