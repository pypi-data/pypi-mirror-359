from PIL import Image
from pyappcreator.consts import TransformType, AnchorType, COLOR_MAP
import struct
from io import BytesIO
import requests
import subprocess
import sys
import os


__all__ = ("is_mac_platform", "apply_transform", "calc_anchor", "calc_draw_point", "parse_color",
           "DataInputStream", "DataOutputStream", "sync_get_bin", "sync_read_file", "hex_to_rgb",
           "sync_write_file", "sync_get_text", "sync_get_json", "sync_post_text", "sync_post_json",
           "run_sync_cmd", "get_filename", "get_file_abs_path")


_platform = sys.platform


def is_mac_platform() -> bool:
    return _platform == "darwin"


def run_sync_cmd(cmd: str) -> tuple[int, str, str]:
    if not cmd:
        return [0, "", ""]
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", check=True)
    return result.returncode, result.stdout, result.stderr


def get_filename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def get_file_abs_path(path: str) -> str:
    return os.path.dirname(os.path.abspath(path))


def apply_transform(image: Image.Image, transform: int=TransformType.TRANS_NONE) -> Image.Image:
    if transform == TransformType.TRANS_NONE:
        return image.copy()
    
    transformed = image.copy()
    
    if transform == TransformType.TRANS_MIRROR:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif transform == TransformType.TRANS_ROT90:
        transformed = transformed.transpose(Image.Transpose.ROTATE_90)
    elif transform == TransformType.TRANS_MIRROR_ROT90:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        transformed = transformed.transpose(Image.Transpose.ROTATE_90)
    elif transform == TransformType.TRANS_ROT180:
        transformed = transformed.transpose(Image.Transpose.ROTATE_180)
    elif transform == TransformType.TRANS_MIRROR_ROT180:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        transformed = transformed.transpose(Image.Transpose.ROTATE_180)
    elif transform == TransformType.TRANS_ROT270:
        transformed = transformed.transpose(Image.Transpose.ROTATE_270)
    elif transform == TransformType.TRANS_MIRROR_ROT270:
        transformed = transformed.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        transformed = transformed.transpose(Image.Transpose.ROTATE_270)
    
    return transformed

    
def calc_anchor(anchor: int=AnchorType.TOP_LEFT) -> str:
    anchor_point = "nw"

    if anchor & AnchorType.HCENTER:
        anchor_point = anchor_point[0] + "c"
    elif anchor & AnchorType.RIGHT:
        anchor_point = anchor_point[0] + "e"
        
    if anchor & AnchorType.VCENTER:
        anchor_point = "c" + anchor_point[1]
    elif anchor & AnchorType.BOTTOM:
        anchor_point = "s" + anchor_point[1]
    
    return anchor_point


def calc_draw_point(x, y, width, height, anchor: int=0) -> tuple[int, int]:
    draw_x, draw_y = x, y
    if anchor & AnchorType.HCENTER:
        draw_x -= width // 2
    elif anchor & AnchorType.RIGHT:
        draw_x -= width
        
    if anchor & AnchorType.VCENTER:
        draw_y -= height // 2
    elif anchor & AnchorType.BOTTOM:
        draw_y -= height
    return draw_x, draw_y


def parse_color(color: str) -> str:
    if color.lower() in COLOR_MAP:
        return COLOR_MAP[color]
    return color


class DataInputStream(object):
    def __init__(self, stream: bytes) -> None:
        self.stream = BytesIO(stream)

    def read_boolean(self):
        return struct.unpack('?', self.stream.read(1))[0]

    def read_byte(self):
        return struct.unpack('>b', self.stream.read(1))[0]

    def read_unsigned_byte(self):
        return struct.unpack('>B', self.stream.read(1))[0]

    def read_char(self):
        return chr(struct.unpack('>H', self.stream.read(2))[0])

    def read_double(self):
        return struct.unpack('>d', self.stream.read(8))[0]

    def read_float(self):
        return struct.unpack('>f', self.stream.read(4))[0]

    def read_short(self):
        return struct.unpack('>h', self.stream.read(2))[0]

    def read_unsigned_short(self):
        return struct.unpack('>H', self.stream.read(2))[0]

    def read_long(self):
        return struct.unpack('>q', self.stream.read(8))[0]

    def read_utf8(self):
        _length = self.read_unsigned_short()
        return self.stream.read(_length).decode('utf-8')

    def read_int(self):
        return struct.unpack('>i', self.stream.read(4))[0]

    def read_bytes(self, length: int) -> bytes:
        return self.stream.read(length)


class DataOutputStream(object):
    def __init__(self):
        self.stream = BytesIO()

    def write_boolean(self, val: bool):
        self.stream.write(b'\x01' if val else '\x00')

    def write_byte(self, val: int):
        self.stream.write(struct.pack('>b', val))

    def write_unsigned_byte(self, val: int):
        self.stream.write(struct.pack('>B', val))

    def write_short(self, val: int):
        self.stream.write(struct.pack('>h', val))

    def write_unsigned_short(self, val: int):
        self.stream.write(struct.pack('>H', val))

    def write_int(self, val: int):
        self.stream.write(struct.pack('>i', val))

    def write_long(self, val: int):
        self.stream.write(struct.pack('>q', val))

    def write_float(self, val: float):
        self.stream.write(struct.pack('>f', val))

    def write_double(self, val: float):
        self.stream.write(struct.pack('>d', val))

    def write_char(self, val: str):
        for s in val:
            self.stream.write(struct.pack('>H', ord(s)))

    def write_utf8(self, s: str):
        encoded = s.encode('utf-8')
        self.write_unsigned_short(len(encoded))
        self.stream.write(encoded)

    def write_bytes(self, val: bytes):
        self.stream.write(val)

    def to_bytes(self):
        return self.stream.getvalue()


def _sync_http(url, r_type="json", m_type="get", **kwargs):
    res = requests.request(m_type, url, **kwargs)
    if r_type == "json":
        res = res.json()
    elif r_type == "text":
        res = res.text
    else:
        res = res.content
    return res


def sync_get_bin(url, **kwargs):
    return _sync_http(url, r_type="bin", m_type="get", **kwargs)


def sync_get_text(url, **kwargs):
    return _sync_http(url, r_type="text", m_type="get", **kwargs)


def sync_get_json(url, **kwargs):
    return _sync_http(url, r_type="json", m_type="get", **kwargs)


def sync_post_text(url, **kwargs):
    return _sync_http(url, r_type="text", m_type="post", **kwargs)


def sync_post_json(url, **kwargs):
    return _sync_http(url, r_type="json", m_type="post", **kwargs)


def sync_read_file(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def sync_write_file(path, data, mode="w"):
    with open(path, mode) as f:
        f.write(data)
        

def hex_to_rgb(hex_color: str="#000000") -> tuple[int, int, int, int]:
    color = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    color.append(255)
    return tuple(color)