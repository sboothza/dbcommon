from faker import Faker
from enum import Enum
from random import Random
import datetime

from base.session import Session

fake = Faker()
random = Random()


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class Person:
    ...


class Person:
    def __init__(self, id: int = 0, name: str = "", gender: Gender = Gender.MALE, address: str = "",
                 credit_card: str = "", phone: str = "", email: str = "",
                 dob: datetime.datetime = datetime.datetime.min):
        self.father_id: int = None
        self.mother_id: int = None
        if name == "":
            self.gender = Gender.MALE if random.randint(0, 1) == 0 else Gender.FEMALE
            self.name = fake.name_male() if self.gender == Gender.MALE else fake.name_female()

            self.address = fake.address()
            self.credit_card = fake.credit_card_number()
            self.phone = fake.phone_number()
            self.email = fake.ascii_email()
            self.dob = fake.date_of_birth(None, 5, 90)
        else:
            self.name = name
            self.gender = gender
            self.address = address
            self.credit_card = credit_card
            self.phone = phone
            self.email = email
            self.dob = dob

    def __str__(self):
        return f"{self.name} {self.gender} {self.address}"

    def get_params_dict(self):
        return {
            "name": self.name,
            "father_id": self.father_id,
            "mother_id": self.mother_id,
            "gender": "M" if self.gender == Gender.MALE else "F",
            "address": self.address,
            "creditcard": self.credit_card,
            "phone": self.phone,
            "email": self.email,
            "dob": self.dob
        }

    def insert(self, sql, session: Session):
        params = self.get_params_dict()
        self.id = session.execute_lastrowid(sql, params)

    def make_parent(self, gender: Gender):
        self.father_id = None
        self.mother_id = None
        self.gender = gender
        self.name = fake.name_male() if self.gender == Gender.MALE else fake.name_female()
        self.address = fake.address()
        self.credit_card = fake.credit_card_number()
        self.phone = fake.phone_number()
        self.email = fake.ascii_email()
        self.dob = fake.date_of_birth(None, 20, 90)

    def make_child(self, father: Person, mother: Person):
        self.father_id = father.id
        self.mother_id = mother.id
        self.gender = Gender.MALE if random.randint(0, 1) == 0 else Gender.FEMALE
        self.name = fake.name_male() if self.gender == Gender.MALE else fake.name_female()
        self.address = father.address
        self.credit_card = ""
        self.phone = father.phone
        self.email = fake.ascii_email()
        parent_age = datetime.date.today().year - father.dob.year
        self.dob = fake.date_of_birth(None, 0, parent_age - 20)
