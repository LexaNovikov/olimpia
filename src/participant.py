class Participant:
    name: str
    surname: str
    school: str
    grade: int
    hall_name: str
    pc_number: int
    parent_name: str
    parent_surname: str
    phone_number: str
    _allParticipants: list = []

    def __init__(
        self,
        name,
        surname,
        school,
        grade,
        hall_name,
        pc_number,
        parent_name,
        phone_number,
    ):
        self.name = name
        self.surname = surname
        self.school = school
        self.grade = grade
        self.hall_name = hall_name
        self.pc_number = pc_number
        self.parent_name = parent_name
        self.phone_number = phone_number
        Participant._allParticipants.append(self)

    def age_group(self):
        if self.grade < 10:
            return False
        else:
            return True
