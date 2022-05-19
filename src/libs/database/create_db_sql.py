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
    DiscordID      STRING         PRIMARY KEY,
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
    ("REGISTERED", "Вы были успешно зарегистрированы на сервере."),
    ("REJECTED", "Заявка на вашу регистрацию была отклонена."),
    ("COLLECT_DATA", "Здесь надо написать инструкцию к заполнению данных."),
    ("QUEUED", "Ваша кандидатура находится на рассмотрении админстрации. Ожидайте дальнейших уведомлений.");
"""