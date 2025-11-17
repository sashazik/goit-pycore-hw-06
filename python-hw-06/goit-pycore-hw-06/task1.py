from collections import UserDict

# --- Базові Класи ---

class Field:
    """
    Базовий клас для всіх полів (наприклад, ім'я, телефон).
    Зберігає значення та надає стандартний строковий вигляд.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """
    Клас для зберігання імені контакту.
    Успадковується від Field. Наразі не додає нової логіки,
    але є обов'язковим полем для Record.
    """
    pass

class Phone(Field):
    """
    Клас для зберігання номера телефону.
    Має вбудовану валідацію на 10 цифр при створенні.
    """
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Неправильний формат телефону. Номер повинен складатися рівно з 10 цифр.")
        super().__init__(value)

    @staticmethod
    def validate(phone_number):
        """Статичний метод для валідації номера."""
        return isinstance(phone_number, str) and phone_number.isdigit() and len(phone_number) == 10

# --- Клас Запису ---

class Record:
    """
    Клас для зберігання інформації про один контакт.
    Містить одне ім'я (Name) та список телефонів (list of Phone).
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone_number):
        """
        Додає новий телефон до контакту.
        Валідація відбувається при створенні об'єкта Phone.
        """
        phone = Phone(phone_number)
        self.phones.append(phone)
        print(f"Додано телефон: {phone_number} для контакту {self.name.value}")

    def remove_phone(self, phone_number):
        """Видаляє телефон зі списку за його значенням."""
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            print(f"Видалено телефон: {phone_number} у контакту {self.name.value}")
        else:
            print(f"Телефон {phone_number} не знайдено у контакту {self.name.value}")

    def edit_phone(self, old_phone_number, new_phone_number):
        """
        Редагує існуючий номер телефону.
        Знаходить старий номер і замінює його новим.
        Новий номер проходить валідацію.
        """
        # Валідація нового номера відбудеться при створенні об'єкта Phone
        try:
            new_phone = Phone(new_phone_number)
            phone_to_edit = self.find_phone(old_phone_number)
            
            if phone_to_edit:
                # Знаходимо індекс і замінюємо об'єкт
                index = self.phones.index(phone_to_edit)
                self.phones[index] = new_phone
                print(f"Телефон {old_phone_number} змінено на {new_phone_number} у контакту {self.name.value}")
            else:
                print(f"Телефон {old_phone_number} не знайдено у контакту {self.name.value}")
        except ValueError as e:
            print(f"Помилка редагування: {e}")


    def find_phone(self, phone_number):
        """Шукає об'єкт Phone за його значенням (номером)."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        """Повертає строкове представлення запису."""
        phone_list = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phone_list if phone_list else 'No phones'}"

# --- Клас Адресної Книги ---

class AddressBook(UserDict):
    """
    Клас для керування адресною книгою.
    Успадковується від UserDict для зберігання записів (Record)
    у вигляді словника {ім'я: Запис}.
    """
    
    def add_record(self, record: Record):
        """Додає новий запис до адресної книги."""
        self.data[record.name.value] = record
        print(f"Додано контакт: {record.name.value}")

    def find(self, name):
        """Шукає запис за ім'ям."""
        return self.data.get(name)

    def delete(self, name):
        """Видаляє запис за ім'ям."""
        if name in self.data:
            del self.data[name]
            print(f"Контакт {name} видалено.")
        else:
            print(f"Контакт {name} не знайдено.")

# --- Приклад Використання ---

if __name__ == "__main__":
    
    # 1. Створення адресної книги
    book = AddressBook()

    # 2. Створення запису для "John"
    john_record = Record("John")
    
    # 3. Додавання телефону (валідація спрацює)
    john_record.add_phone("1234567890")
    
    # 4. Спроба додати невалідний телефон (спричинить помилку)
    try:
        john_record.add_phone("12345")
    except ValueError as e:
        print(f"Помилка: {e}")
    
    # 5. Додавання другого телефону
    john_record.add_phone("5555555555")

    # 6. Додавання запису "John" до адресної книги
    book.add_record(john_record)

    # 7. Створення та додавання нового запису "Jane"
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    print("--- Вміст адресної книги ---")
    for name, record in book.data.items():
        print(record)
    print("----------------------------")

    # 8. Пошук контакту "John"
    john = book.find("John")
    if john:
        print(f"Знайдено John: {john}")

        # 9. Редагування телефону
        john.edit_phone("1234567890", "1111111111")
        
        # 10. Спроба редагувати неіснуючий телефон
        john.edit_phone("9999999999", "2222222222")

        # 11. Спроба редагувати на невалідний номер
        john.edit_phone("1111111111", "abc")

        print(f"Оновлений John: {john}")

        # 12. Пошук конкретного телефону
        found_phone = john.find_phone("5555555555")
        if found_phone:
            print(f"Знайдено телефон у John: {found_phone.value}")

        # 13. Видалення телефону
        john.remove_phone("1111111111")
        print(f"John після видалення телефону: {john}")

    # 14. Видалення контакту "Jane"
    book.delete("Jane")

    # 15. Спроба знайти "Jane"
    jane = book.find("Jane")
    if not jane:
        print("Контакт Jane успішно видалено.")

    print("--- Фінальний вміст адресної книги ---")
    for name, record in book.data.items():
        print(record)
    print("-----------------------------------")