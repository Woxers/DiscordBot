create_status_table = """
create table if not exists status
(
    Name        varchar(20)  not null,
    Description varchar(256) null,
    constraint status_Name_uindex
        unique (Name)
);
"""

create_users_table = """
create table if not exists users
(
    DiscordID      int                          not null
        primary key,
    Status         varchar(20) default 'JOINED' not null,
    JoinedDatetime datetime                     not null,
    Name           varchar(32)                  null,
    Nickname       varchar(32)                  null,
    RegDatetime    datetime                     null,
    constraint users_DiscordID_uindex
        unique (DiscordID),
    constraint users_Nickname_uindex
        unique (Nickname),
    constraint Status
        foreign key (Status) references status (Name)
);"""

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