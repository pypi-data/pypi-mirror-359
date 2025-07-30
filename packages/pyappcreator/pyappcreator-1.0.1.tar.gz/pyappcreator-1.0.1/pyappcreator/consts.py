from enum import Enum


__all__ = ("TransformType", "AnchorType", "COLOR_MAP", "CALLBACK_TYPE")


class CALLBACK_TYPE(Enum):
    ON_INIT = "on_init"
    ON_SHOW = "on_show"
    ON_ENTER = "on_enter"
    ON_UPDATE = "on_update"
    ON_EXIT = "on_exit"
    RE_CALC_DRAW_POINT = "re_calc_draw_point"
    

class TransformType(object):
    TRANS_NONE = 0
    TRANS_MIRROR = 1
    TRANS_ROT90 = 2
    TRANS_MIRROR_ROT90 = 3
    TRANS_ROT180 = 4
    TRANS_MIRROR_ROT180 = 5
    TRANS_ROT270 = 6
    TRANS_MIRROR_ROT270 = 7
    

class AnchorType(object):
    LEFT = 1
    RIGHT = 2
    HCENTER = 4
    TOP = 8
    BOTTOM = 16
    VCENTER = 32
    TOP_LEFT = TOP | LEFT
    TOP_HCENTER = TOP | HCENTER
    TOP_RIGHT = TOP | RIGHT
    VCENTER_LEFT = VCENTER | LEFT
    VCENTER_HCENTER = VCENTER | HCENTER
    VCENTER_RIGHT = VCENTER | RIGHT
    BOTTOM_LEFT = BOTTOM | LEFT
    BOTTOM_HCENTER = BOTTOM | HCENTER
    BOTTOM_RIGHT = BOTTOM | RIGHT
    
    
COLOR_MAP = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF"
}
