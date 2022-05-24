create_status_table = """
CREATE TABLE IF NOT EXISTS status (
    Name        STRING NOT NULL
                       UNIQUE
                       PRIMARY KEY,
    Description STRING NOT NULL
                       DEFAULT ('Описания нет') 
);
"""

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    DiscordID      INT            PRIMARY KEY,
    Status                        REFERENCES status (Name) 
                                  NOT NULL
                                  DEFAULT ('JOINED'),
    JoinedDatetime DATETIME       NOT NULL,
    Name           STRING (1, 32),
    Nickname       STRING (3, 32) UNIQUE,
    RegDatetime    DATETIME
);

"""

insert_status = """
INSERT INTO
    status (Name, Description)
VALUES
    ("JOINED", "Вы только присоединились к серверу, попросите пригласившего вас человека отправить заявку на регистрацию."),
    ("CONFIRMED", "Вы подтвержденный пользователь. Когда откроется minecraft сервер, вы получите к нему доступ одним из первых."),
    ("ACCESS", "Вы подтвержденный пользователь. Получен доступ к Discord и Minecraft серверу."),
    ("SPECTATOR", "Вы получили доступ только к Discord серверу."),
    ("REJECTED", "Ваша заявка была отклонена."),
    ("INTERVIE", "Вы находитесь на этапе верификации. Пожалуйста, заполните данные о себе."),
    ("QUEUED", "Ваша кандидатура находится на рассмотрении админстрации. Ожидайте дальнейших уведомлений.");
"""