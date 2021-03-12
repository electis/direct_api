### Конфиги

Добавляем конфиг supervisor:

```
sudo ln -s /www/church_api/etc/supervisor.conf /etc/supervisor/conf.d/church22.conf
sudo supervisorctl reread
sudo supervisorctl update
```

Добавляем конфиг nginx:

Прописываем в файле etc/nginx.conf нужный server_name, затем
```
sudo ln -s /www/church_api/etc/nginx.conf /etc/nginx/sites-enabled/church22.conf
sudo nginx -s reload
```
