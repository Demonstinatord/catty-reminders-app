from fastapi import FastAPI, HTTPException
from tinydb import TinyDB, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="TinyDB Network Service")
db = TinyDB('/data/reminder_db.json')

_lists = db.table('reminder_lists')
_items = db.table('reminder_items')
_selected = db.table('selected_lists')

class ListPayload(BaseModel):
    name: str
    owner: str

@app.post("/lists")
def create_list(payload: ListPayload):
    return {"id": _lists.insert({'name': payload.name, 'owner': payload.owner})}

@app.get("/lists")
def get_lists(owner: str):
    res = _lists.search(Query().owner == owner)
    return [{"id": r.doc_id, **r} for r in res]

@app.get("/lists/{list_id}")
def get_list(list_id: int, owner: str):
    res = _lists.get(doc_id=list_id)
    if not res: raise HTTPException(status_code=404)
    if res['owner'] != owner: raise HTTPException(status_code=403)
    return {"id": list_id, **res}

@app.get("/selected")
def get_selected_list_id(owner: str):
    res = _selected.search(Query().owner == owner)
    # Если пользователя еще нет в таблице выбранных списков, возвращаем None
    if not res or len(res) == 0: 
        return {"list_id": None}
    
    # ИСПРАВЛЕНО: берем первый документ из списка [0], а затем его ключ 'list_id'
    return {"list_id": res[0]['list_id']}
@app.delete("/lists/{list_id}")
def delete_list(list_id: int):
    _lists.remove(doc_ids=[list_id])
    _items.remove(Query().list_id == list_id)
    return {"status": "ok"}
