from market_graphics_scene import QMarketGraphicsScene

class Market():
    box_offices = {}

class Scene:
    def __init__(self):
        """ Настройки сцены """
        self.nodes = []
        self.edges = []

        self.scene_width = 700
        self.scene_height = 400

        self.initUI()

    def initUI(self):
        self.grScene = QMarketGraphicsScene(self)
        #self.grScene.setGraphScene(self.scene_width, self.scene_height)
