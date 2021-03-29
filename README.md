# Yandex Backend School
В данном файле описывается как именно необходимо запускать этот сервис. 
Инструкции выполнялись на виртуальной машине, которая была предоставлена.
К сервису также можно направлять запросы по ip адресу 178.154.211.238
Также можно почитать подробную информацию о реализации в файле ```Information_about_project.txt'.

## Запуск
Для того чтобы уметь запускать текущий сервис необходим python3, а также pip3 для того чтобы уметь установить необходимые библиотеки.
```sudo apt-get update
apt-get install python3
apt-get install python3-pip
```

Далее необходимо установить все необходимые для проекта библиотеки
```pip3 install -r requirements.txt```

Теперь нам необходимо установить nginx
```apt install nginx```
Вызываем команду
```cd flask_project
nano /etc/nginx/sites-enabled/flask_project```
И записываем внутрь данные из файла nginx_settings
Далее ```unlink /etc/nginx/sites-enabled/default```
И обновляем данные ```nginx -s reload```
После этого нам необходимо установить gunicorn
```apt-get install gunicorn```
И наконец запускаем 3 отдельных процесса
```gunicorn -w 3 flask_project:app```
И после этого мы можем посылать запросы к данному сервису

## Тестирование
Для того чтобы запустить тесты, необходимо запустить файл 'testing.py'
Данные тесты практически не зависят от времени, в которое их запускать, но есть некоторые ограниченные промежутки.
За этим нужно следить в функциях 'test_couriers_3() and test_orders_3()'. 