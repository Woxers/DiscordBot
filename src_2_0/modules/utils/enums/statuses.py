from enum import Enum

class Statuses(Enum):
    '''
        `admin` Администратор 🔱

        `moder` Модератор ⚜️

        `access` Допущен 🎗️

        `verified` Проверен 💠

        `spectator` Наблюдающий 🗿

        `joined` Начинающий 🔰

        `rejected` Отклонен ⛔
    '''
    # Staff statuses
    admin = {'name': 'Администратор', 'weight': 100, 'emoji': '🔱', 'description': 'Доступны все возможные функции'}
    moder = {'name': 'Модератор', 'weight': 50, 'emoji': '⚜️', 'description': 'Расширенный доступ к серверу'}
    
    # User's statuses
    access = {'name': 'Допущен', 'weight': 20, 'emoji': '🎗️', 'description': 'Доступ к серверу Minecraft'}
    verified = {'name': 'Проверен', 'weight': 15, 'emoji': '💠', 'description': 'Доступ к Discord серверу'}
    spectator = {'name': 'Наблюдающий', 'weight': 10, 'emoji': '🗿', 'description': 'Ограниченный доступ к Discord серверу'}
    joined = {'name': 'Начинающий', 'weight': 1, 'emoji': '🔰', 'description': 'Доступ к функциям ограничен'}
    rejected = {'name': 'Отклонен', 'weight': 0, 'emoji': '⛔', 'description': 'Доступ к функциям ограничен'}

    @classmethod
    def get(cls, name):
        for i in Statuses:
            if (i.name.lower() == name.lower()):
                return i
        return None
