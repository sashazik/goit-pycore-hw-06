from collections import UserDict
from datetime import datetime, timedelta

# --- РОБОТА З КЛАСАМИ ---

class Field:
    """Базовий клас для всіх полів."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Клас для зберігання імені. Обов'язкове поле."""
    pass

class Phone(Field):
    """Клас для зберігання номера телефону. Має валідацію на 10 цифр."""
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Invalid phone format. Must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    """Клас для зберігання дати народження. Валідація у форматі DD.MM.YYYY."""
    def __init__(self, value):
        try:
            # Перетворюємо рядок на об'єкт datetime
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        # Повертаємо дату у вихідному форматі
        return self.value.strftime('%d.%m.%Y')


class Record:
    """
    Клас для зберігання інформації про контакт, 
    включаючи ім'я, список телефонів та дату народження.
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # Необов'язкове поле

    def add_phone(self, phone_number):
        """Додає телефон до контакту."""
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        """Видаляє телефон з контакту."""
        phone_obj = self.find_phone(phone_number)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone not found.")

    def edit_phone(self, old_number, new_number):
        """Замінює старий номер телефону на новий."""
        phone_obj = self.find_phone(old_number)
        if not phone_obj:
            raise ValueError("Old phone number not found.")
        
        # Валідація нового номера відбувається в __init__ класу Phone
        new_phone_obj = Phone(new_number)
        
        # Знаходимо індекс старого номера і замінюємо
        for i, phone in enumerate(self.phones):
            if phone.value == old_number:
                self.phones[i] = new_phone_obj
                return
            
    def find_phone(self, phone_number):
        """Пошук телефону у контакті."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        """Додає або оновлює дату народження."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        """Повертає рядкове представлення запису."""
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    """Клас для зберігання та управління записами."""
    def add_record(self, record: Record):
        """Додає запис до адресної книги."""
        self.data[record.name.value] = record

    def find(self, name):
        """Знаходить запис за ім'ям."""
        return self.data.get(name)

    def delete(self, name):
        """Видаляє запис за ім'ям."""
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        """
        Повертає список користувачів, яких потрібно привітати 
        протягом наступних 7 днів, згрупованих по днях.
        """
        users_to_greet = {}
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue
            
            bday = record.birthday.value
            # Розраховуємо дату дня народження цього року
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                # Якщо ДН вже пройшов, дивимось наступний рік
                bday_this_year = bday.replace(year=today.year + 1)

            # Перевіряємо, чи ДН потрапляє у 7-денний інтервал
            delta_days = (bday_this_year - today).days

            if 0 <= delta_days < 7:
                day_of_week = bday_this_year.weekday() # Понеділок=0, Неділя=6
                
                # Визначаємо день привітання
                congr_day_str = bday_this_year.strftime('%A')
                
                # Якщо Субота (5) або Неділя (6), переносимо на Понеділок
                if day_of_week == 5 or day_of_week == 6:
                    congr_day_str = "Monday"
                    
                if congr_day_str not in users_to_greet:
                    users_to_greet[congr_day_str] = []
                users_to_greet[congr_day_str].append(record.name.value)
        
        return users_to_greet

# --- ДЕКОРАТОР ТА ОБРОБНИКИ КОМАНД ---

def input_error(func):
    """
    Декоратор для обробки помилок вводу користувача.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)  # Для помилок валідації Phone, Birthday
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format. Please provide necessary arguments."
        except AttributeError:
            return "Contact has no birthday saved."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return inner

def parse_input(user_input):
    """Розбиває ввід користувача на команду та аргументи."""
    cmd, *args = user_input.split()
    return cmd.lower(), *args

@input_error
def add_contact(args, book: AddressBook):
    """Додає контакт або новий телефон до існуючого контакту."""
    if len(args) < 2:
        raise IndexError("Invalid format. Usage: add [name] [phone]")
        
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    
    # Валідація номера відбувається при створенні Phone
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    """Змінює номер телефону для існуючого контакту."""
    if len(args) < 3:
        raise IndexError("Invalid format. Usage: change [name] [old_phone] [new_phone]")
        
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError # "Contact not found."
    
    # Помилки (не знайдено старий, невалідний новий) обробляться всередині
    record.edit_phone(old_phone, new_phone)
    return "Contact phone updated."

@input_error
def show_phone(args, book: AddressBook):
    """Показує телефони вказаного контакту."""
    if len(args) < 1:
        raise IndexError("Invalid format. Usage: phone [name]")
        
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError # "Contact not found."
    
    if not record.phones:
        return "Contact has no phones saved."
        
    return f"{name}'s phones: {'; '.join(p.value for p in record.phones)}"

def show_all(book: AddressBook):
    """Показує всі контакти в адресній книзі."""
    if not book.data:
        return "Address book is empty."
    
    # Використовуємо __str__ з Record для гарного форматування
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    """Додає день народження до контакту."""
    if len(args) < 2:
        raise IndexError("Invalid format. Usage: add-birthday [name] [DD.MM.YYYY]")
            
    name, bday_str = args
    record = book.find(name)
    if record is None:
        raise KeyError # "Contact not found."
    
    # Валідація формату дати відбувається в record.add_birthday
    record.add_birthday(bday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    """Показує день народження контакту."""
    if len(args) < 1:
        raise IndexError("Invalid format. Usage: show-birthday [name]")
        
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError # "Contact not found."
            
    if not record.birthday:
        raise AttributeError # "Contact has no birthday saved."
            
    # Використовуємо __str__ з Birthday для форматування
    return f"{name}'s birthday: {record.birthday}"

@input_error
def birthdays(args, book: AddressBook):
    """Показує дні народження, які відбудуться протягом наступного тижня."""
    upcoming = book.get_upcoming_birthdays()
    
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    result_lines = ["Upcoming birthdays:"]
    
    # Виводимо дні у логічному порядку (Пн-Пт)
    # Дні, перенесені з вихідних, вже будуть у "Monday"
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    output_found = False
    for day in days_order:
        if day in upcoming and upcoming[day]:
            result_lines.append(f"{day}: {', '.join(upcoming[day])}")
            output_found = True
            
    if not output_found:
        return "No upcoming birthdays during the work week. (Check weekends)"
        
    return "\n".join(result_lines)


# --- ГОЛОВНА ФУНКЦІЯ ---

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()