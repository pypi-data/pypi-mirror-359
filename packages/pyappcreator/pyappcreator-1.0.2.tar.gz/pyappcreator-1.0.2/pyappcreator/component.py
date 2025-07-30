from pyappcreator import AppObject, ImageManger, AnchorType, hex_to_rgb
from PIL import Image

__all__ = ("AppImage", "AppLabel", "AppButton", "AppContainer")


class AppImage(AppObject):
    def __init__(self, url:str=""):
        super().__init__()
        self._url = url
        self._image: Image.Image = None
    
    def _load(self, reload:bool):
        if self._url:
            self._image = ImageManger.get_cached_image(self._url)
            self.resize(self._image.width, self._image.height)
            
    def set_url(self, url: str):
        if url:
            self._url = url
            self._load(False)
        
    def init(self):
        self._load(True)
        
    def draw(self):
        if self._image:
            _br = self.body_rect
            self.graphic.draw_image(self._image, _br[0], _br[1])
    
    def loaded(self):
        pass


class AppLabel(AppObject):
    def __init__(self, text:str="", color:tuple[int,int,int,int]=(0,0,0,255), family:str="arial",
                 size: int=10, bold: bool=False, italic: bool=False, anchor: int=AnchorType.TOP_LEFT):
        super().__init__()
        self._text = text
        self._color = color
        self._family = family
        self._size = size
        self._bold = bold
        self._italic = italic
        self.anchor = anchor
        
    def init(self):
        self._measure_text_size()
        
    def draw(self):
        self.graphic.draw_string(self._text, 0, 0, self._color, self.anchor)
        
    def _measure_text_size(self):
        if not self._text:
            return
        self.graphic.save()
        self.graphic.set_font(self._family, self._size, self._bold, self._italic)
        _w, _h = self.graphic.measure_text(self._text)
        self.graphic.restore()
        self.resize(_w, _h)
        
    def set_color(self, color: tuple[int,int,int,int]=(0,0,0,255)):
        self._color = color
        
    def set_family(self, family: str):
        if not family or family == self._family:
            return
        self._family = family
        self._measure_text_size()
        
    def set_bold(self, bold: bool):
        if bold == self._bold:
            return
        self._bold = bold
        self._measure_text_size()
        
    def set_italic(self, italic: bool):
        if italic == self._italic:
            return
        self._italic = italic
        self._measure_text_size()
        
    def set_font_size(self, size: int):
        if size <= 0 or size == self._size:
            return
        self._size = size
        self._measure_text_size()
        
    def set_text(self, text: str):
        if self._text == text:
            return
        self._text = text
        self._measure_text_size()
        
    def set_anchor(self, anchor):
        super().set_anchor(anchor)
        self._measure_text_size()


class AppButton(AppObject):
    def __init__(self, txt: str="", type:int=1, img_bg: Image.Image = None,
                 img_bg_down: Image.Image=None, img_bg_gray: Image.Image = None,
                 mirror: bool = False):
        super().__init__()
        self._img_bg: Image.Image = img_bg
        self._img_bg_down: Image.Image = img_bg_down
        self._img_bg_gray: Image.Image = img_bg_gray
        self._btn_text: str = txt
        self._mirror: bool = mirror
        self._type: int = type # 1 scale, 2 replace


class AppContainer(AppObject):
    def __init__(self, width:int = 0, height:int = 0, 
                 img_bg: Image.Image = None,
                 color: str="#000000", alpha:float=1.0):
        super().__init__()
        self.witdh = width
        self.height = height
        self.alpha = alpha
        self._bg_color = hex_to_rgb(color)
        self._bg_img: Image.Image = img_bg

