from functools import cache
from os import path

from PIL import Image


class MapImageGenerator:
    SEGMENT_WIDTH = 250
    SEGMENT_HEIGHT = 250
    COLUMNS = 6
    ROWS = 5
    SEGMENTS = COLUMNS * ROWS
    WIDTH = SEGMENT_WIDTH * COLUMNS
    HEIGHT = SEGMENT_HEIGHT * ROWS

    def __init__(self) -> None:
        """Initialize the map image"""

        self.segments_path = path.join(path.dirname(__file__), "segments")
        if not path.exists(self.segments_path):
            raise FileNotFoundError("Map segments directory not found")
        self.background_path = path.join(self.segments_path, "background.jpg")

    def get_image(self, segments: list[int]) -> Image:
        """Get the map image"""

        output = self._get_background().copy()

        for segment in segments:
            segment_image = Image.open(self._get_segment_path(segment))
            segment_position = self._get_segment_position(segment)
            output.paste(segment_image, segment_position)

        return output

    @cache
    def _get_background(self) -> Image:
        """Get the background image"""

        return Image.open(self.background_path)

    @cache
    def _get_segment(self, segment: int) -> Image:
        """Get the segment image"""

        return Image.open(self._get_segment_path(segment))

    @cache
    def _get_segment_path(self, segment: int) -> str:
        """Get the path to the segment image"""

        return path.join(self.segments_path, f"{segment}.jpg")

    @cache
    def _get_segment_position(self, segment: int) -> tuple[int, int]:
        """Get the position of the segment on the map image"""

        row, column = divmod(segment - 1, self.COLUMNS)
        return column * self.SEGMENT_WIDTH, row * self.SEGMENT_HEIGHT
