# db/repositories/items_repo.py
from PySide6.QtSql import QSqlQuery

class ItemsRepository:

    def __init__(self,db):
        self.db=db

    def list_item_names(self) -> list[str]:
        names = []
        q = QSqlQuery(self.db)
        q.exec("SELECT item_name FROM items ORDER BY item_name")
        while q.next():
            names.append(str(q.value(0)))
        return names

    def get_item_id_by_name(self,name: str) -> int | None:
        q = QSqlQuery(self.db)
        q.prepare("SELECT item_id FROM items WHERE item_name=:n")
        q.bindValue(":n", name)
        q.exec()
        return int(q.value(0)) if q.next() else None

    def get_item_by_id(self, item_id: int) -> dict | None:
        q = QSqlQuery(self.db)
        q.prepare("""
            SELECT item_id, item_name, price, freshness, sales_class, item_type, is_active
            FROM items WHERE item_id=:id
        """)
        q.bindValue(":id", item_id)
        if q.exec() and q.next():
            return {
                "item_id": int(q.value(0)),
                "item_name": str(q.value(1)),
                "price": int(q.value(2)),
                "freshness": int(q.value(3)),
                "sales_class": str(q.value(4)),
                "item_type": str(q.value(5)),
                "is_active": int(q.value(6)),
            }
        return None


    def add_item(self, data: dict) -> bool:
        """商品を追加"""
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT INTO items(item_name, price, freshness, sales_class, item_type, is_active)
            VALUES(:name, :price, :freshness, :sales_class, :item_type, :is_active)
        """)
        q.bindValue(":name", data["item_name"])
        q.bindValue(":price", data["price"])
        q.bindValue(":freshness", data["freshness"])
        q.bindValue(":sales_class", data["sales_class"])
        q.bindValue(":item_type", data["item_type"])
        q.bindValue(":is_active", data["is_active"])
        return q.exec()
    
    def delete_item(self, item_id: int) -> bool:
        """商品削除"""
        q = QSqlQuery(self.db)
        q.prepare("DELETE FROM items WHERE item_id=:id")
        q.bindValue(":id", item_id)
        return q.exec()

    def update_item(self, item_id: int, data: dict) -> bool:
        """商品情報を更新"""
        q = QSqlQuery(self.db)
        q.prepare("""
            UPDATE items
            SET item_name=:name, price=:price, freshness=:freshness,
                sales_class=:sales_class, item_type=:item_type, is_active=:is_active
            WHERE item_id=:id
        """)
        q.bindValue(":id", item_id)
        q.bindValue(":name", data["item_name"])
        q.bindValue(":price", data["price"])
        q.bindValue(":freshness", data["freshness"])
        q.bindValue(":sales_class", data["sales_class"])
        q.bindValue(":item_type", data["item_type"])
        q.bindValue(":is_active", data["is_active"])
        return q.exec()