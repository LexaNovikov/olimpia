from pandas.core.frame import DataFrame

from src.hall import Hall
from src.participant import Participant


def check(hall_workspaces: list, cur_i: int, school: str, grade: int):
    if hall_workspaces[cur_i] is not False:
        return False
    left = max(0, cur_i - 1)
    right = min(len(hall_workspaces), cur_i + 2)
    if grade < 10:
        age_group = False
    else:
        age_group = True
    for i in range(left, right):
        if (
            hall_workspaces[i] is not False
            and hall_workspaces[i].school == school
            and age_group == hall_workspaces[i].age_group()
        ):
            return False
    return True


def get_workplace(halls: list[Hall], school: str, grade: int):
    for hall in halls:
        for workspace_num in range(hall.workspace_quantity):
            if check(hall.workspaces, workspace_num, school, grade):
                return hall, workspace_num
    return None


def algorithm(halls: list[Hall], group: DataFrame.Group):
    for index, participant in group.iterrows():
        name = participant["Имя"]
        surname = participant["Фамилия"]
        school = participant["Название школы"]
        grade = participant["Класс обучения"]
        parent_name = participant["ФИО родителя"]
        phone_number = participant["Номер телефона родителя"]
        workplace = get_workplace(halls, school, grade)
        if str(surname) == "":
            continue
        if workplace is not None:
            hall_name = workplace[0].name
            workplace_name = workplace[0].workspaces_names[workplace[1]]
        else:
            hall_name = " "
            workplace_name = ""
        new_participant = Participant(
            name,
            surname,
            school,
            grade,
            hall_name,
            workplace_name,
            parent_name,
            phone_number,
        )
        if workplace is not None:
            workplace[0].set_workspace(workplace[1], new_participant)
        group.at[index, "№ компьютера"] = hall_name[0] + "-" + str(workplace_name)

    return group
