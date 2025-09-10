# db/repositories/items_repo.py
from PySide6.QtSql import QSqlQuery

def list_item_names(db) -> list[str]:
    names = []
    q = QSqlQuery(db)
    q.exec("SELECT item_name FROM items ORDER BY item_name")
    while q.next():
        names.append(str(q.value(0)))
    return names

def get_item_id_by_name(db, name: str) -> int | None:
    q = QSqlQuery(db)
    q.prepare("SELECT item_id FROM items WHERE item_name=:n")
    q.bindValue(":n", name)
    q.exec()
    return int(q.value(0)) if q.next() else None

def add_item(db, name: str) -> bool:
    q = QSqlQuery(db)
    q.prepare("INSERT INTO items(item_name) VALUES(:n)")
    q.bindValue(":n", name)
    return q.exec()  # UNIQUE違反時はFalse
