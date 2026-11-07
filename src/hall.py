from src.json_opperations import (
    add_hall,
    delete_hall_result,
    change_workspace_quantity_result,
    read_hall,
)


class Hall:
    name: str
    workspace_quantity: int
    workspaces = list
    workspaces_names: list
    _is_active: bool
    _all_halls: list = []

    def __init__(self, name, workspace_quantity, workspaces_names=None):
        self.name = name
        self.workspace_quantity = workspace_quantity
        self.workspaces = [False] * workspace_quantity
        self._is_active = False
        if workspaces_names is None:
            self.workspaces_names = [i for i in range(1, 1 + workspace_quantity)]
        else:
            self.workspaces_names = workspaces_names
        Hall._all_halls.append(self)

    def activate(self):
        self._is_active = True

    def deactivate(self):
        self._is_active = False

    def set_workspace(self, workspace_number, person):
        self.workspaces[workspace_number] = person

    def get_all_halls(self):
        return self._all_halls

    def delete_hall(self):
        if self.name == "Open space":
            raise ValueError("Встроенный зал Open space нельзя удалить")
        delete_hall_result(self)
        for idx, hall in enumerate(Hall._all_halls):
            if hall == self:
                del Hall._all_halls[idx]
        return

    @classmethod
    def load_halls(cls):
        halls = read_hall()
        cls._all_halls.clear()
        for hall in halls["halls"]:
            cls(hall["name"], hall["workspace_quantity"], hall["workspaces_names"])
        return cls._all_halls

    @classmethod
    def create_hall(
        cls, name: str, workspace_quantity, workspaces_names: list | None = None
    ):
        hall = cls(name, workspace_quantity, workspaces_names)
        add_hall(hall)
        return hall

    def add_workspace(self, number: int):
        if number <= 0:
            return "Число должно быть больше нуля"
        else:
            self.workspaces += [False] * number
            self.workspace_quantity += number
            change_workspace_quantity_result(self)
            return "Успешно"
