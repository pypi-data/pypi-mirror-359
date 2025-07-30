import tkinter as tk
from PIL import Image, ImageTk
from pyappcreator.utils import calc_anchor, apply_transform, parse_color
from pyappcreator.consts import AnchorType, TransformType


__all__ = ("Graphics", )


class Graphics(object):
    
    def __init__(self, canvas: tk.Canvas):
        self._canvas = canvas
        
        self._images: list[ImageTk.PhotoImage] = []
        
        self._state_stack: list[dict] = []
        self._fill_style: str = "#000000"
        self._stroke_style: str = "#000000"
        self._line_width: int = 1
        self._font: tuple[str, int] = ("arial", 10)
        
    def save(self):
        self._state_stack.append({
            "fill_style": self._fill_style,
            "stroke_style": self._stroke_style,
            "line_width": self._line_width,
            "font": self._font,
        })
        
    def restore(self):
        if not self._state_stack:
            return
        _state = self._state_stack.pop()
        self._fill_style = _state['fill_style']
        self._stroke_style = _state['stroke_style']
        self._line_width = _state['line_width']
        self._font = _state['font']
        
    def set_stroke_style(self, color: str):
        self._stroke_style = parse_color(color)
        
    def set_fill_style(self, color: str):
        self._fill_style = parse_color(color)
        
    def set_line_width(self, width: int):
        self._line_width = max(0, width)
        
    def set_font(self, font: tuple[str, int]):
        self._font = font
        
    def set_font_size(self, size: int):
        self._font = (self._font[0], size)
        
    def fill_rect(self, x: int, y: int, w: int, h: int):
        self._canvas.create_rectangle(x, y, x+w, y+h, 
                                     fill=self._fill_style,
                                     width=0)
        
    def stroke_rect(self, x: int, y: int, w: int, h: int):
        self._canvas.create_rectangle(x, y, x+w, y+h, 
                                     fill=self._stroke_style,
                                     width=self._line_width)
    
    def clear_rect(self, x: int, y: int, w:int, h: int):
        bg_color = self._canvas['background']
        self._canvas.create_rectangle(x, y, x+w, y+h, fill=bg_color, outline=bg_color)
        
    def fill_text(self, text: str, x: int, y: int, anchor: int = 0):
        anchor = calc_anchor(anchor)
        self._canvas.create_text(x, y, text=text, 
                                fill=self._fill_style,
                                font=self._font,
                                anchor=anchor)
        
    def draw_region(self, image: Image.Image, x_src: int, y_src: int, 
                    width: int, height: int, transform: int,
                    x_dest: int, y_dest: int, anchor: int
                    ):
        cropped = image.crop((x_src, y_src, x_src + width, y_src + height))
        
        transformed = apply_transform(cropped, transform)
        
        tk_image = ImageTk.PhotoImage(transformed)
        
        anchor_point = calc_anchor(anchor)
        
        self._canvas.create_image(x_dest, y_dest, image=tk_image, anchor=anchor_point)
        
        self._images.append(tk_image)

    def draw_image(self, image: Image.Image, x: int, y: int, transform: int=TransformType.TRANS_NONE, anchor: int=AnchorType.TOP_LEFT):
        w, h = image.size
        self.draw_region(image, 0, 0, w, h, transform, x, y, anchor)
    
    def clear(self):
        self._canvas.delete("all")
        self._images = []


if __name__ == "__main__":
    from mgr_image import ImageManger
    ImageManger.set_base_url("http://candyworks.oss-cn-qingdao.aliyuncs.com/candy/global")
    img = ImageManger.get_cached_image("Bear_activity.jpg")
    root = tk.Tk()
    root.title("TestCanvas")
    root.geometry(f"800x600")
    canvas = tk.Canvas(root, width=800, height=600, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    graphics = Graphics(canvas)
    graphics.set_fill_style("#00ff00")
    graphics.fill_rect(50, 50, 100, 80)
    
    graphics.set_stroke_style("blue")
    graphics.set_line_width(10)
    graphics.stroke_rect(200, 100, 150, 60)
    
    graphics.set_font(("Times", 10))
    graphics.fill_text("Hello World", 300, 300)
    
    graphics.save()
    graphics.set_font_size(20)
    graphics.fill_text("你好", 500,500)
    graphics.restore()
    
    graphics.fill_text("你好", 600,500)
    
    graphics.clear_rect(60, 60, 80, 60)
    
    graphics.draw_image(img, 360, 50, TransformType.TRANS_NONE)
    root.mainloop()