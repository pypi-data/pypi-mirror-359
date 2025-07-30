from PIL import Image
from io import BytesIO
from pyappcreator.utils import sync_get_bin


__all__ = ("ImageManger", )


class _ImageManager(object):
    def __init__(self):
        self._base_url: str = ""
        self._images: dict[str, Image.Image] = {}
        
    def set_base_url(self, base_url: str):
        self._base_url = base_url
        
    def _load_cached_image(self, path: str):
        if path and path not in self._images:
            self._images[path] = self._load_image(path)
            
    def get_cached_image(self, path: str) -> Image.Image:
        if path not in self._images:
            self._load_cached_image(path)
        return self._images[path]
    
    def free_cached_image(self, path: str):
        if path in self._images:
            self._images.pop(path)
            
    def _load_image_from_url(self, path: str) -> Image.Image:
        _final_url = f"{self._base_url}/{path}"
        return Image.open(BytesIO(sync_get_bin(_final_url)))
        
    def _load_image(self, path: str) -> Image.Image:
        try:
            return Image.open(path)
        except FileNotFoundError:
            if not self._base_url:
                raise ValueError(f"base url not set.")
            return self._load_image_from_url(path)


ImageManger = _ImageManager()


if __name__ == "__main__":
    ImageManger.set_base_url("http://candyworks.oss-cn-qingdao.aliyuncs.com/candy/global")
    img = ImageManger.get_cached_image("Bear_activity.jpg")
    print(img)
    