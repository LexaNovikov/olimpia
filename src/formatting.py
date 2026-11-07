import re

from pandas import DataFrame


def formatting(df_raw: DataFrame):
    df = df_raw.copy()
    firstnums = {
        "двадцат": 2,
        "тридцат": 3,
        "сорок": 4,
        "пятдесят": 5,
        "пятидесят": 5,
        "шестьдесят": 6,
        "шестидесят": 6,
    }
    nums = {
        "сингулярити": "сингулярити",
        "один": 1,
        "два": 2,
        "три": 3,
        "перв": 1,
        "втор": 2,
        "трет": 3,
        "чет": 4,
        "пят": 5,
        "шест": 6,
        "седьм": 7,
        "сем": 7,
        "восьм": 8,
        "девят": 9,
        "десят": 10,
        "одиннадцат": 11,
    }

    for _, row in df.iterrows():
        if type(row["Название школы"]) != str:
            continue
        raw_school = row["Название школы"].lower().strip().replace(" ", "")
        result_school = []
        if "лицей" in raw_school:
            result_school.append("Лицей")
        elif "гимназия" in raw_school:
            result_school.append("Гимназия")
        else:
            if row["Тип уч. заведения"] != "Колледж":
                result_school.append("СОШ")
        firststatus = False
        numstaus = False
        digits = list(re.finditer(r"\d+", str(raw_school)))
        numidx = -1
        index = -1
        if digits:
            result_school.append(digits[0].group())
            numidx = int(digits[0].span()[0])
        for firstnum in firstnums.keys():
            index = raw_school.find(firstnum)
            if index != -1:
                if numidx != -1:
                    if numidx < index:
                        result_school.append(
                            result_school.pop() + str(firstnums[firstnum])
                        )
                    else:
                        result_school.append(
                            str(firstnums[firstnum]) + result_school.pop()
                        )
                else:
                    result_school.append(str(firstnums[firstnum]))
                firststatus = True
                break
        if index == -1:
            index = 0
        for num in nums.keys():
            if raw_school.find(num, index) != -1:
                if len(result_school) > 1 and numidx == -1:
                    result_school[-1] += str(nums[num])
                elif numidx == -1:
                    result_school.append(str(nums[num]))
                numstaus = True
                break
        if firststatus and numstaus is False:
            result_school[-1] += "0"
        if len(result_school) <= 1:
            result_school_name = row["Название школы"]
        else:
            result_school_name = " ".join(result_school)
        df.at[_, "Название школы"] = result_school_name
    return df
