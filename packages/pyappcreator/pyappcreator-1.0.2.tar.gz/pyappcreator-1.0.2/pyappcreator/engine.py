from pyappcreator.consts import AnchorType, CALLBACK_TYPE
from pyappcreator.buffer import BufferedGraphics, BufferedImage
from pyappcreator.utils import calc_draw_point
import tkinter as tk
from pyappcreator.graphic import Graphics
import time


__all__ = ("AppObject", "AppEngine", "Director")


class AppObject(object): pass


class AppObject(object):
    def __init__(self):
        self.graphic: BufferedGraphics = AppEngine.get_buffer_graphics()
        self._children: list[AppObject] = []
        self._visible: bool = True
        
        self.appoint_x: int = 0
        self.appoint_y: int = 0
        self.draw_x: int = 0
        self.draw_y: int = 0
        
        self.w: int = 0
        self.h: int = 0
        
        self.anchor: int = AnchorType.TOP_LEFT
        
        self.body_rect: list[int] = [0, 0, 0, 0]
        self.hot_zone: list[tuple[int, int, int, int]] = []
        self.view_zone: list[int] = [0, 0, 0, 0]
        self.fix_hot_zone: bool = False
        
        self.parent: AppObject = None

        self._running: bool = False
        
        self.scale_x: float = 1.0
        self.scale_y: float = 1.0
        self.alpha: float = 1.0
        self.rotate: int = 0
        
    def _call_events_for_children(self, ctype: CALLBACK_TYPE):
        if self._children:
            for c in self._children:
                if c._visible:
                    _func = getattr(c, ctype.value)
                    if _func:
                        _func()
                        
    def _calc_body_rect(self):
        if self.w <= 0 or self.h <= 0:
            return
        _w = 0
        _h = 0
        _w, _h = calc_draw_point(_w, _h, self.w, self.h) 
        self.body_rect[0] = _w
        self.body_rect[1] = _h
        self.body_rect[2] = self.w
        self.body_rect[3] = self.h
        
        if not self.fix_hot_zone:
            self.update_hot_zone()
            
        self.re_calc_draw_point()
               
    def _re_calc_draw_point(self):
        _x = self.appoint_x
        _y = self.appoint_y
        
        if not self._children:
            if self.parent:
                _x += self.parent.body_rect[0]
                _y += self.parent.body_rect[1]
        
        self.draw_x = self.parent.draw_x + _x if self.parent else _x
        self.draw_y = self.parent.draw_y + _y if self.parent else _y

    def resize(self, w: int, h: int):
        self.w = w
        self.h = h
        self._calc_body_rect()
        
    def set_anchor(self, anchor: int):
        self.anchor = anchor
        self._calc_body_rect()
        
    def update_hot_zone(self):
        self.hot_zone.clear()
        self.hot_zone.append(self.body_rect)
        
    def set_hot_zone(self, hot_zone: list[tuple[int, int, int, int]]):
        self.fix_hot_zone = True
        self.hot_zone = hot_zone
    
    def add_child(self, child: AppObject):
        c: AppObject = child
        self._children.append(c)
        c.parent = self
        c.re_calc_draw_point()
        
    def move_to(self, x: int, y: int):
        self.appoint_x = x
        self.appoint_y = y
        self.re_calc_draw_point()
        
    def hidden(self):
        self._visible = False
        
    def show(self):
        self._visible = True
         
    def re_calc_draw_point(self):
        self._re_calc_draw_point()
        self._call_events_for_children(CALLBACK_TYPE.RE_CALC_DRAW_POINT)
                        
    def on_show(self):
        if not self._running or not self._visible:
            return
        
        if self.alpha <= 0:
            return

        self.graphic.save()
        self.graphic.update_config(alpha=self.alpha, 
                             anchor=self.anchor, 
                             draw_x=self.draw_x, 
                             draw_y=self.draw_y, 
                             scale_x=self.scale_x, 
                             scale_y=self.scale_y)
        self.draw()
        self.graphic.restore()
        self._call_events_for_children(CALLBACK_TYPE.ON_SHOW)
        
    def on_init(self):
        self.init()
        self._call_events_for_children(CALLBACK_TYPE.ON_INIT)
        
    def on_enter(self):
        self._running = True
        self.enter()
        self._call_events_for_children(CALLBACK_TYPE.ON_ENTER)
        
    def on_exit(self):
        self._running = False
        self._call_events_for_children(CALLBACK_TYPE.ON_EXIT)
        self.exit()
        
    def on_update(self):
        if not self._running:
            return
        self.update()
        self._call_events_for_children(CALLBACK_TYPE.ON_UPDATE)
        
    def init(self):
        pass
    
    def draw(self):
        pass
    
    def enter(self):
        pass
    
    def update(self):
        pass
    
    def exit(self):
        pass


class _AppEngine(object): pass


class _Director(object):
    def __init__(self):
        self._next_view: AppObject = None
        self._init: bool = False
        self._running_view: AppObject = None
    
    def run(self, view: AppObject):
        self._next_view =view
        self._init = False
        
    def replace(self, view: AppObject):
        self.run(view)
        
    def main_loop(self):
        self._draw_view()
        
    def _draw_view(self):
        if self._next_view and not self._init:
            self._next_view.on_init()
            self._init = True
        elif self._next_view:
            self._switch_view()
        elif self._running_view:
            self._running_view.on_update()
            self._running_view.on_show()
          
    def _switch_view(self):
        if self._running_view:
            self._running_view.on_exit()
        
        self._running_view = self._next_view
        self._next_view = None
        self._running_view.on_enter()
        

Director = _Director()
    

class _AppEngine(object):
    def __init__(self, title: str="TkGame", width: int = 800, height:int = 600, fps: int = 60):
        self.root = tk.Tk()
        self.width = width
        self.height = height
        self.fps = fps
        
        self.root.title(title)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) >> 1
        y = (screen_height - height) >> 1
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.canvas = tk.Canvas(
            self.root, width=width, height=height, bg="black", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.graphics = Graphics(self.canvas)
        
        self.buff_image = BufferedImage(width, height)
        self.buff_graphics = self.buff_image.get_graphics()
        
        self.is_running: bool = False
        self.current_frame: int = 0
        
    def resize(self, w: int, h: int):
        self.width = w
        self.height = h
        
    def get_buffer_graphics(self):
        return self.buff_graphics
        
    def _game_loop(self):
        self.current_frame += 1
        _delay = 1000//self.fps
        self.graphics.clear()
        _start = int(time.time() * 1000)
        Director.main_loop()
        _used = int(time.time() * 1000) - _start
        if _used >= _delay:
            _delay = 0
        else:
            _delay = _delay - _used
        self.graphics.draw_image(self.buff_image.get_image(), 0, 0)
        self.root.after(_delay, self._game_loop)
        
    def run_first_view(self, view: AppObject):
        if not self.is_running:
            self.is_running = True
            Director.run(view)
            self.root.after(0, self._game_loop)
            self.root.mainloop()
        

AppEngine = _AppEngine()
