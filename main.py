from functools import wraps

from address_book import AddressBook, Record


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def input_error(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ValueError as error:
            return str(error)
    return wrapped


def require_args(args, count, usage):
    if len(args) != count:
        raise ValueError(f"Usage: {usage}")
    return args


def get_record(book, name):
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    return record


@input_error
def add_contact(args, book):
    name, phone = require_args(args, 2, "add NAME PHONE")
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book):
    name, old, new = require_args(args, 3, "change NAME OLD_PHONE NEW_PHONE")
    get_record(book, name).edit_phone(old, new)
    return "Contact updated."


@input_error
def show_phone(args, book):
    (name,) = require_args(args, 1, "phone NAME")
    phones = get_record(book, name).phones
    return "; ".join(str(phone) for phone in phones) or "No phones."


@input_error
def show_all(args, book):
    require_args(args, 0, "all")
    return "\n".join(str(record) for record in book.values()) or "No contacts."


@input_error
def add_birthday(args, book):
    name, birthday = require_args(args, 2, "add-birthday NAME DD.MM.YYYY")
    get_record(book, name).add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    (name,) = require_args(args, 1, "show-birthday NAME")
    birthday = get_record(book, name).birthday
    return str(birthday) if birthday else "Birthday is not set."


@input_error
def birthdays(args, book):
    require_args(args, 0, "birthdays")
    upcoming = book.get_upcoming_birthdays()
    return "\n".join(
        f"{item['name']}: {item['congratulation_date']}" for item in upcoming
    ) or "No upcoming birthdays."


def run_bot(book):
    handlers = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }
    print("Welcome to the assistant bot!")
    while True:
        try:
            command, args = parse_input(input("Enter a command: "))
        except (EOFError, KeyboardInterrupt):
            print("Good bye!")
            return
        if command in ("close", "exit") and not args:
            print("Good bye!")
            return
        if command == "hello" and not args:
            print("How can I help you?")
        elif command in handlers:
            print(handlers[command](args, book))
        elif command:
            print("Invalid command.")


def main():
    run_bot(AddressBook())


if __name__ == "__main__":
    main()
