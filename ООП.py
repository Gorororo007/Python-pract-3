
import json
import os
import hashlib
from cryptography.fernet import Fernet
from abc import ABC, abstractmethod
from datetime import datetime

# Генерация ключа для шифрования
def generate_key():
    return Fernet.generate_key()

# Загрузка ключа из файла или создание нового
def load_key():
    if os.path.exists('secret.key'):
        with open('secret.key', 'rb') as key_file:
            return key_file.read()
    else:
        key = generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
        return key

# Шифруем данные
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

# Дешифруем данные
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()

# Хэшируем пароль
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

DATA_FILE = 'shop_data.json'  # Имя файла для хранения данных

class User:
    def __init__(self, username, password, role):
        self.__username = username
        self.__password = hash_password(password)  # Хэшируем пароль
        self.__role = role
        self.__history = []
        self.__created_at = datetime.now().strftime('%Y-%m-%d')

    def authenticate(self, password):
        return self.__password == hash_password(password)  # Сравниваем хэши паролей

    def get_username(self):
        return self.__username

    def get_role(self):
        return self.__role

    def add_to_history(self, product_name):
        self.__history.append(product_name)

    def get_history(self):
        return self.__history

    def update_password(self, new_password):
        self.__password = hash_password(new_password)  # Хэшируем новый пароль

    def to_dict(self):
        return {
            'username': self.__username,
            'password': self.__password,
            'role': self.__role,
            'history': self.__history,
            'created_at': self.__created_at
        }

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, 'admin')

    def add_product(self, product_list, name, price, rating):
        product = Product(name, price, rating)
        product_list.append(product)
        print(f"{name} добавлен!")
        shop.save_data()  # Сохранение данных после добавления продукта

    def remove_product(self, product_list, name):
        for product in product_list:
            if product.get_name() == name:
                product_list.remove(product)
                print(f"{name} удалён!")
                shop.save_data()  # Сохранение данных после удаления продукта
                return
        print(f"{name} не найден!")

class RegularUser(User):
    def __init__(self, username, password):
        super().__init__(username, password, 'user')

    def buy_product(self, product_list, product_name):
        for product in product_list:
            if product.get_name() == product_name:
                self.add_to_history(product_name)
                print(f"{product_name} куплен!")
                shop.save_data()  # Сохранение данных после покупки
                return
        print(f"{product_name} не найден!")

class Product:
    def __init__(self, name, price, rating):
        self.__name = name
        self.__price = price
        self.__rating = rating
        self.__added_at = datetime.now().strftime('%Y-%m-%d')

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_rating(self):
        return self.__rating

    def to_dict(self):
        return {
            'name': self.__name,
            'price': self.__price,
            'rating': self.__rating,
            'added_at': self.__added_at
        }

class Shop:
    def __init__(self):
        self.users = []
        self.products = []
        self.load_data()  # Загрузка данных при инициализации

    def add_user(self, user):
        self.users.append(user)

    def authenticate(self, username, password):
        for user in self.users:
            if user.get_username() == username and user.authenticate(password):
                return user
        return None

    def view_products(self):
        for product in self.products:
            print(f"Товар: {product.get_name()}, Цена: {product.get_price()}, Рейтинг: {product.get_rating()}")

    def filter_products_by_price(self, threshold):
        filtered = filter(lambda p: p.get_price() < threshold, self.products)
        for p in filtered:
            print(f"Товар: {p.get_name()}, Цена: {p.get_price()}, Рейтинг: {p.get_rating()}")

    def sort_products_by_price(self):
        sorted_products = sorted(self.products, key=lambda p: p.get_price())
        for p in sorted_products:
            print(f"Товар: {p.get_name()}, Цена: {p.get_price()}, Рейтинг: {p.get_rating()}")

    def save_data(self):
        data = {
            'users': [user.to_dict() for user in self.users],
            'products': [product.to_dict() for product in self.products]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в {DATA_FILE}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = [self.create_user(u) for u in data['users']]
                    self.products = [Product(p['name'], p['price'], p['rating']) for p in data['products']]
                print(f"Данные загружены из {DATA_FILE}")
            except json.JSONDecodeError:
                print("Ошибка при разборе файла JSON.")
            except KeyError as e:
                print(f"Ошибка: отсутствует ключ '{e}' в данных.")

    def create_user(self, user_data):
        if 'role' not in user_data or 'username' not in user_data or 'password' not in user_data:
            print("Недостаточно данных для создания пользователя.")
            return None
        if user_data['role'] == 'admin':
            return Admin(user_data['username'], user_data['password'])
        else:
            return RegularUser(user_data['username'], user_data['password'])

def main():
    global shop
    shop = Shop()
    
    # Создание пользователей
    if not any(user.get_username() == 'john_doe' for user in shop.users):
        user1 = RegularUser('john_doe', 'password')
        shop.add_user(user1)

    if not any(user.get_username() == 'admin_user' for user in shop.users):
        admin = Admin('admin_user', 'password')
        shop.add_user(admin)

    # Создание продуктов
    if not any(product.get_name() == 'Роза' for product in shop.products):
        shop.products.append(Product('Роза', 100, 5))

    if not any(product.get_name() == 'Тюльпан' for product in shop.products):
        shop.products.append(Product('Тюльпан', 50, 4))

    if not any(product.get_name() == 'Лилия' for product in shop.products):
        shop.products.append(Product('Лилия', 80, 5))

    username = input("Введите логин: ")
    password = input("Введите пароль: ")
    user = shop.authenticate(username, password)

    if user:
        print(f"Добро пожаловать, {user.get_username()}!")
        while True:
            if isinstance(user, RegularUser):
                action = input("Выберите действие: 1=Просмотр, 2=Покупка, 3=История, 4=Обновление пароля, 5=Выход: ")
                if action == '1':
                    shop.view_products()
                elif action == '2':
                    product_name = input("Введите название товара для покупки: ")
                    user.buy_product(shop.products, product_name)
                elif action == '3':
                    print("История покупок:", user.get_history())
                elif action == '4':
                    new_password = input("Введите новый пароль: ")
                    user.update_password(new_password)  # Хэшируем новый пароль
                    shop.save_data()  # Сохранение данных после изменения пароля
                    print("Пароль обновлён!")
                elif action == '5':
                    break
            elif isinstance(user, Admin):
                action = input("Выберите действие: 1=Добавить, 2=Удалить, 3=Сортировать, 4=Импорт данных, 5=Экспорт данных, 6=Выход: ")
                if action == '1':
                    name = input("Название товара: ")
                    price = float(input("Цена: "))
                    
                    # Обработка ввода рейтинга
                    while True:
                        try:
                            rating = float(input("Рейтинг (целое число): "))
                            if rating < 0 or rating > 5:
                                print("Рейтинг должен быть в диапазоне от 0 до 5.")
                            else:
                                break
                        except ValueError:
                            print("Пожалуйста, введите корректное число для рейтинга.")
                    
                    user.add_product(shop.products, name, price, rating)
                elif action == '2':
                    name = input("Введите название товара для удаления: ")
                    user.remove_product(shop.products, name)
                elif action == '3':
                    shop.sort_products_by_price()
                elif action == '4':
                    filename = input("Введите имя файла для импорта: ")
                    shop.import_data(filename)
                elif action == '5':
                    filename = input("Введите имя файла для экспорта: ")
                    shop.save_data()  # Сохранение данных перед экспортом
                elif action == '6':
                    break
    else:
        print("Неверные учетные данные")

if __name__ == "__main__":
    main()
