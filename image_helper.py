import rembg
from PIL import Image, ImageEnhance
from io import BytesIO


class ImageHelper(object):
    def __init__(self):
        self._max_size = (512, 512)

    def set_size_limit(self, max_width, max_height):
        self._max_size = (max_width, max_height)

    def load(self, img_path):
        self._source_img = self._scale_down(Image.open(img_path))
        self._head_img = None
        self._final_img = None

    def load_bytes(self, img):
        self._source_img = self._scale_down(Image.open(BytesIO(img)))
        self._head_img = None
        self._final_img = None

    def remove_background(self):
        self._head_img = rembg.remove(self._source_img)

    def gen_tiktok_style(self):
        background_img = Image.new("RGBA", self._source_img.size, (0, 0, 0, 255))
        aqua_img = self._generate_background(
            (37, 244, 238, 255),
            (int(-16 * (self._max_size[0] / 512)), int(-5 * (self._max_size[1] / 512))),
        )
        pink_img = self._generate_background(
            (254, 44, 85, 255), (int(16 * (self._max_size[0] / 512)), 0)
        )

        final_img = self._composite(aqua_img, background_img)
        final_img = self._composite(pink_img, final_img)
        final_img = self._composite(self._adjust_head_img(self._head_img), final_img)
        self._final_img = final_img

    def _adjust_head_img(self, img):
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.15)
        saturation_enhancer = ImageEnhance.Color(img)
        return saturation_enhancer.enhance(0)

    def _generate_background(self, color, offset=(0, 0)):
        out_img = Image.new("RGBA", self._head_img.size, color=(0, 0, 0, 0))
        for x in range(self._head_img.width):
            for y in range(self._head_img.height):
                alpha = self._head_img.getpixel((x, y))[3]
                new_x, new_y = x + offset[0], y + offset[1]
                if (
                    alpha > 0
                    and (0 <= new_x < out_img.size[0])
                    and (0 <= new_y < out_img.size[1])
                ):
                    out_img.putpixel((new_x, new_y), color)
        return out_img

    def _composite(self, upper_img, lower_img):
        return Image.alpha_composite(lower_img, upper_img)

    def _scale_down(self, img):
        scale = min(self._max_size[0] / img.width, self._max_size[1] / img.height)
        if scale < 1:
            img.thumbnail((int(img.width * scale), int(img.height * scale)))
        return img

    def show(self):
        self._final_img.show()

    def save(self, img_path):
        self._final_img.save(img_path)

    def get_img(self):
        return self._final_img


if __name__ == "__main__":
    name = "img/test3"

    helper = ImageHelper()
    helper.set_size_limit(512, 512)
    helper.load(f"{name}.jpg")
    helper.remove_background()
    helper.gen_tiktok_style()
    helper.show()
    helper.save(f"{name}-out.png")
