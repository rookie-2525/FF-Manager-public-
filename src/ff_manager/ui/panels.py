# ui/panels.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton
from dataclasses import dataclass
from enum import Enum

class ButtonType(str, Enum):
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    SAVE = "save"
    REVERT = "revert"
    CLEAR = "clear"

@dataclass(frozen=True)
class Buttons:
    add: QPushButton
    update: QPushButton
    delete: QPushButton
    save: QPushButton
    revert: QPushButton
    clear: QPushButton

    def get(self, kind: ButtonType) -> QPushButton:
        return {
            ButtonType.ADD: self.add,
            ButtonType.UPDATE: self.update,
            ButtonType.DELETE: self.delete,
            ButtonType.SAVE: self.save,
            ButtonType.REVERT: self.revert,
            ButtonType.CLEAR: self.clear,
        }[kind]


def build_form_and_editors(model, header_map, exclude=("id","log_id")):
    form = QFormLayout()
    editors = {}
    rec = model.record()
    for i in range(rec.count()):
        name = rec.fieldName(i)
        if name.lower() in exclude:
            continue
        # ヘッダー日本語化
        model.setHeaderData(i, 1, header_map.get(name, name))  # 1 = Qt.Horizontal
        label = model.headerData(i, 1) or name

        le = QLineEdit()
        le.setObjectName(name)
        form.addRow(label, le)
        editors[name] = le
    return form, editors


def build_buttons_column() -> tuple[QVBoxLayout, Buttons]:
    v = QVBoxLayout()
    v.addStretch()

    add     = QPushButton("追加")
    update  = QPushButton("更新（選択行）")
    delete  = QPushButton("削除（選択行）")

    for b in (add, update, delete):
        v.addWidget(b)

    v.addStretch()

    save    = QPushButton("保存（反映）")
    revert  = QPushButton("やり直し")
    clear   = QPushButton("クリア")

    for b in (save, revert, clear):
        v.addWidget(b)

    return v, Buttons(add=add, update=update, delete=delete, save=save, revert=revert, clear=clear)
