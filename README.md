# GPS Art
## Возможность разнообразить себе прогулки

---
Gps art, изначально, — интересное использование возможностей приложений для
тренировок. Например, популярное приложение Strava показывает пройденный за 
время тренировки путь на карте, и некоторые креативные люди придумали этим путем создавать
разные рисунки.

Нам очень понравилась эта идея, мы захотели попробовать и поняли,
что самое сложное — спланировать, куда и когда надо идти. Обычные навигаторы созданы
в основном для нахождения кратчайшего пути между 2 точками, а не для
быстрого добавления новых точек. Также навигатор будет прокладывать маршрут только по знакомым 
ему улицам, и если попытаться сделать маршрут через, например, поле, то 
навигатор обогнет его.
##### Для облегчения планирования прогулки или тренировки создан наш сайт, названный _GPS art_.

---

## Что есть на сайте?
 
 * ###  Удобная система прокладывания маршрута
    На отдельной странице пользователь может создавать маршрут, просто кликая на изображение
    карты, также там есть возможность сохранять маршрут под нужным пользователю названием.
 * ###  Удобная система просмотра уже созданных маршрутов
    Для каждого пользователя создана страница, где в форме таблицы показаны все созданные им
    маршруты. Их можно удалить, нажав на специальную кнопку, или, нажав на название, просмотреть
 * ### Система регистрации
    Для создания маршрутов пользователю необходимо зарегистрироваться на сайте

---

## Как запустить?

### 1. Скачать проект
Это можно сделать скачав `.zip` файл в github (ну или не в github) и распаковав его

### 2. Скачать необходимые модули
Для этого есть файл `requirements.txt`, можно установить модули, используя инструменты терминала вашей ОС
(на Windows это делается командой `pip install -r requirements.txt`, а на 
Linux `pip3 install -r requirements.txt`)

### 3. Запустить `main.py`

### Готово!

---

## Детали для разработчиков

### Создание маршрутов
Эта система была сделана на основе **Static API Яндекс.Карт**. 
Пользователь кликает на
изображение карты/кнопки, и сервер получает информацию через AJAX. Если пользователь кликнул на карту,
то сервер получает только координаты мыши во время нажатия, после различных вычислений обращается к API
и меняет клиенту картинку. Конечно, можно было сделать через JavaScript API Яндекс.Карт, но это
слишком просто

### База данных
База данных — файл `db/users.db`. Этот файл будет создан при запуске программы(если его нет)

### Карты пользователей
Карты пользователей хранятся в папке `static/img/users_maps`. Если такой папки нет, то она
будет создана при запуске. Название файлов генерируется так, чтобы оно точно не могло повториться.
Оно формата `map-<id пользователя>-<время в наносекундах[4:]>.png`

