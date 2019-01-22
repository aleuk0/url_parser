сервис, который обходит произвольный сайт
(например https://ria.ru/, http://www.vesti.ru/, http://echo.msk.ru/, http://tass.ru/ural, http
s://lenta.ru/) с глубиной 2 и сохраняет html, url и title страницы в произвольное хранилище

для запуска надо установить необходимые библиотеки из requirements в свое виртуальное окружение
и запустить скрипт scripts/main.py

принимает команды:
python scripts/main.py load http://www.python.org --depth 2
python scripts/main.py get http://www.python.org -n 2