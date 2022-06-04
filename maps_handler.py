import requests


class Map:
    def __init__(self, start_ll=None, start_z=10, size=(650, 450), layer="map", data_string=None):
        """
        :param start_ll: начальная долгота, широта центра карты
        :param start_z: начальный уровень приближения
        :param size: размер возвращаемой картинки
        :param layer: слой карты, снимок которого будет возвращаться
                "map" - схема местности и названия географических объектов, .png
                "sat" - местность, сфотографированная со спутника, .jpg
                "skl" - названия географических объектов, .png
                "trf" - слой пробок, .png
                Слои можно комбинировать, например, можно написать "sat,skl" для получения гибрида
        """
        if start_ll is None:
            start_ll = [37.620070, 55.753630]
        self.ll = start_ll
        self.z = start_z
        self.points = []
        self.layer = layer
        self.size = size
        self.params = {"size": f"{self.size[0]},{self.size[1]}", "l": self.layer, "z": self.z,
                       "ll": f"{self.ll[0]},{self.ll[1]}"}
        self.spn = 180 / 2 ** self.z
        # Переменная для дальнейших вычислений
        # Вычислена мной, работает

        self.pts = []  # все точки
        if data_string is not None:
            self.get_data_from_string(data_string)

    def change_size(self, new_size: (int, int)) -> None:
        """
        Просто изменяет размер карты
        :param new_size: картеж в формата (размер_x, размер_y); x <= 650, y <= 450
        """
        if new_size[0] > 650 or new_size[0] < 1:
            print(f'Недопустимое значение размера карты по x ({new_size[0]}), ничего не изменилось')
            return
        if new_size[1] > 450 or new_size[1] < 1:
            print(f'Недопустимое значение размера карты по y ({new_size[1]}), ничего не изменилось')
            return
        self.size = new_size
        self.params["size"] = f"{self.size[0]},{self.size[1]}"

    def change_layer(self, new_layer: str) -> None:
        """
        Изменяет слой карты
        :param new_layer: слой карты, снимок которого будет возвращаться
                "map" - схема местности и названия географических объектов, .png
                "sat" - местность, сфотографированная со спутника, .jpg
                "skl" - названия географических объектов, .png
                "trf" - слой пробок, .png
                Слои можно комбинировать, например, можно написать "sat,skl" для получения гибрида
        """
        self.layer = new_layer
        self.params["l"] = self.layer

    def request_map(self, file_path='static/img/starter_map.png') -> None:
        """
        Запрашивает изображение карты и сохраняет его в file
        Выводит на экран ошибку, если возникла проблема с запросом
        :param file_path: относительный путь до файла, куда нужно сохранить изображение карты
        """
        link = "https://static-maps.yandex.ru/1.x/"
        response = requests.get(link, params=self.params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(f"Параметры: {self.params}")
            print(f"Ссылка: {link}")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return
        map_file = file_path
        with open(map_file, "wb") as file:
            file.write(response.content)

    def make_pts_param(self) -> None:
        """
        Делает параметр pt и pl
        создает кривую-путь, отмечая точку начала и конца
        Если переменная self.pts пустая, то ничего не происходит
        Если переменная self.pts содержит только 1 точку, то ставится
        только точка A
        """
        if not self.pts:
            if "pt" in self.params.keys():
                self.params.pop("pt")
            return

        self.params["pt"] = f"{self.pts[0][0]},{self.pts[0][1]},pm2am"
        # Точка с буквой A в начале

        if len(self.pts) > 1:
            self.params["pt"] += f"~{self.pts[-1][0]},{self.pts[-1][1]},pm2bm"
            # Точка с буквой B в конце
        else:
            if "pl" in self.params.keys():
                self.params.pop("pl")
            return
        for i, pt in enumerate(self.pts):
            if i == 0:
                self.params["pl"] = f"{pt[0]},{pt[1]}"
            else:
                self.params["pl"] += f",{pt[0]},{pt[1]}"

    def place_point(self, x: int, y: int) -> None:
        """
        Ставит точку на карте, соответствующую x и y. Не ставит ничего,
        если уровень масштабирования меньше 7 (слишком большой масштаб)
        Также есть проверка на допустимое значение долготы и широты -
        -180 <= ll[0] <= 180 and -90 <= ll[1] <= 90
        :param x: x точки
        :param y: y точки
        """

        if self.z <= 7:
            return

        left_up = [self.ll[0] - self.spn * 2.555, self.ll[1] + self.spn * .96]
        # Долгота и широта левого верхнего угла
        right_bottom = [self.ll[0] + self.spn * 2.539, self.ll[1] - self.spn * .99]
        # Долгота и широта правого нижнего угла

        # Коэффициенты были получены лично мной, спустя очень долгое время подбора
        # Вроде это самый масштабируемый способ поставить точку по координатам x и y

        px_val = [(right_bottom[0] - left_up[0]) / 650,
                  (left_up[1] -
                   right_bottom[1]) / 450]
        # сколько градусов широты, долготы в 1 пикселе

        pos = [x,
               self.size[1] - y]
        # Делает так, чтобы x и y возрастали так же, как долгота и широта -
        # долгота возрастает, как и x, слева вправо, а широта - снизу вверх

        point_ll = [pos[0] * px_val[0] + left_up[0], pos[1] * px_val[1] + right_bottom[1]]

        if abs(point_ll[0]) > 180 or abs(point_ll[1]) > 90:
            return
        self.pts.append(point_ll)
        self.make_pts_param()

    def change_z(self, z: int) -> None:
        """
        Меняет значение z
        :param z: новое значение z
        :return: True, если изменилось, False, если нет
        """
        if z >= 22:
            # Не будет нормально работать
            return False
        elif z <= 0:
            # Беды с запросом тогда
            return False
        self.z = z
        self.params["z"] = z
        self.spn = 180 / 2 ** self.z
        return True

    def move(self, direction: str) -> None:
        """
        Изменяет центр карты на 1/2 self.spn
        :param direction: равно "up","down","left" или "right"
        Не будет двигать карту, если после передвижения край
        карты примет недопустимые значения долготы или широты -
        -180 <= ll[0] <= 180 and -90 <= ll[1] <= 90
        """
        change = self.spn / 2
        new_ll = self.ll[:]
        if direction == "up":
            new_ll[1] += change
        elif direction == "down":
            new_ll[1] -= change
        elif direction == "right":
            new_ll[0] += change
        elif direction == "left":
            new_ll[0] -= change
        else:
            return

        if abs(new_ll[0]) > 180 or abs(new_ll[1]) > 90:
            return

        self.ll = new_ll
        self.params["ll"] = f'{self.ll[0]},{self.ll[1]}'

    def undo(self) -> None:
        """
        Удаляет последнюю точку
        """
        if self.pts:
            self.pts.pop()
            self.make_pts_param()

    def get_data_string(self) -> str:
        """
        Делает строку, по которой можно
        воссоздать класс путем вызова функции ниже
        :return: str
        """
        string = ""
        for key in self.params.keys():
            string += f'{key}:{self.params[key]};'
        return string

    def get_data_from_string(self, string: str) -> None:
        """
        Получает данные из строки, созданной методом
        get_data_string()
        :param string: str
        :return: None
        """
        self.params = {}
        params = string.split(';')[:-1]
        for param in params:
            val = param.split(":")
            self.params[val[0]] = val[1]
        if "ll" in self.params.keys():
            self.ll = [float(v) for v in self.params["ll"].split(",")]
        if "z" in self.params.keys():
            self.z = int(self.params["z"])
            self.spn = 180 / 2 ** self.z
        if "size" in self.params.keys():
            self.size = [float(v) for v in self.params["ll"].split(",")]
        if "l" in self.params.keys():
            self.layer = self.params["l"]
        if "pl" in self.params.keys():
            new_pl = self.params["pl"].split(",")
            self.pts = [[float(new_pl[i]), float(new_pl[i + 1])] for i in
                        range(0, len(new_pl) - 1, 2)]
        elif "pt" in self.params.keys():
            new_pt = self.params["pt"].split("~")
            self.pts = [[float(i.split(",")[0]), float(i.split(",")[1])] for i in new_pt]
        # print(f"pts:{self.pts}\nl:{self.layer}\nz:{self.z}\nll:{self.ll}\nspn:{self.spn}")
        # print(f"params:{self.params}") # for debug