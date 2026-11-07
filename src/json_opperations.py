from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.hall import Hall

base_path = Path(__file__).resolve().parent.parent


def halls_file_path() -> Path:
    bundled_halls = base_path / "halls.json"
    if not getattr(sys, "frozen", False):
        return bundled_halls

    if sys.platform == "win32":
        data_root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        data_root = Path.home() / "Library" / "Application Support"
    else:
        data_root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")

    destination = data_root / "Olimpia" / "halls.json"
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundled_halls, destination)
    return destination


def read_hall():
    with open(halls_file_path(), "r") as f:
        halls = json.load(f)
        return halls


def write_hall(hall: Hall, halls: dict):
    with open(halls_file_path(), "w") as f:
        new_hall = {
            "name": hall.name,
            "workspace_quantity": hall.workspace_quantity,
            "workspaces_names": hall.workspaces_names,
        }
        halls["halls"].append(new_hall)
        new_halls = json.dumps(halls, indent=2, ensure_ascii=False)
        f.write(new_halls)


def add_hall(hall: Hall):
    write_hall(hall, read_hall())


def delete_hall(hall: Hall, halls: dict):
    with open(halls_file_path(), "w") as f:
        new_hall = {
            "name": hall.name,
            "workspace_quantity": hall.workspace_quantity,
        }
        for i in range(len(halls["halls"])):
            if halls["halls"][i]["name"] == new_hall["name"]:
                del halls["halls"][i]
                break
        new_halls = json.dumps(halls, indent=2, ensure_ascii=False)
        f.write(new_halls)


def delete_hall_result(hall: Hall):
    delete_hall(hall, read_hall())


def change_workspace_quantity(hall: Hall, halls: dict):
    for h in halls["halls"]:
        if h["name"] == hall.name:
            h["workspace_quantity"] = hall.workspace_quantity
    with open(halls_file_path(), "w") as f:
        f.write(json.dumps(halls, indent=2, ensure_ascii=False))


def change_workspace_quantity_result(hall: Hall):
    change_workspace_quantity(hall, read_hall())
