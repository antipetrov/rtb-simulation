# Объявлятор

Сервис имитации показа объявлений по алгоритму RTB

## Тестовый сайт

Сервис: http://adtest.artrediska.com/

Админка: http://adtest.artrediska.com/admin/


## Локальный (отладочный) запуск

### Требуется

- Python 3.5
- PostgreSQL 11.2
- Docker, docker-compose

### Запуск

- Установка зависимостей: `pip install -r requirements.txt`
- Запуск БД из докера: `docker-compose up -d`
- Запуск тестового бекенда: `./manage.py startserver`


## Деплой (докером)

Все зависимости собираются в докер контейнере.

Для старта `docker-compose -f docker-compose.stage.yaml up -d`
