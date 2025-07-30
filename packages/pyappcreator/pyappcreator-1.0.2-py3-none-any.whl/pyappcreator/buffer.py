from PIL import Image, ImageDraw, ImageFont
from typing import Union
import math
from pyappcreator.utils import apply_transform, is_mac_platform, calc_draw_point
from pyappcreator.consts import TransformType, AnchorType


__all__ = ("BufferedImage", "BufferedGraphics")


class BufferedGraphics(object): pass


class BufferedImage(object):
    def __init__(self, w: int, h: int, bg: tuple[int, int, int, int]=(255,255,255, 0)):
        self._width = w
        self._height = h
        self._bg_color: tuple[int, int, int, int] = bg
        self._buffer = Image.new("RGBA", (self._width, self._height), self._bg_color)
        self._drawer = ImageDraw.Draw(self._buffer)
        
    def get_drawer(self) -> ImageDraw.ImageDraw:
        return self._drawer
        
    def get_graphics(self) -> BufferedGraphics:
        return BufferedGraphics(self)
    
    def get_image(self) -> Image.Image:
        return self._buffer

    def get_size(self) -> tuple[int, int]:
        return (self._width, self._height)
        
        
class BufferedGraphics(object):
    def __init__(self, image: BufferedImage):
        self._image: BufferedImage = image
        self._font = ImageFont.load_default()
        self._text_baseline_offset: int = 0
        
        self._text_size: int = 12
        self._text_family: str = "arial"
        self._text_bold: bool = False
        self._text_italic: bool = False

        self._angle: int = 0
        self._scale_x: float = 1.0
        self._scale_y: float = 1.0
        self._alpha: float = 1.0
        self._anchor: int = AnchorType.TOP_LEFT
        self._draw_x: int = 0
        self._draw_y: int = 0
        
        self._state_stack: list[dict] = []
        
        self._cached_fonts: dict[str, dict] = {}
        self._cached_fonts[self._get_font_cache_key()] = {"font": self._font, "text_baseline_offset": self._text_baseline_offset}
        
    def _get_font_cache_key(self) -> str:
        return "_".join([self._text_family, str(self._text_size), str(self._text_bold), str(self._text_italic)])
    
    def _update_font(self):
        _key = self._get_font_cache_key()
        if _key in self._cached_fonts:
            self._font = self._cached_fonts[_key]['font']
            self._text_baseline_offset = self._cached_fonts[_key]['text_baseline_offset']
        else:
            font = ImageFont.truetype(self._text_family, self._text_size)
            if self._text_bold or self._text_italic:
                font = ImageFont.truetype(
                    self._text_family, self._text_size,
                    layout_engine=ImageFont.Layout.BASIC if self._text_bold and self._text_italic else 
                    ImageFont.Layout.RAQM
                )
            
            try:
                ascent, descent = font.getmetrics()
                self._text_baseline_offset = descent
            except:
                self._text_baseline_offset = 0
                
            self._font = font
            self._cached_fonts[_key] = {'font': font, "text_baseline_offset": self._text_baseline_offset}
    
    def save(self):
        self._state_stack.append({
            "text_size": self._text_size,
            "text_family": self._text_family,
            "text_bold": self._text_bold,
            "text_italic": self._text_italic,
            "angle": self._angle,
            "scale_x": self._scale_x,
            "scale_y": self._scale_y,
            "alpha": self._alpha,
            "anchor": self._anchor,
            "draw_x": self._draw_x,
            "draw_y": self._draw_y
        })
    
    def restore(self):
        if not self._state_stack:
            return
        _state = self._state_stack.pop()
        self._text_bold = _state['text_bold']
        self._text_italic = _state['text_italic']
        self._text_size = _state['text_size']
        self._text_family = _state['text_family']
        self._angle = _state['angle']
        self._scale_x = _state['scale_x']
        self._scale_y = _state['scale_y']
        self._alpha = _state['alpha']
        self._anchor = _state['anchor']
        self._draw_x = _state['draw_x']
        self._draw_y = _state['draw_y']
        
    def update_config(self, alpha: float=1.0, 
                      angle: int = 0, 
                      anchor: int = AnchorType.TOP_LEFT,
                      draw_x: int = 0,
                      draw_y: int = 0,
                      scale_x: float=1.0, 
                      scale_y: float=1.0):
        self._alpha = alpha
        self._anchor = anchor
        self._angle = angle
        self._draw_x = draw_x
        self._draw_y = draw_y
        self._scale_x = scale_x
        self._scale_y = scale_y
    
    def set_font(self, name:str="arial", size: int=12, bold:bool=False, italic:bool=False):
        if is_mac_platform():
            name = f"{name[0].upper()}{name[1:]}"
        self._text_family = name
        self._text_size = size
        self._text_bold = bold
        self._text_italic = italic
        self._update_font()
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, 
                  color:tuple[int, int, int, int]=(0,0,0,255), 
                  line_width:int=1):
        self._image.get_drawer().line([(x1, y1), (x2, y2)], fill=color, width=line_width)
        
    def draw_rect(self, x: int, y: int, width: int, heiht: int, 
                  color:tuple[int, int, int, int]=(0,0,0,255), 
                  line_width:int=1):
        self._image.get_drawer().rectangle([(x, y), (x+width, y+heiht)], outline=color, width=line_width)
        
    def fill_rect(self, x: int, y: int, width: int, height: int,
                  fill_color: tuple[int, int, int, int] = (0,0,0,255), 
                  stroke_color:tuple[int,int,int,int]=(0,0,0,255),
                  line_width: int = 0):
        self._image.get_drawer().rectangle([(x, y), (x+width, y+height)], 
                                           fill=fill_color, 
                                           outline=stroke_color, 
                                           width=line_width)
        
    def measure_text(self, text: str) -> tuple[int, int]:
        bbox = self._font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    def _final_draw_point(self, x: int, y: int) -> tuple[int, int]:
        return self._draw_x + x, self._draw_x + y
        
    def draw_string(self, text: str, x: int, y: int, 
                    color: tuple[int,int,int,int] = (0,0,0,255),
                    anchor=AnchorType.TOP_LEFT):
        if not text:
            return
        text_width, text_height = self.measure_text(text)
        
        draw_x, draw_y = calc_draw_point(x, y, text_width, text_height, anchor)
            
        draw_y -= self._text_baseline_offset
        
        draw_x, draw_y = self._final_draw_point(draw_x, draw_y)
        
        self._image.get_drawer().text((draw_x, draw_y), text, fill=color, font=self._font)
        
    def draw_image(self, image: Union[BufferedImage, Image.Image], x: int, y: int, alpha: float=1.0):
        if isinstance(image, BufferedImage):
            img = image.get_image()
        else:
            img = image
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            
        if alpha < 1.0:
            alpha_img = Image.new("RGBA", img.size)
            alpha_img.putdata([(r, g, b, int(a * alpha)) for (r, g, b, a) in img.getdata()])
            img = alpha_img
        
        x, y = self._final_draw_point(x, y)
            
        self._image.get_image().alpha_composite(img, (x, y))
            
    def draw_region(self, image: Union[BufferedImage, Image.Image], x_src: int, y_src: int, width: int, height: int,
                    transform: int, x_dest: int, y_dest: int, anchor: int=AnchorType.TOP_LEFT, alpha: float=1.0):
        if isinstance(image, BufferedImage):
            img = image.get_image()
        else:
            img = image
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            
        src_box = (x_src, y_src, x_src + width, y_src + height)
        cropped = img.crop(src_box)
        
        transformed = apply_transform(cropped, transform)
        
        if alpha < 1.0:
            alpha_img = Image.new("RGBA", transformed.size)
            alpha_img.putdata([(r, g, b, int(a*alpha)) for (r, g, b, a) in transformed.getdata()])
            transformed = alpha_img
        
        region_w, region_h = transformed.size
        draw_x, draw_y = calc_draw_point(x_dest, y_dest, region_w, region_h, anchor)
        draw_x, draw_y = self._final_draw_point(draw_x, draw_y)
        
        self._image.get_image().alpha_composite(transformed, (draw_x, draw_y))
    
    def draw_image_advance_simple(self, image: Union[BufferedImage, Image.Image], src_x: int, src_y: int, src_w: int, src_h: int):
        self.draw_image_advance(image, 0, 0, self._angle, self._scale_x, self._scale_y, self._anchor, self._alpha,
                                (src_x, src_y, src_w, src_h))
    
    def draw_image_advance(self, image: Union[BufferedImage, Image.Image], 
                          x: int, y: int, 
                          angle: float = 0, 
                          scale_x: float = 1.0, 
                          scale_y: float = 1.0,
                          anchor: int = AnchorType.TOP_LEFT,
                          alpha: float = 1.0,
                          src_rect: tuple[int, int, int, int] = None):
        if isinstance(image, BufferedImage):
            img = image.get_image()
        else:
            img = image
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            
        if src_rect:
            x_src, y_src, src_width, src_height = src_rect
            img = img.crop((x_src, y_src, x_src + src_width, y_src + src_height))
        
        original_width, original_height = img.size
        
        scaled_width = int(original_width * scale_x)
        scaled_height = int(original_height * scale_y)
        if scale_x != 1.0 or scale_y != 1.0:
            img = img.resize((scaled_width, scaled_height), Image.LANCZOS)
        
        if angle != 0:
            radians = math.radians(angle)
            cos = abs(math.cos(radians))
            sin = abs(math.sin(radians))
            
            new_width = int((scaled_width * cos) + (scaled_height * sin))
            new_height = int((scaled_width * sin) + (scaled_height * cos))
            
            rotated_img = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
            
            anchor_x, anchor_y = 0, 0
            if anchor & AnchorType.HCENTER:
                anchor_x = scaled_width / 2
            elif anchor & AnchorType.RIGHT:
                anchor_x = scaled_width
                
            if anchor & AnchorType.VCENTER:
                anchor_y = scaled_height / 2
            elif anchor & AnchorType.BOTTOM:
                anchor_y = scaled_height
                
            rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)
            
            pos_x = (new_width - rotated.width) // 2 - anchor_x + scaled_width / 2
            pos_y = (new_height - rotated.height) // 2 - anchor_y + scaled_height / 2
            
            rotated_img.paste(rotated, (int(pos_x), int(pos_y)), rotated)
            img = rotated_img
        
        if alpha < 1.0:
            alpha_img = Image.new("RGBA", img.size)
            alpha_img.putdata([(r, g, b, int(a * alpha)) for (r, g, b, a) in img.getdata()])
            img = alpha_img
        
        draw_width, draw_height = img.size
        draw_x, draw_y = calc_draw_point(x, y, draw_width, draw_height, anchor)
        draw_x, draw_y = self._final_draw_point(draw_x, draw_y)
        
        self._image.get_image().alpha_composite(img, (draw_x, draw_y))
        

if __name__ == "__main__":
    from mgr_image import ImageManger
    ImageManger.set_base_url("http://candyworks.oss-cn-qingdao.aliyuncs.com/candy/global")
    tmp_img = ImageManger.get_cached_image("Bear_activity.jpg")
    import tkinter as tk
    from graphic import Graphics
    root = tk.Tk()
    root.title("Test")
    root.geometry(f"800x600")
    canvas = tk.Canvas(root, width=800, height=600, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    cg = Graphics(canvas)
    img = BufferedImage(800, 600)
    graphics = img.get_graphics()

    graphics.draw_line(10, 10, 100, 100, (255, 0, 0, 100), line_width=10)
    
    graphics.draw_rect(200, 200, 100, 100, (0, 255, 0, 255), line_width=2)
    
    graphics.fill_rect(350, 200, 100, 100, (0, 0, 255, 255), (0, 255, 0, 255), line_width=3)
    graphics.draw_line(100, 100, 101, 101, (0, 0, 0, 255))
    graphics.set_font(size=50)
    graphics.draw_string("Hello", 100, 100, (0, 0, 255, 255), anchor=AnchorType.LEFT|AnchorType.TOP)
    width, height = graphics.measure_text("Hello")
    graphics.draw_rect(100, 100, width, height, (0,0,0,255), line_width=1)
    
    graphics.draw_image(tmp_img, 0, 0, 1.0)
    
    graphics.draw_region(tmp_img, 0, 0, 240, 320, TransformType.TRANS_MIRROR_ROT90, 300, 200, anchor=AnchorType.BOTTOM_RIGHT)
    graphics.draw_line(300, 200, 301, 201, (255, 0, 0, 255))
    graphics.draw_line(0, 0, 100, 100)
    graphics.fill_rect(50, 50, 50, 50)
    graphics.draw_rect(100, 100, 100, 100)
    graphics.draw_string("hello world", 250, 250)
    graphics.draw_image(tmp_img, 300, 100, 0.2)
    graphics.draw_region(tmp_img, 100, 100, 100, 100, TransformType.TRANS_NONE, 400, 400, alpha=0.2)
    
    graphics.draw_image_advance(tmp_img, 500, 200, scale_x=0.6, scale_y=0.6, anchor=AnchorType.VCENTER_HCENTER, alpha=0.8, src_rect=(0, 0, 100, 200), angle=90)
    graphics.draw_line(500, 200, 501, 201, (255, 0, 0, 255))
    cg.draw_image(img.get_image(), 0, 0)
    root.mainloop()
