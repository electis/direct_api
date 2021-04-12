### Установка

```
sudo apt install ffmpeg
```

### Конфиги

Добавляем конфиг supervisor:

```
sudo ln -s /www/direct_api/etc/supervisor.conf /etc/supervisor/conf.d/direct_api.conf
sudo supervisorctl reread && sudo supervisorctl update
```

Добавляем конфиг nginx:

Прописываем в файле etc/nginx.conf нужный server_name, затем
```
sudo ln -s /www/direct_api/etc/nginx.conf /etc/nginx/sites-enabled/direct_api.conf
sudo nginx -s reload
```
