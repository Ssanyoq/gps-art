import requests


class Map:
    def __init__(self, start_ll=None, start_z=10, size=(650, 450), layer="map"):
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
        # Вычислена мной, почему-то работает

        self.pts = []  # все точки

    def change_size(self, new_size) -> None:
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

    def change_layer(self, new_layer) -> None:
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

    def request_map(self, file_path='static/img/map.png') -> None:
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

    def place_point(self, x, y) -> None:
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

    def change_z(self, z) -> None:
        """
        Меняет значение z
        :param z: новое значение z
        """
        self.z = z
        self.params["z"] = z
        self.spn = 180 / 2 ** self.z

    def move(self, direction) -> None:
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
            # TODO доделать
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

# Ниже визуализатор работы класса на pygame

# import pygame
# pygame.init()
# screen = pygame.display.set_mode((650, 450))
# # Рисуем картинку, загружаемую из только что созданного файла.
# card = Map()
# card.request_map()
# screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
# pygame.display.flip()
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if event.button == 1:
#                 mouse = pygame.mouse.get_pos()
#                 card.place_point(mouse[0], mouse[1])
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.button == 4:
#                 card.change_z(card.z + 1)
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.button == 5:
#                 card.change_z(card.z - 1)
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_LEFT:
#                 card.move("left")
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.key == pygame.K_UP:
#                 card.move("up")
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.key == pygame.K_RIGHT:
#                 card.move("right")
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.key == pygame.K_DOWN:
#                 card.move("down")
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
#             elif event.key == pygame.K_BACKSPACE:
#                 card.undo()
#                 card.request_map()
#                 screen.blit(pygame.image.load("static/img/map.png"), (0, 0))
#                 pygame.display.flip()
# pygame.quit()
