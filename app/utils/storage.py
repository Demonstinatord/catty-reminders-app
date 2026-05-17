"""
This module handles the persistence layer (the "database") for the app.
"""

import requests
from app.utils.exceptions import NotFoundException, ForbiddenException
from pydantic import BaseModel
from typing import List, Optional

# --------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------

class ReminderItem(BaseModel):
    id: int
    list_id: int
    description: str
    completed: bool


class ReminderList(BaseModel):
    id: int
    owner: str
    name: str


class SelectedList(BaseModel):
    id: int
    owner: str
    name: str
    items: List[ReminderItem]


# --------------------------------------------------------------------------------
# ReminderStorage Class
# --------------------------------------------------------------------------------

class ReminderStorage:
    
    def __init__(self, owner: str, db_url: str = "http://db-service:8181",db_path: Optional[str] = None, **kwargs) -> None:
        import os
        self.owner = owner
        self.db_url = os.getenv("DB_URL",db_url)

    # --- Reminder Lists ---
    def create_list(self, name: str) -> int:
        res = requests.post(f"{self.db_url}/lists", json={'name': name, 'owner': self.owner})
        return res.json()["id"]

    def get_lists(self) -> List[ReminderList]:
        res = requests.get(f"{self.db_url}/lists", params={"owner": self.owner})
        return [ReminderList(**item) for item in res.json()]

    def get_list(self, list_id: int) -> ReminderList:
        res = requests.get(f"{self.db_url}/lists/{list_id}", params={"owner": self.owner})
        if res.status_code == 404: 
            raise NotFoundException()
        if res.status_code == 403: 
            raise ForbiddenException()
        return ReminderList(**res.json())

    def delete_list(self, list_id: int) -> None:
        self.get_list(list_id)  # Проверка прав доступа
        requests.delete(f"{self.db_url}/lists/{list_id}")

    def delete_lists(self) -> None:
        for rem_list in self.get_lists():
            self.delete_list(rem_list.id)

    def update_list_name(self, list_id: int, new_name: str) -> None:
        self.get_list(list_id)
        requests.put(f"{self.db_url}/lists/{list_id}", json={'name': new_name, 'owner': self.owner})

    # --- Reminder Items ---
    def add_item(self, list_id: int, description: str) -> int:
        self.get_list(list_id)
        res = requests.post(f"{self.db_url}/items", json={'list_id': list_id, 'description': description})
        return res.json()["id"]

    def get_item(self, item_id: int) -> ReminderItem:
        res = requests.get(f"{self.db_url}/items/{item_id}")
        if res.status_code == 404: 
            raise NotFoundException()
        item_data = res.json()
        self.get_list(item_data['list_id'])  # Проверка прав owner
        return ReminderItem(**item_data)

    def get_items(self, list_id: int) -> List[ReminderItem]:
        self.get_list(list_id)
        res = requests.get(f"{self.db_url}/items", params={"list_id": list_id})
        return [ReminderItem(**item) for item in res.json()]

    def delete_item(self, item_id: int) -> None:
        self.get_item(item_id)
        requests.delete(f"{self.db_url}/items/{item_id}")

    def strike_item(self, item_id: int) -> None:
        self.get_item(item_id)
        requests.put(f"{self.db_url}/items/{item_id}/strike")

    def update_item_description(self, item_id: int, new_description: str) -> None:
        self.get_item(item_id)
        requests.put(f"{self.db_url}/items/{item_id}/description", params={"description": new_description})

    # --- Selected Lists ---
    def get_selected_list_id(self) -> Optional[int]:
        res = requests.get(f"{self.db_url}/selected", params={"owner": self.owner})
        return res.json()["list_id"]

    def set_selected_list(self, list_id: Optional[int]) -> None:
        requests.post(f"{self.db_url}/selected", json={'owner': self.owner, 'list_id': list_id})
    def get_selected_list(self) -> Optional[SelectedList]:
        list_id = self.get_selected_list_id()
        
        # Если у пользователя еще нет выбранного списка (новый аккаунт)
        if list_id is None:
            lists = self.get_lists()
            # Если списков вообще нет — создаем первый список по умолчанию
            if not lists:
                list_id = self.create_list("Основной")
            else:
                list_id = lists[0].id
            # Запоминаем его как выбранный
            self.set_selected_list(list_id)

        try:
            reminder_list = self.get_list(list_id)
            reminder_items = self.get_items(list_id)
            return SelectedList(
                id=reminder_list.id, 
                owner=reminder_list.owner, 
                name=reminder_list.name, 
                items=reminder_items
            )
        except:
            # Если список был записан, но в базе его нет (синхронизация)
            self.set_selected_list(None)
            return None

    def reset_selected_after_delete(self, deleted_id: int) -> None:
        current_selected = self.get_selected_list_id()
        if current_selected == deleted_id:
            lists = self.get_lists()
            next_id = lists[0].id if lists else None
            self.set_selected_list(next_id)
