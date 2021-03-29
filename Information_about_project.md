# Задание
Чтобы немного скрасить жизнь людей на самоизоляции, вы решаете открыть
интернет-магазин по доставке конфет "Сласти от всех напастей".
Ваша задача — разработать на python REST API сервис, который позволит нанимать курьеров на работу,
принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.


Также здесь хранятся файлы с полной информацией как именно должен работать сервис, как он должен обрабатывать запросы.


Я использовала Flask framework, а также базу данных Sqlalchemy, т.к. эту базу довольно легко подключить к приложению.
Я создала две таблицы чтобы с ними работать. OrderModel и CourierModel.

В CourierModel  хранится базовая информация о курьере: ID, type, regions and working hours.
Regions и working hours являются листами, и я храню их с помощью преобразования к строке.
Также в CourierModel у меня есть два листа, в которых для каждого региона хранится суммарное время доставки всех заказов, 
а также количество доставленных заказов. 
Это необходимо для того чтобы быстро считать среднее время по району. 
Т.к. минимальное среднее время среди всех районов используется для того чтобы посчитать рейтинг.

Также я храню зарплату для курьера.
Здесь нужно уточнить что в моей реализации курьер получает зарплату только после того как завершил все заказы из текущего развоза.
Для этого во время начала развоза я добавляю ему зарплату за текущий развоз, чтобы запомнить что я её дала.
При этом если у курьера спрашивают какая у него сейчас текущая зарплата, я проверяю есть ли у него незавершенные заказы. 
И если они у него есть, значит выданную зарплату нужно убрать из ответа.
Чтобы корректно убирать выданную зарплату нужно помнить тип курьера который был у него изначально, 
на случай если курьер сменил свой тип в процессе текущего развоза. 
Т.к. зарплата считается именно для того типа, который был в самом начале развоза.

Для заказа я также храню базовую информацию: id, weight, region and working hours. 
Также working hours является листом, и я конвертирую данные в строку.
Плюс я сохраняю assign_time, как время которое было назначено во время формирования развоза. 
И сохраняю completed_time, чтобы было понятно что данный заказ завершён.

Для некоторых json которые будут подаваться на вход с запросом я использую reqparse.RequestParser(), чтобы просто распарсить аргументы.
А для некоторых других json я получаю их с помощью request.get_json(force=True)
Также я использую marshall_with для того чтобы корректно возвращать данные.

Я создаю классы, которые наследуются от Resource, чтобы потом с помощью этих классов отвечать на запросы.

## 1. Post /couriers
Я проверяю все полученные данные на валидацию. Также проверяю что тип курьера допустимый.
После этого временно добавляю подходящего курьера в таблицу. И если все данные курьеров подходят, то я сохраняю данные в таблице.

## 3. Post /orders
Оно работает аналогично Post /couriers, проверяет что все данные подходят, и после этого добавляет данные в таблицу.
И если все данные подходят, то фиксирую обновление таблицы.

## 2. PATCH /couriers/$courier_id
Я обращаюсь к данным, для начала я смотрю что все данные валидны и нет никаких лишних полей.
Изменяю необходимые поля. После этого я определяю есть ли у курьера незавершенные заказы, которые теперь не будут для него подходить.
Я нахожу заказы которые сейчас есть у курьера, сортирую во возрастанию веса. И начинаю заново как бы собирать заказы.
И если заказ не подходит теперь, то я помечаю что его assign_time None, т.е. теперь этот заказ свободен.
Также я пометила что тип курьера сменился и теперь если у него спросят зарплату, когда он ещё не закончил заказы из этого развода,
то у него нужно будет вычитать эту зарплату смотря на тип который был изначально.
Но я забираю зарплату если у него есть ещё незавершенные заказы.
При этом если тип курьера изменился, и у него не осталось заказов, то зарплата не вычтется когда будет вызываться get/courier
Значит её необходимо вычесть здесь. Если у курьера уже были завершённые заказы, то её нужно оставить.
А если у курьера не было ни одного завершённого заказа за этот развоз, то зарплату надо вычитать.

## 4. POST /orders/assign
Сначала я проверяю что текущий курьер существует. После этого пытаюсь назначить заказы.
Я назначаю курьеры заказы только на тот промежуток времени в который он работает именно сейчас.
Потому что если ему сразу назначить заказы со следующего времени работы, то если перерыв большой, время доставки будет также большим.
И это время доставки будет плохо влиять на его рейтинг. 
Именно поэтому я вычисляю в каком промежутке из рабочих часов курьер работает прямо сейчас.
После этого я ищу подходящие заказы по региону, и фильтрую чтобы они были свободны, а после этого сортирую по возрастанию веса, чтобы взять как можно больше заказов.
Далее я смотрю можно ли доставить заказ сейчас. То есть есть ли у заказа промежуток времени доставки который попадает во время сейчас.
И если заказ можно доставить сейчас, то значит его нужно пометить что его доставляют, сохранить его assign_time.
То есть я прохожусь по заказам которые отфильтровала, сверяю время, и добавляю его. При этом слежу за весом.
И если больше заказов назначить нельзя, то возвращаю необходимые данные.
(Плюс назначаю курьеру зарплату).

## 5. POST /orders/complete
Здесь я сначала проверяю всё ли в порядке с данными. А после этого вычисляю время доставки этого заказа, чтобы сохранить это время.
Я сохраняю данные в сумму времён доставки по району, и увеличиваю количество доставленных заказов также по району.
После этого вычисляю новое среднее время, и если новое время меньше минимального среднего времени, то его необходимо обновить.

## 6. GET /couriers/$courier_id
Здесь я только возвращаю данные из таблицы. И плюс если необходимо уменьшаю зарплату, которую ещё не надо было учитывать.

## 7. Также у меня есть метод GET /orders/$order_id
Я его использовала для того чтобы проверять информацию по заказу

## 8. И плюс метод, который удаляет все данные, которые содержатся в таблице.

Также я составила различные тесты для того чтобы проверить что всё работает корректно. 
Данные тесты сильно зависимы от времени, но можно подкорректировать время так чтобы тест работал прямо сейчас. 
Большую часть времени они будут работать.
Ко многим функциям приложены тесты которые проверяют различные случаи.
