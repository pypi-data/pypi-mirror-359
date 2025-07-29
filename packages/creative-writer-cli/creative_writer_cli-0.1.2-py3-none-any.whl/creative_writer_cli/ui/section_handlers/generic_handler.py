from .base_section_handler import BaseSectionHandler
import questionary
import json

class GenericHandler(BaseSectionHandler):
    def display_content(self, data: list):
        self.console.print(json.dumps(data, indent=2))

    def get_choices(self, data: list) -> list:
        choices = ["Back to Project Menu"]
        choices.insert(0, "Add Item")
        if data:
            choices.insert(1, "Edit Item")
            choices.insert(2, "Delete Item")
        return choices

    def handle_section_action(self, project_name: str, section_name: str, action: str, data: list):
        if action == "Add Item":
            new_item = questionary.text("Enter new item (in JSON format or simple text):").ask()
            if new_item:
                try:
                    data.append(json.loads(new_item))
                except json.JSONDecodeError:
                    data.append(new_item)
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Item added.[/green]")
        elif action == "Edit Item":
            if not data:
                self.console.print("[yellow]No items to edit.[/yellow]")
                return
            selected_item_display = questionary.select("Select item to edit:", choices=[f"{i}: {json.dumps(item)}" for i, item in enumerate(data)]).ask()
            if selected_item_display:
                index = int(selected_item_display.split(':')[0])
                new_value = questionary.text("Enter new value:", default=json.dumps(data[index])).ask()
                try:
                    updated_item_data = json.loads(new_value)
                except json.JSONDecodeError:
                    updated_item_data = new_value
                
                if updated_item_data:
                    data[index] = updated_item_data
                    self.project_repository.save_section_content(project_name, section_name, data)
                    self.console.print("[green]Item updated.[/green]")
        elif action == "Delete Item":
            if not data:
                self.console.print("[yellow]No items to delete.[/yellow]")
                return
            selected_item_display = questionary.select("Select item to delete:", choices=[f"{i}: {json.dumps(item)}" for i, item in enumerate(data)]).ask()
            if selected_item_display:
                index = int(selected_item_display.split(':')[0])
                del data[index]
                self.project_repository.save_section_content(project_name, section_name, data)
                self.console.print("[green]Item deleted.[/green]")
