### Установка

```sh
sudo apt install ffmpeg
```

### Конфиги

Добавляем конфиг supervisor:

```sh
sudo ln -s /www/direct_api/etc/supervisor.conf /etc/supervisor/conf.d/direct_api.conf
sudo supervisorctl reread && sudo supervisorctl update
```

Добавляем конфиг nginx:

Прописываем в файле etc/nginx.conf нужный server_name, затем
```sh
sudo ln -s /www/direct_api/etc/nginx.conf /etc/nginx/sites-enabled/direct_api.conf
sudo nginx -s reload
```

### Запуск линтеров
```sh
make lint
```
