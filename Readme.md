## Запуск:
1) Запустить базу данных
```
docker-compose up --build -d
```
2) Установить и запустить сервер
```
poetry install
alembic upgrade head
poetry run python -m app
```
3) Тесты
```
poetry run python tests/test_api.py
```

## Эндпойнты:
```
POST /v1/user - создание пользователя
GET /v1/user/{user_id} - получение инфы по пользователю
POST /v1/user/{user_id}/transaction - создание транзакции
GET /v1/user/{user_id}/transaction/{transaction_id} - получение инфы по транзакции
```

## Дополнительно
### Транзакция будет обработана один раз за счет того, что сохраняется по уникальному uid, который также играет роль ключа идемпотентности. Хотя есть маааленькая вероятность что uid повторится.
### Уведомить другие сервисы можно через очередь сообщений, напирмер RabbitMQ или Кафка
### grafana для мониторинга нагрузки, какой нибудь инструмет для логгирования (например graylog)
