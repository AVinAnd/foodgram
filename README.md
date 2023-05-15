# Foodgram
Проект Foodgram представляет собой площадку, где каждый может опубликовать свои рецепты,
а так же найти интересные блюда для себя. Доступна подписка на интересных авторов, список избранных рецептов,
и функционал списка покупок, который соберет все необходимые ингредиенты для приготовления выбранных блюд, 
и объединит их в единый список необходимого к покупке.

## Стек технологий использованный в проекте:
 - Python
 - Django
 - Django REST Framework
 - REST API
 - Postgresql
 - Docker
 - Nginx

### Шаблон env файла
```
SECRET_KEY=your_secret_key # секретный ключ
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
### Как запустить проект в контейнерах
1. Клонировать репозиторий
```
https://github.com/AVinAnd/foodgram-project-react.git
```
2. Заполнить в директории infra файл .env

Секретный ключ можно сгенерировать командой:
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
3. В терминале перейти в директорию с docker-compose.yaml и выполнить команду
```
docker-compose up -d
```
4. Выполнить миграции и собрать статику
```
docker-compose exec infra_backend_1 python manage.py migrate
docker-compose exec infra_backend_1 python manage.py collectstatic --no-input
```
5. Создать суперпользователя
```
docker-compose exec infra_backend_1 python manage.py createsuperuser
```
6. Наполнить базу данных ингредиентами из data файла
```
docker-compose exec infra_backend_1 python manage.py loaddata ./data/ingredients.csv
```

### Об авторе
Андрей Виноградов - python-developer, выпускник Яндекс Практикума по курсу Python-разработчик
