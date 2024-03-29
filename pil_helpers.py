import os
from typing import Tuple, Union, List

from PIL import ImageFont, ImageDraw, Image, ImageOps

from enums import HAlign, VAlign

DEBUG_TEXT_BOX_BORDERS = False
FONTS_FOLDER = os.environ["FONTS_FOLDER"]  # Usually found at C:\Users\<user>\AppData\Local\Microsoft\Windows\Fonts\
DEFAULT_FONT = os.path.join(FONTS_FOLDER, "Chalfont_Medium.otf")
TEXT_FONT = os.path.join(FONTS_FOLDER, "Aktiv_Grotesque.otf")


def open_image(filepath: str) -> Image.Image:
    return Image.open(filepath)


def build_font(font_name, font_size) -> ImageFont:
    return ImageFont.truetype(font_name, font_size)


class TextBox:

    def __init__(self, x, y, w, h, halign: HAlign = HAlign.CENTER, valign: VAlign = VAlign.CENTER,
                 font_name: str = DEFAULT_FONT, font_size: int = 50, rotate: int = 0,
                 use_height_for_text_wrap: bool = False, shrink_font_size_to_fit: bool = False):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.halign, self.valign, self.rotate = halign, valign, rotate
        self.use_height_for_text_wrap = use_height_for_text_wrap
        self.shrink_font_to_fit = shrink_font_size_to_fit
        self.font_name, self.font_size = font_name, font_size

    @staticmethod
    def wrap_text(text, font, max_width=0):
        """
        Wraps text properly, so that each line does not exceed a maximum width in pixels. It does this by adding words
        in the string to the line, one by one, until the next word would make the line longer than the maximum width.
        It then starts a new line with that word instead.
        New lines get special treatment. It's kind of funky.
        "Words" are split around spaces.
        """
        text = text.strip("\n")
        if max_width <= 0:
            return text

        temp = ""
        wrapped_text = ""

        for w in text.split(' '):
            # Add words to empty string until the next word would make the line too long
            # If next word contains a newline, check only first word before newline for width match
            if "\n" in w:
                wrapped_text += temp.strip(' ')
                width = font.getlength("{} {}".format(temp, w.partition('\n')[0]))
                # If adding one last word before the line break will exceed max width
                # Add in a line break before last word.
                if width > max_width:
                    wrapped_text += "\n"
                else:
                    wrapped_text += " "
                par = w.rpartition('\n')
                wrapped_text += par[0] + "\n"
                temp = par[2] + " "
            else:
                width = font.getlength(u"{0} {1}".format(temp, w))
                if width > max_width:
                    wrapped_text += temp.strip(' ') + "\n"
                    temp = ""
                temp += w + " "
        return wrapped_text + temp.strip(' ')

    def get_text_block_size(self, text: str, font: ImageFont, width: int, height: int, leading_offset: int = 0
                            ) -> Tuple[List[str], int, int]:
        wrapped_text = self.wrap_text(text, font, height if self.use_height_for_text_wrap else width)
        lines = wrapped_text.split('\n')

        # Set leading
        leading = font.font.ascent + font.font.descent + leading_offset

        # Get max line width
        max_line_width = 0
        for line in lines:
            line_width, line_height = font.getsize(line)
            # Keep track of the longest line width
            max_line_width = max(max_line_width, line_width)

        return lines, max_line_width, len(lines) * leading

    def shrink_font_until_text_fits(self, text: str, font_name: str, starting_font_size: int, width: int, height: int
                                    ) -> Tuple[List[str], ImageFont]:
        font_size = starting_font_size
        while font_size > 0:
            font = build_font(font_name, font_size)
            text_lines, block_width, block_height = self.get_text_block_size(text, font, width, height)
            if block_width <= width and block_height <= height:
                print(font_size)
                return text_lines, font
            font_size -= 1
        else:
            raise ValueError("Text is too big to fit in the text box at any font size")

    def add_text(self, image: Image.Image, text: str, color: Union[str, Tuple[int, int, int]] = "black",
                 leading_offset: int = 0, scale: float=1.0) -> Tuple[int, int]:
        """
        First, attempt to wrap the text if max_width is set, and creates a list of each line. Then paste each
        individual line onto a transparent layer one line at a time, taking into account halign. Then rotate the layer,
        and paste on the image according to the anchor point, halign, and valign.

        @return (int, int): Total width and height of the text block added, in pixels.
        """
        if self.shrink_font_to_fit:
            text_lines, font = self.shrink_font_until_text_fits(
                text,
                self.font_name,
                int(self.font_size * scale),
                int(self.width * scale),
                int(self.height * scale),
            )
        else:
            font = build_font(self.font_name, int(self.font_size * scale))
            max_size = self.height if self.use_height_for_text_wrap else self.width
            wrapped_text = self.wrap_text(
                text,
                font,
                int(max_size * scale)
            )
            text_lines = wrapped_text.split('\n')

        # Initialize layer and draw object
        layer = Image.new('L', (5000, 5000))
        draw = ImageDraw.Draw(layer)
        start_y = 500
        if self.halign == HAlign.LEFT:
            start_x = 500
        elif self.halign == HAlign.CENTER:
            start_x = 2500
        elif self.halign == HAlign.RIGHT:
            start_x = 4500
        else:
            raise ValueError(f"Invalid halign value: {self.halign}")

        # Set leading
        leading = font.font.ascent + font.font.descent + leading_offset

        # Begin laying down the lines, top to bottom
        y = start_y
        max_line_width = 0
        for line in text_lines:
            # If current line is blank, just change y and skip to next
            if not line == "":
                line_width = font.getlength(line)
                if self.halign == HAlign.LEFT:
                    x_pos = start_x
                elif self.halign == HAlign.CENTER:
                    x_pos = start_x - (line_width / 2)
                elif self.halign == HAlign.RIGHT:
                    x_pos = start_x - line_width
                else:
                    raise ValueError(f"Invalid halign value: {self.halign}")
                # Keep track of the longest line width
                max_line_width = max(max_line_width, line_width)
                draw.text((x_pos, y), line, font=font, fill=255)
            y += leading

        total_text_size = (max_line_width, len(text_lines) * leading)

        # Now that the text is added to the image, find the crop points
        top = start_y
        bottom = y - leading_offset
        if self.halign == HAlign.LEFT:
            left = start_x
            right = start_x + max_line_width
        elif self.halign == HAlign.CENTER:
            left = start_x - max_line_width / 2
            right = start_x + max_line_width / 2
        elif self.halign == HAlign.RIGHT:
            left = start_x - max_line_width
            right = start_x
        else:
            raise ValueError(f"Invalid halign value: {self.halign}")
        layer = layer.crop((left, top, right, bottom))
        # Now that the image is cropped down to just the text, rotate
        if self.rotate != 0:
            layer = layer.rotate(self.rotate, expand=True)

        x, y, width, height = int(self.x * scale), int(self.y * scale), int(self.width * scale), int(self.height * scale)
        anchor_x, anchor_y = get_anchors(x, y, width, height, self.halign, self.valign)

        # Determine the anchor point for the new layer
        layer_width, layer_height = layer.size
        if self.halign == HAlign.LEFT:
            coords_x = anchor_x
        elif self.halign == HAlign.CENTER:
            coords_x = anchor_x - layer_width // 2
        elif self.halign == HAlign.RIGHT:
            coords_x = anchor_x - layer_width
        else:
            raise ValueError(f"Invalid halign value: {self.halign}")
        if self.valign == VAlign.TOP:
            coords_y = anchor_y
        elif self.valign == VAlign.CENTER:
            coords_y = anchor_y - layer_height // 2
        elif self.valign == VAlign.BOTTOM:
            coords_y = anchor_y - layer_height
        else:
            raise ValueError(f"Invalid valign value: {self.valign}")

        image.paste(
            ImageOps.colorize(layer, (255, 255, 255), color),
            (coords_x, coords_y),
            layer
        )

        # Add debug box if the flag is set
        if DEBUG_TEXT_BOX_BORDERS:
            draw_box(image, x, y, width, height, anchor_x, anchor_y)

        return total_text_size


def draw_box(image, x: int, y: int, width: int, height: int, anchor_x=None, anchor_y=None, color="red"):
    """
    Useful for figuring out where in the image a text box will land
    """
    draw = ImageDraw.Draw(image)
    draw.rectangle((x, y, x + width, y + height), outline=color)
    # Draw top-left cross
    draw_cross(draw, x, y)
    # Draw center cross
    center_x = x + (width // 2)
    center_y = y + (height // 2)
    draw_cross(draw, center_x, center_y)
    # Draw bottom-right cross
    draw_cross(draw, x + width, y + height)
    # Draw cross at layer anchor point
    if anchor_x is not None and anchor_y is not None:
        draw_cross(draw, anchor_x, anchor_y, color="purple")


def draw_cross(draw: ImageDraw, x: int, y: int, color="green", size=5):
    start = (x, y - size)
    end = (x, y + size)
    draw.line((start, end), color)
    start = (x - size, y)
    end = (x + size, y)
    draw.line((start, end), color)


def get_anchors(x: int, y: int, width: int, height: int, halign: HAlign, valign: VAlign) -> Tuple[int, int]:
    if halign == HAlign.LEFT:
        anchor_x = x
    elif halign == HAlign.CENTER:
        anchor_x = x + width // 2
    elif halign == HAlign.RIGHT:
        anchor_x = x + width
    else:
        raise ValueError(f"Invalid halign value: {halign}")
    if valign == VAlign.TOP:
        anchor_y = y
    elif valign == VAlign.CENTER:
        anchor_y = y + height // 2
    elif valign == VAlign.BOTTOM:
        anchor_y = y + height
    else:
        raise ValueError(f"Invalid valign value: {valign}")
    return anchor_x, anchor_y


def add_class_icon(im: Image, dirname: str):
    path = f"classes/{dirname}/symbol.jpeg"
    if os.path.isfile(path):
        symbol = Image.open(path)
        symbol = symbol.resize((62, 62))
        im.paste(symbol, box=(3, 986))


def save_page(card_list: List[Image], grid: Tuple[int, int], filename, cut_line_width=3,
              page_ratio=8.5 / 11.0, h_margin=100):
    """
    Adds cards, in order, to a grid defined by grid_width, grid_height.
    It then adds a border to the grid, making sure to preserve the
    page ratio for later printing, and saves to filename
    Assumes that all the cards are the same size
    """
    # Create card grid based on size of the first card
    w, h = card_list[0].size
    bg = Image.new(
        "RGB",
        (
            (w + cut_line_width) * grid[0],
            (h + cut_line_width) * grid[1]
        ),
        color="white"
    )
    blank_image = Image.new("RGB", (w, h), color="white")
    # Add cards to the grid, top down, left to right
    for y in range(grid[1]):
        for x in range(grid[0]):
            if not card_list:
                # Card list ran out of images. Use blank images to fill out grid remainder
                card = blank_image
            else:
                card = card_list.pop(0)
            coords = (x * (w + cut_line_width),
                      y * (h + cut_line_width))
            bg.paste(card, coords)
    # If there's a margin defined, add extra whitespace around the page
    # if h_margin > 0:
    #     w,h = bg.size
    #     w_margin = (((h_margin*2)+h)*page_ratio-w)/2.0
    #     w_margin = round(w_margin)
    #     page = Image.new("RGB", (int(w+w_margin*2), int(h+h_margin*2)), (255, 255, 255))
    #     page.paste(bg, (w_margin,h_margin))
    #     page.save(filename)
    # else:
    # bg.save(filename)
    # Create a paper image the exact size of an 8.5x11 paper
    # to paste the card images onto
    paper_width = int(8.5 * 300)  # 8.5 inches times 300 dpi
    paper_height = int(11 * 300)  # 11 inches times 300 dpi
    paper_image = Image.new("RGB", (paper_width, paper_height), (255, 255, 255))
    w, h = bg.size
    # TODO Add code that shrinks the bg if it's bigger than any dimension
    # of the Paper image
    paper_image.paste(bg, ((paper_width - w) // 2, (paper_height - h) // 2))
    paper_image.save(filename, dpi=(300, 300))


action_box = TextBox(0, 50, 67, 500, halign=HAlign.RIGHT, valign=VAlign.TOP, rotate=90,
                     font_name=os.path.join(FONTS_FOLDER, "Astoria_Sans_Extended_Bold.otf"),
                     use_height_for_text_wrap=True)
name_box = TextBox(92, 47, 631, 82, shrink_font_size_to_fit=True)
description_box = TextBox(105, 150, 610, 700,
                          font_size=32, halign=HAlign.LEFT, valign=VAlign.TOP, font_name=TEXT_FONT,
                          shrink_font_size_to_fit=True)
footnote_box = TextBox(105, 860, 610, 50, font_size=32, font_name=TEXT_FONT)
source_box = TextBox(125, 933, 382, 82, font_name=TEXT_FONT, shrink_font_size_to_fit=True)
level_box = TextBox(560, 933, 163, 82)