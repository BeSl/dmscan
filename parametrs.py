class ImgParametrs:
    source = 0
    def __init__(self, height=None, width=None, source=None):
        self.height = height
        self.width = width
        self.source = source


    def set_params(self, height, width, source):

        if height:
            self.height = height
        if width:
            self.width = width
        if (source or source==0):
            self.source = source