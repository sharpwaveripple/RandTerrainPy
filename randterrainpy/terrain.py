"""This module is for the Terrain class, used for storing randomly generated terrain."""

from exceptions import *


class Terrain(object):
    """Container for a randomly generated area of terrain."""

    def __init__(self, width, length):
        """Initializer for Terrain.

        Args:
            width (int): Width of terrain.
            length (int): Height of terrain.

        """
        self._width = width
        self._length = length
        self._height_map = [[0 for _ in range(self.width)] for _ in range(self.length)]
        """List[list[float]]: Map of heights of all points in terrain grid."""

    @property
    def width(self):
        """int: Width of terrain."""
        return self._width

    @property
    def length(self):
        """int: Height of terrain."""
        return self._length

    def __getitem__(self, item):
        """Get an item at x-y coordinates.

        Indices out of range are taken modulo (length or width).

        Args:
            item (tuple): 2-tuple of x and y coordinates.

        Returns:
            float: Height of terrain at coordinates, between 0 and 1.

        """
        return self._height_map[item[1] % self.length][item[0] % self.width]

    def __setitem__(self, key, value):
        """Set the height of an item.

        Args:
            key (tuple): 2-tuple of x and y coordinates.
            value (float): New height of map at x and y coordinates, between 0 and 1.

        """
        self._height_map[key[1] % self.length][key[0] % self.width] = value

    def __eq__(self, other):
        """Test equality, element by element.

        Returns:
            bool: True if all heights in first are equal to other and same dimensions, False otherwise.

        """
        if not isinstance(other, Terrain):
            return False
        elif not (other.width == self.width and other.length == self.length):
            return False
        else:
            return all(self[x, y] == other[x, y] for x in range(self.width) for y in range(self.length))

    def __add__(self, other):
        """Add two terrains, height by height. Maximum value of element is 1.

        Args:
            other (Terrain): Other terrain to add self to. Must have same dimensions as self.

        Returns:
            Terrain: Terrain of heights of self and other added together.

        Raises:
            InvalidDimensionsError: Other and self have different widths and lengths.

        """
        if other.length != self.length or other.width != self.width:
            raise InvalidDimensionsError()
        result = Terrain(self.width, self.length)
        for i in range(self.width):
            for j in range(self.length):
                result[i, j] = min(self[i, j] + other[i, j], 1)
        return result

    def __sub__(self, other):
        """Subtract two terrains, height by height. Minimum value of element is 0.

        Args:
            other (Terrain): Other terrain to subtract self from. Must have same dimensions as self.

        Returns:
            Terrain: Terrain of heights of self subtracted from other.

        Raises:
            InvalidDimensionsError: Other and self have different widths and lengths.

        """
        if other.length != self.length or other.width != self.width:
            raise InvalidDimensionsError()
        result = Terrain(self.width, self.length)
        for i in range(self.width):
            for j in range(self.length):
                result[i, j] = max(self[i, j] - other[i, j], 0)
        return result

    def __mul__(self, other):
        """Multiply self with scalar; scales all values down by scalar, bounded by 0 and 1.

        Args:
            other (float): Scalar to scale self by.

        Returns:
            Terrain: Terrain of heights of self multiplied by other.

        """
        result = Terrain(self.width, self.length)
        for i in range(self.width):
            for j in range(self.length):
                val = self[i, j] * other
                result[i, j] = val if 0 < val < 1 else round(val)
        return result

    def __str__(self):
        """Return string representation of self.

        Returns:
            str: String of float's, to 1 decimal place, in a 2D grid of heights.

        """
        result = ""
        for x in range(self.length):
            result += "\t".join("{0:.1f}".format(abs(i)) for i in self._height_map[x]) + "\n"
        return result
