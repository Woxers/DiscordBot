from enum import Enum

class McSettings(Enum):
    '''
    '''
    quick_auth = {'name': 'Быстрая авторизация', 'description': 'Авторизация по уведомлению в ЛС', 'emoji': '🔐', 'image': 'https://media.discordapp.net/attachments/866681575639220255/1012773250528448593/unknown.png','variants': [
        {'key': 0, 'name': 'Отключено', 'description': 'Отключить быструю авторизацию'},
        {'key': 1, 'name': 'Включено', 'description': 'Включить быструю авторизацию'}]}
    
    join_notify = {'name': 'Оповещения о входе', 'description': 'Оповещает в ЛС о входе в ваш аккаунт', 'emoji': '📩', 'image': 'https://media.discordapp.net/attachments/866681575639220255/1012772959976444035/unknown1.png', 'variants': [
        {'key': 0, 'name': 'Отключено', 'description': 'Отключить опевещения о входе'},
        {'key': 1, 'name': 'Включено', 'description': 'Включить оповещения о входе'}]}
    
    tab_type = {'name': "Вид TAB'а в игре", 'description': 'Изменяет вид списка игроков на сервере', 'emoji': '📓', 'variants': [
        {'key': 'logo', 'name': 'Логотип', 'description': 'Логотип и Ping-Tps, загрузка РП', 'emoji': '🟢', 'image': 'https://media.discordapp.net/attachments/866681575639220255/1012770217568510074/unknown.png'},
        {'key': 'no_logo', 'name': 'Без логотипа', 'description': 'Только Ping-Tps', 'emoji': '🟡', 'image': 'https://media.discordapp.net/attachments/866681575639220255/1012769572161585152/unknown.png'}, 
        {'key': 'clear', 'name': 'Полу-Ванильный', 'description': 'Без логотипа и Ping-Tps', 'emoji': '🟣', 'image': 'https://media.discordapp.net/attachments/866681575639220255/1012769948403241153/unknown.png'}]}

    @classmethod
    def get(cls, name):
        for i in McSettings:
            if (i.name.lower() == name.lower()):
                return i
        return None