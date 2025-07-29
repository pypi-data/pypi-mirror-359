from .base_section_handler import BaseSectionHandler
from ..display.tables import display_worldbuilding_table
from ..display.views import view_details
from ..wizards.novel_wizards import get_worldbuilding_element_input
import questionary

class WorldbuildingHandler(BaseSectionHandler):
    def display_content(self, data: list):
        display_worldbuilding_table(data)

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Worldbuilding Element")
        if data:
            choices.insert(1, "Edit Worldbuilding Element")
            choices.insert(2, "Delete Worldbuilding Element")
            choices.insert(3, "View Worldbuilding Element Details")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Worldbuilding Element":
            new_item_data = get_worldbuilding_element_input()
            if new_item_data:
                data.append(new_item_data)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Worldbuilding Element added.[/green]")
        elif action == "Edit Worldbuilding Element":
            if not data:
                self.console.print("[yellow]No worldbuilding elements to edit.[/yellow]")
                return
            selected_item_name = questionary.select("Select worldbuilding element to edit:", choices=[item.get("name", f"Worldbuilding Element {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    updated_item_data = get_worldbuilding_element_input(data[index])
                    if updated_item_data:
                        data[index] = updated_item_data
                        self.project_repository.save_section_content(project_name, section_name, data)
                        self.console.print("[green]Worldbuilding Element updated.[/green]")
        elif action == "Delete Worldbuilding Element":
            if not data:
                self.console.print("[yellow]No worldbuilding elements to delete.[/yellow]")
                return
            selected_item_name = questionary.select("Select worldbuilding element to delete:", choices=[item.get("name", f"Worldbuilding Element {i}") for i, item in enumerate(data)]).ask()
            if selected_item_name:
                index = next((i for i, item in enumerate(data) if item.get("name") == selected_item_name), None)
                if index is not None:
                    del data[index]
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Worldbuilding Element deleted.[/green]")
        elif action == "View Worldbuilding Element Details":
            view_details(data, "name")
