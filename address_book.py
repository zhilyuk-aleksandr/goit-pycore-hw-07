import re
from collections import UserDict
from datetime import date, datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name is required.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{10}", value):
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        message = "Invalid date format. Use DD.MM.YYYY"
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", value):
            raise ValueError(message)
        try:
            parsed = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError(message) from None
        super().__init__(parsed)

    def __str__(self):
        return f"{self.value.day:02}.{self.value.month:02}.{self.value.year:04}"


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        return next((item for item in self.phones if item.value == phone), None)

    def remove_phone(self, phone):
        item = self.find_phone(phone)
        if item is None:
            raise ValueError("Phone not found.")
        self.phones.remove(item)

    def edit_phone(self, old_phone, new_phone):
        item = self.find_phone(old_phone)
        if item is None:
            raise ValueError("Phone not found.")
        self.phones[self.phones.index(item)] = Phone(new_phone)

    def __str__(self):
        phones = "; ".join(str(phone) for phone in self.phones)
        details = f"Contact name: {self.name}, phones: {phones}"
        if self.birthday:
            details += f", birthday: {self.birthday}"
        return details


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self, today=None):
        if today is None:
            today = date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday = record.birthday.value.date()
            anniversary = _anniversary(birthday, today.year)
            if anniversary < today:
                anniversary = _anniversary(birthday, today.year + 1)
            if (anniversary - today).days >= 7:
                continue
            if anniversary.weekday() >= 5:
                anniversary += timedelta(days=7 - anniversary.weekday())
            upcoming.append((anniversary, record.name.value))
        return [
            {"name": name, "congratulation_date": day.strftime("%d.%m.%Y")}
            for day, name in sorted(upcoming)
        ]


def _anniversary(birthday, year):
    try:
        return birthday.replace(year=year)
    except ValueError:
        # У невисокосний рік відзначаємо 29 лютого 28-го.
        return date(year, 2, 28)
