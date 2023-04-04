# Direct-API
Для связи с автором пишите на Andrey@electis.ru 

## Описание

Сервис для взаимодействия с социальными сетями

На данный момент поддерживает:
- скачивание видео с YouTube
- постинг сообщений в Вконтакт и Одноклассники
- отправка формы в телеграм и на емейл

## Установка серверной части

Необходимые библиотеки
```shell
sudo apt install ffmpeg
sudo apt install redis
```
Python 3.6+ в виртуальном окружении

### Установка зависимостей
```shell
pip install -r requirements.txt
```

### Конфиги

Настройка проекта
```shell
cp .env.example .env
```
в .env файле прописываем


Добавляем конфиг supervisor:

```shell
sudo ln -s /www/direct_api/etc/supervisor.conf /etc/supervisor/conf.d/direct_api.conf
sudo supervisorctl reread && sudo supervisorctl update
```

Добавляем конфиг nginx:

Прописываем в файле etc/nginx.conf нужный server_name, затем
```shell
sudo ln -s /www/direct_api/etc/nginx.conf /etc/nginx/sites-enabled/direct_api.conf
sudo nginx -s reload
```

## Генерация документации
```shell
pip install sphinx recommonmark
ln -s /путь/к/проекту/Readme.md docs/source/Readme.md
cd docs
make html
```

## Проверка оформления кода
Если хотите предложить правки, то перед созданием коммита проверьте код командой
```shell
make lint
```

## TODO
- Скачивание видео с других соцсетей
- Доработка постинга в соцсети с поддержкой видео и тд
- Доработка авторизации в соцсетях для получения долгоживущего токена
