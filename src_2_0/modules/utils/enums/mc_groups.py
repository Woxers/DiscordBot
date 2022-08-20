from enum import Enum
from functools import cmp_to_key

class McGroups(Enum):
    '''
        `admin` Администратор 🟥

        `moderator` Модератор 🟦

        `player` Игрок 🟩

        `disabled` Игрок (Отключен) ⬜
    '''
    # Basic groups
    admin = {'name': 'Администратор', 'emoji': '🟥', 'weight': 100, 'primary': 1}
    stuff = {'name': 'Модератор', 'emoji': '🟦', 'weight': 50, 'primary': 1}
    default = {'name': 'Игрок', 'emoji': '🟩', 'weight': 10, 'primary': 1}
    disabled = {'name': 'Игрок (Отключен)', 'emoji': '⬜', 'weight': 5, 'primary': 1}

    # Authme groups
    notlogged = {'name': 'Не авторизирован (Онлайн)', 'emoji': '🟧', 'weight': 1000, 'primary': 1}
    notregistered = {'name': 'Не зарегистрирован (Онлайн)', 'emoji': '🟧', 'weight': 1000, 'primary': 1}

    # Badges group
        # Staff
    knife = {'name': 'Кинжал', 'emoji': '🗡️', 'weight': 9, 'primary': 0}
    axe = {'name': 'Топор', 'emoji': '🪓', 'weight': 8, 'primary': 0}
        # Credits
    star = {'name': 'Звезда', 'emoji': '⭐', 'weight': 7, 'primary': 0}
    fire = {'name': 'Огонь', 'emoji': '🔥', 'weight': 6, 'primary': 0}
        # Default
    fork = {'name': 'Трезубец', 'emoji': '🔱', 'weight': 5, 'primary': 0}
    pickaxe = {'name': 'Кирка', 'emoji': '⛏️', 'weight': 4, 'primary': 0}
    potion = {'name': 'Зелье', 'emoji': '⚗️', 'weight': 3, 'primary': 0}
    skull = {'name': 'Череп', 'emoji': '💀', 'weight': 2, 'primary': 0}

    @classmethod
    def static_init(cls):
        cls.comparator = cmp_to_key(cls.compare)

    @classmethod
    def get(cls, name):
        for i in McGroups:
            if (i.name == name):
                return i
        return None

    @classmethod
    def compare(cls, item1, item2):
        if (item1.value['primary'] >= item2.value['primary']):
            if (item1.value['weight'] > item2.value['weight']):
                return 1
        return -1

    @classmethod
    def get_comparator(cls):
        return cls.comparator

McGroups.static_init()

# groups = [McGroups.moderator, McGroups.star, McGroups.notregistered, McGroups.fire, McGroups.axe, McGroups.admin, McGroups.knife, McGroups.pickaxe, McGroups.notlogged, McGroups.fork, McGroups.player, McGroups.potion, McGroups.skull]
# cmp_key = cmp_to_key(McGroups.compare)
# groups.sort(key=McGroups.get_comparator(), reverse=1)
# for group in groups:
#     print(f"{group.value['primary']}\t {group.name} - {group.value['weight']}")
