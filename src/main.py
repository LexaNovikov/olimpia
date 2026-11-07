import os
import pandas as pd
from src.formatting import formatting
from src.algoritm import algorithm
from src.hall import Hall


def main(path: str, selected_halls: list | None = None):
    """Основная функция рассадки"""
    if not os.path.exists(path):
        raise FileNotFoundError("Файла по указанному пути не существует")
    if not os.path.isfile(path):
        raise ValueError("Указанный путь ведёт к папке")
    halls = Hall.load_halls()
    if selected_halls is not None:
        halls = [hall for hall in halls if hall.name in selected_halls]
    if not halls:
        raise ValueError("Отметьте хотя бы один зал для рассадки")
    file = formatting(pd.read_excel(path).copy())
    file["№ компьютера"] = pd.NA
    test_pd = file.groupby(by="Название школы").size()
    test_pd_sorted = test_pd.sort_values(ascending=False)
    for school_name in test_pd_sorted.index:
        school_group = file[file["Название школы"] == school_name]
        new_group = algorithm(halls, school_group)
        file.loc[new_group.index, "№ компьютера"] = new_group["№ компьютера"]
    return file
