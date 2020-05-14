import requests
import sys


class Librus:
    host = "https://api.librus.pl/"

    def __init__(self):
        self.headers = {
            "Authorization": "Basic Mjg6ODRmZGQzYTg3YjAzZDNlYTZmZmU3NzdiNThiMzMyYjE="
        }
        self.logged_in = False

    # Checks data and decides method of login
    def login(self, login, password):
        if not self.logged_in:
            if login is None or password is None or login == "" or password == "":
                return False
            else:
                """Make connection to the host and get auth token"""
                r = None
                loop = 0
                while r is None:
                    try:
                        r = requests.post(self.host + "OAuth/Token", data={"username": login,
                                                                           "password": password,
                                                                           "librus_long_term_token": "1",
                                                                           "grant_type": "password"},
                                          headers=self.headers)

                        if r.ok:
                            self.logged_in = True
                            self.headers["Authorization"] = "Bearer " + r.json()["access_token"]

                            return True
                        else:
                            return False
                    except requests.exceptions.Timeout:
                        if loop >= 10:
                            return False
                        else:
                            loop += 1
                            continue
                    except requests.exceptions.RequestException:
                        raise requests.exceptions.ConnectionError

    # Make connection and get access token

    def get_data(self, url):
        if self.logged_in:
            try:
                return requests.get(self.host + "2.0/" + url, headers=self.headers)
            except (requests.exceptions.ConnectionError, TimeoutError, requests.exceptions.Timeout,
                    requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
                raise Exception("Connection error")
        else:
            raise Exception("User not logged in")

    def get_lucky_number(self):
        r = self.get_data("LuckyNumbers")
        lucky_number = r.json()["LuckyNumber"]["LuckyNumber"]

        return lucky_number

    def get_grades(self, v2=False):
        r = self.get_data("Grades")

        if v2:
            return r.json()

        subjects = self.get_subjects()
        categories = self.get_categories()
        teachers = self.get_teachers()

        grades = {i: [] for i in subjects.values()}
        grades_comments = self.get_comments()

        for i in r.json()["Grades"]:
            if "Comments" in i:
                comment = grades_comments[i["Comments"][0]["Id"]]["Text"]
            else:
                comment = "Brak komentarza"

            grades[subjects[i["Subject"]["Id"]]].append({
                "Grade": i["Grade"],
                "Weight": categories[i["Category"]["Id"]]["Weight"],
                "Category": categories[i["Category"]["Id"]]["Name"],
                "Teacher": teachers[i["AddedBy"]["Id"]],
                "Comment": comment,
                "To_the_average": categories[i["Category"]["Id"]]["CountToTheAverage"]
            })

        return grades

    def get_subjects(self, v2=False):
        r = self.get_data("Subjects")

        if v2:
            return r.json()

        return {i["Id"]: i["Name"] for i in r.json()["Subjects"]}

    def get_categories(self, v2=False):
        categories = {}

        r = self.get_data("Grades/Categories")

        if v2:
            return r.json()

        for i in r.json()["Categories"]:
            if "Weight" in i:
                w = i["Weight"]
            else:
                w = None

            if i["CountToTheAverage"]:
                i["CountToTheAverage"] = "Tak"
            else:
                i["CountToTheAverage"] = "Nie"

            categories[i["Id"]] = {
                "Name": i["Name"],
                "Weight": w,
                "CountToTheAverage": i["CountToTheAverage"],
            }

        return categories

    def get_teachers(self, *, v2=False, mode="normal"):
        r = self.get_data("Users")

        if v2:
            return r.json()

        teachers = {
            i["Id"]: {
                "FirstName": i["FirstName"],
                "LastName": i["LastName"]
            } for i in r.json()["Users"]
        }

        if mode == "fullname":
            return ["%s %s" % (data["FirstName"], data["LastName"]) for t_id, data in teachers.items()]
        elif mode == "fullname-id":
            return ["%s: %s %s" % (t_id, data["FirstName"], data["LastName"]) for t_id, data in teachers.items()]

        return teachers

    def get_comments(self, v2=False):
        r = self.get_data("Grades/Comments")

        if v2:
            return r.json()

        comments = {
            i["Id"]: {
                "Text": i["Text"]
            } for i in r.json()["Comments"]
        }

        return comments

    def get_school_free_days(self, v2=False):
        r = self.get_data("SchoolFreeDays")

        if v2:
            return r.json()

        school_free_days = r.json()["SchoolFreeDays"]

        for i in school_free_days:
            for e in ["Id", "Units"]:
                i.pop(e)

        return school_free_days

    def get_teacher_free_days(self, v2=False):
        r = self.get_data("TeacherFreeDays")

        if v2:
            return r.json()

        teacher_free_days = r.json()["TeacherFreeDays"]

        teachers = self.get_teachers()

        r = self.get_data("TeacherFreeDays/Types")
        teacher_free_days_types = {
            i["Id"]: i["Name"] for i in r.json()["Types"]
        }

        for i in teacher_free_days:
            i.pop("Id")
            i["Teacher"] = teachers[i["Teacher"]["Id"]]
            i["Type"] = teacher_free_days_types[i["Type"]["Id"]]

        return teacher_free_days

    def get_lessons(self, v2=False):
        r = self.get_data("Lessons")

        if v2:
            return r.json()

        subjects = self.get_subjects()
        teachers = self.get_teachers()

        lessons = {
            i["Id"]: {
                "Subject": subjects[i["Subject"]["Id"]],
                "Teacher": teachers[i["Teacher"]["Id"]]

            } for i in r.json()["Lessons"]
        }

        return lessons

    def get_attendances(self, v2=False):
        r = self.get_data("Attendances/Types")

        if v2:
            return r.json()

        attendances_types = {
            i["Id"]: {
                "Name": i["Name"],
                "Short": i["Short"],
                "Standard": i["Standard"],
                "IsPresenceKind": i["IsPresenceKind"],
                "Order": i["Order"]
            } for i in r.json()["Types"]
        }

        lessons = self.get_lessons()
        teachers = self.get_teachers()
        attendances = self.get_data("Attendances").json()["Attendances"]

        for i in attendances:
            i.pop("Student")
            i["Type"] = attendances_types[i["Type"]["Id"]]
            i["AddedBy"] = teachers[i["AddedBy"]["Id"]]
            i["Lesson"] = lessons[i["Lesson"]["Id"]]

        return attendances
