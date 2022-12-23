from typing import Tuple

from PIL import ImageFont, ImageDraw, Image, ImageOps

from monk_cards.enums import HAlign, VAlign

DEFAULT_FONT = "Chalfont_Medium.otf"


def open_image(filepath: str) -> Image:
    return Image.open(filepath)


def build_font(font_name, font_size):
    return ImageFont.truetype(font_name, font_size)


class TextBox:

    def __init__(self, x, y, w, h, halign: HAlign = HAlign.CENTER, valign: VAlign = VAlign.CENTER,
                 font_name=DEFAULT_FONT, font_size=50, rotate=0):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.halign, self.valign, self.rotate = halign, valign, rotate
        self.font = build_font(font_name, font_size)

    def draw_box(self, image, color="red", x=None, y=None, width=None, height=None):
        """
        Useful for figuring out where in the image a text box will land
        """
        if DEBUG_TEXT_BOX_BORDERS or DEBUG_TEXT_BOX_ANCHORS:
            if x is None:
                x = self.x
            if y is None:
                y = self.y
            if width is None:
                width = self.width
            if height is None:
                height = self.height
            draw = ImageDraw.Draw(image)
            if DEBUG_TEXT_BOX_BORDERS:
                draw.rectangle((x, y, x + width, y + height), outline=color)
            if DEBUG_TEXT_BOX_ANCHORS:
                # Draw top-left cross
                self.draw_cross(draw, x, y)
                # Draw center cross
                center_x = x + (width // 2)
                center_y = y + (height // 2)
                self.draw_cross(draw, center_x, center_y)
                # Draw bottom-right cross
                self.draw_cross(draw, x + width, y + height)

    @staticmethod
    def draw_cross(draw: ImageDraw, x: int, y: int, color="green", size=5):
        start = (x, y - size)
        end = (x, y + size)
        draw.line((start, end), color)
        start = (x - size, y)
        end = (x + size, y)
        draw.line((start, end), color)

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

    def get_text_block_size(self, text, leading_offset=0):
        wrapped_text = self.wrap_text(text, self.font, self.width)
        lines = wrapped_text.split('\n')

        # Set leading
        leading = self.font.font.ascent + self.font.font.descent + leading_offset

        # Get max line width
        max_line_width = 0
        for line in lines:
            line_width, line_height = self.font.getsize(line)
            # Keep track of the longest line width
            max_line_width = max(max_line_width, line_width)

        return max_line_width, len(lines) * leading

    def add_text(self, image, text, color="black", leading_offset=0):
        """
        First, attempt to wrap the text if max_width is set, and creates a list of each line. Then paste each
        individual line onto a transparent layer one line at a time, taking into account halign. Then rotate the layer,
        and paste on the image according to the anchor point, halign, and valign.

        @return (int, int): Total width and height of the text block added, in pixels.
        """
        wrapped_text = self.wrap_text(text, self.font, self.width)
        lines = wrapped_text.split('\n')

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
        leading = self.font.font.ascent + self.font.font.descent + leading_offset

        # Begin laying down the lines, top to bottom
        y = start_y
        max_line_width = 0
        for line in lines:
            # If current line is blank, just change y and skip to next
            if not line == "":
                line_width = self.font.getlength(line)
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
                draw.text((x_pos, y), line, font=self.font, fill=255)
            y += leading

        total_text_size = (max_line_width, len(lines) * leading)

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

        anchor_x, anchor_y = self.get_anchors(self.halign, self.valign)

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

        return total_text_size

    def get_anchors(self, halign: HAlign, valign: VAlign) -> Tuple[int, int]:
        if halign == HAlign.LEFT:
            anchor_x = self.x
        elif halign == HAlign.CENTER:
            anchor_x = self.x + self.width // 2
        elif halign == HAlign.RIGHT:
            anchor_x = self.x + self.width
        else:
            raise ValueError(f"Invalid halign value: {halign}")
        if valign == VAlign.TOP:
            anchor_y = self.y
        elif valign == VAlign.CENTER:
            anchor_y = self.y + self.height // 2
        elif valign == VAlign.BOTTOM:
            anchor_y = self.y + self.height
        else:
            raise ValueError(f"Invalid valign value: {valign}")
        return anchor_x, anchor_y
