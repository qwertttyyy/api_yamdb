# **API для проекта "YaMDb"**

## **Описание проекта**

Данный проект выполнен совместно с двумя однокурсниками:
<https://github.com/qwertttyyy> и <https://github.com/st1teec>

Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

## **Технологии**

| Библиотека                  | Версия |
|-----------------------------|--------|
|Django                       | 3.2    |
|djangorestframework          | 3.12.4 |
|djangorestframework-simplejwt| 5.2.2  |
|django-filter                | 23.1   |
|drf-spectacular              | 0.26.1 |
|Pytest                       | 6.2.4  |
|pytest-django                | 4.4.0  |
|PyJWT                        | 2.1.0  |
|requests                     | 2.26.0 |


## Запуск

1. Установите python версии 3.9 и выше.
1. Клонируйте репозиторий и перейдите в него в командной строке:

    ```bash
    git clone https://github.com/LizaKoch/api_yamdb.git && \
    cd api_yamdb
    ```

1. Создайте вертуальное окружение и установите зависимости (пример команд на linux/mac):

    ```bash
    python3 -m venv venv && \ 
        source venv/bin/activate && \
        python3 -m pip install --upgrade pip && \
        pip install -r requirements.txt
    ```

1. Выполните миграции:

    ```bash
    python3 api_yamdb/manage.py migrate
    ```

1. Загрузка данных в базу:

    ```bash
    cd api_yamdb &&
    python manage.py writecsv reviews.Genre genre &&
    python manage.py writecsv reviews.Category category &&
    python manage.py writecsv reviews.Title titles &&
    python manage.py writecsv reviews.TitleGenre genre_title &&
    python manage.py writecsv reviews.User users &&
    python manage.py writecsv reviews.Review review &&
    python manage.py writecsv reviews.Comment comments
    ```

1. Создайте superuser:

    ```bash
    python3 api_yamdb/manage.py createsuperuser
    ```

1. Запустите проект:

    ```bash
    python3 api_yamdb/manage.py runserver
    ```

## **Примеры запросов API**

Полная документация доступна по ссылке <http://127.0.0.1:8000/doc/> после запуска проекта.
