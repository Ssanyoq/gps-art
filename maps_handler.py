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
        self.spn = 180 / 2 ** self.z  # переменная для дальнейших вычислений

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
