"""This module is for the Terrain class, used for storing randomly generated terrain."""

import copy
from exceptions import *
from terraindisplay import *
import random
import math
import os


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
        """Set the height of an item, bounded within 0 and 1.

        Args:
            key (tuple): 2-tuple of x and y coordinates.
            value (float): New height of map at x and y coordinates.

        Raises:
            HeightOutOfBoundsError: Value is not between 0 and 1, when rounded to 3 decimal places.

        """
        if not 0 <= round(value, 3) <= 1:
            raise HeightOutOfBoundsError()
        self._height_map[key[1] % self.length][key[0] % self.width] = round(value, 3)

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
                val = self[i, j] + other[i, j]
                result[i, j] = 1 if val > 1 else val
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
                val = self[i, j] - other[i, j]
                result[i, j] = 0 if val < 0 else val
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
                if not 0 <= val <= 1:
                    raise HeightOutOfBoundsError()
                result[i, j] = val
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

    def display_2d(self):
        """Display a 2D top-down image of terrain as a grid of greyscale squares.

        Each square corresponds to a height value, being on a scale from white if 1 to black if 0.

        """
        Terrain2D.display_terrain(self)

    def display_3d(self):
        """Display a 3D image of terrain as a surface mesh.

        Notes:
            Uses matplotlib internally; is guaranteed to be somewhat slow, so intended for testing only.

        """
        Terrain3D(self).display_terrain()

    def save_terrain(self, path, fname):
        """Save terrain to a location, using .terr extension.

        .terr extension has width and length on first line, space delimited.
        Next lines all contain heights, with each row on a new line, and separate elements in row space delimited.
        Each value is set to 4 decimal points, with no accidental sign from rounding errors.

        Args:
            path (str): Path to folder containing terrain. Must end with slash.
            fname (str): Name of file, minus extension.

        Raises:
            IOError: Cannot get path.

        """
        if not os.path.isdir(path):
            raise IOError()
        else:
            terr_file = open(path + fname + ".terr", mode="w")
            terr_file.write(str(self.width) + " " + str(self.length) + "\n")
            for row in self._height_map:
                terr_file.write(" ".join(str(round(x, 4)) for x in row) + "\n")
            terr_file.close()

    @classmethod
    def load_terrain(cls, path, fname):
        """Load terrain from a .terr file.

        Args:
            path (str): Path to folder containing terrain. Must end with slash.
            fname (str): Name of file, minus extension.

        Returns:
            Terrain: Terrain from .terr file.

        Raises:
            IOError: Cannot get given file from path.
            InvalidFileFormatError: File does not conform to .terr extension format.

        """
        if not os.path.isdir(path + fname + ".terr"):
            raise IOError()
        else:
            terr_file = open(path + fname + ".terr", mode="r")
            terr_file_lines = terr_file.read().split("\n")
            terr_file.close()
            width = int(terr_file_lines[0].split(" ")[0])
            length = int(terr_file_lines[0].split(" ")[1])
            if not len(terr_file_lines) == length + 1:
                raise InvalidFileFormatError()
            heights = [[float(x) for x in terr_file_lines[1:][y].split(" ")] for y in range(length)]
            if not all(len(line) == width for line in heights):
                raise InvalidFileFormatError()
            terr = Terrain(width, length)
            for y in range(length):
                for x in range(width):
                    terr[x, y] = heights[y][x]
            return terr

    def get_vonneumann_neighbours(self, x, y):
        """Get Von Neumann neighbours of point x, y.

        Neighbours are points one above, one below, one to left, and one to right.

        Args:
            x (int): X coordinate of input point.
            x (int): Y coordinate of input point.

        Returns:
            tuple(tuple(int, int) * 4): Coordinates of upper, lower, left and right neighbours in order.

        """
        neighbours = [(x, y+1), (x-1, y), (x+1, y), (x, y-1)]
        filtered_neighbours = [(px, py) for (px, py) in neighbours
                               if 0 <= px < self.width and 0 <= py < self.length]
        return filtered_neighbours

    def get_moore_neighbours(self, x, y):
        """Get Moore neighbours of point x, y.

        Neighbours are nine points directly adjacent to sides and diagonals of given point.

        Args:
            x (int): X coordinate of input point.
            x (int): Y coordinate of input point.

        Returns:
            tuple(tuple(int, int) * 9): upper, up right, right, low right, low, low left, left, up left, in order.

        """
        neighbours = [(x-1, y+1), (x, y+1), (x+1, y+1),
                      (x-1, y), (x+1, y),
                      (x-1, y-1), (x, y-1), (x+1, y-1)]
        filtered_neighbours = [(px, py) for (px, py) in neighbours
                               if 0 <= px < self.width and 0 <= py < self.length]
        return filtered_neighbours

    def thermal_erode(self, iterations=1, talus=0.5):
        """Perform one iteration of thermal erosion upon self.

        Args:
            iterations (int): Number of times to do thermal erosion.
            talus (int): Minimumm height difference that will cause height transfter to a neighbour.

        """
        for _ in range(iterations):
            for x in range(self.width):
                for y in range(self.length):
                    diff_total = 0
                    diff_max = 0
                    # get largest height difference with neighbours and total difference
                    for nx, ny in self.get_vonneumann_neighbours(x, y):
                        difference = self[x, y] - self[nx, ny]
                        if difference > talus:
                            diff_total += difference
                            if difference > diff_max:
                                diff_max = difference
                    # transfer some height of current point to adjacent points <= current height - talus
                    for nx, ny in self.get_vonneumann_neighbours(x, y):
                        difference = self[x, y] - self[nx, ny]
                        if difference > talus:
                            transferred_height = (diff_max - talus)*(difference / float(diff_total))
                            self[x, y] -= transferred_height
                            self[nx, ny] += transferred_height


class VoronoiTerrain(Terrain):
    """A Terrain where a set of regions are defined of positions closest to certain points.

    The diagram takes a preset group of points,
    and makes each position on the grid aware of which point it is closest to.

    """

    def __init__(self, width, length, points):
        """

        Args:
            width (int): Width of terrain.
            length (int): Length of terrain.
            points (list[tuple(int, int)]): List of seed points to define regions in diagram around.

        """
        super(VoronoiTerrain, self).__init__(width, length)
        self._points = points
        """List[tuple(int, int)]: List of all points to define regions around."""
        self._region_map = [[0 for _ in range(self.width)] for _ in range(self.length)]
        """List[list[int]]: 2-dimensional list of indices of which point each position is closest to."""
        self._point_regions = [[] for _ in self._points]
        """List[list[tuple(int, int)]]: Lists of points in each region.
        Point's index in _points coincides with index in _point_regions."""
        self._feature_points = [[] for _ in self._points]
        """List[list[tuple(int, int)]]: Lists of feature points in each region.
        Point's index in _points coincides with index in _point_regions."""
        self._init_regions()

    def _init_regions(self):
        """Initialize region map. and list of regions."""
        self._point_regions = [[] for _ in self._points]    # Reset list of regions
        self._feature_points = [[] for _ in self._points]
        for x in range(self.width):
            for y in range(self.length):
                min_dist = self.width**2 + self.length**2
                closest_pnt_index = 0
                for pnt in self._points:
                    dist_squared = (pnt[0] - x)**2 + (pnt[1] - y)**2
                    if dist_squared < min_dist:
                        min_dist = dist_squared
                        closest_pnt_index = self._points.index(pnt)
                self._region_map[y][x] = closest_pnt_index
                if len(self._point_regions) > 0:
                    self._point_regions[closest_pnt_index] += [(x, y)]

    @property
    def points(self):
        """List[tuple(int, int)]: List of all points to define regions around."""
        return copy.deepcopy(self._points)  # list is mutable, don't allow user to alter it

    def get_closest_point(self, x, y):
        """Get the index of the closest point to a position.

        Args:
            x (int): X coordinate of position.
            y (int): Y coordinate of position.

        Returns:
            tuple(int, int): X-Y coordinates of closest point in Voronoi diagram to position.

        """
        return self._region_map[y][x]

    def add_point(self, x, y):
        """Add a point to make region around.

        Args:
            x (int): X coordinate of point.
            y (int): Y coordinate of point.

        """
        self._points.append((x, y))
        self._init_regions()

    def get_region(self, point_x, point_y):
        """Get all positions within the region defined around a point.

        Args:
            point_x (int): X coordinate of point to get region around.
            point_y (int): Y coordinate of point to get region around.

        Returns:
            list[tuple(int, int)]: List of 2-tuples, representing x-y coordinates of positions in region.

        """
        return self._point_regions[self.points.index((point_x, point_y))]

    def get_region_length(self, region_x, region_y):
        """Get side length of bounding box of region.

        Args:
            region_x (int): X coordinate of center point of region.
            region_y (int): Y coordinate of center point of region.

        Returns:
            int: Number of positions across vertical side of bounding box.

        """
        min_y = min(y for _, y in self.get_region(region_x, region_y))
        max_y = max(y for _, y in self.get_region(region_x, region_y))
        return max_y - min_y + 1

    def get_region_width(self, region_x, region_y):
        """Get side width of bounding box of region.

        Args:
            region_x (int): X coordinate of center point of region.
            region_y (int): Y coordinate of center point of region.

        Returns:
            int: Number of positions across horizontal side of bounding box.

        """
        min_x = min(x for x, _ in self.get_region(region_x, region_y))
        max_x = max(x for x, _ in self.get_region(region_x, region_y))
        return max_x - min_x + 1

    def set_region_height(self, point_x, point_y, height):
        """Set uniform height of all positions within the region defined around a point.

        Args:
            point_x (int): X coordinate of point to set region around.
            point_y (int): Y coordinate of point to set region around.
            height (float): Uniform height to set all points in region to. Between 0 and 1.

        """
        for x, y in self.get_region(point_x, point_y):
            self[x, y] = height

    def set_uniform_random_points(self, num_points):
        """Set region points to be a preset number of new random positions.

        Points are uniformly distributed, but are guaranteed to never be the same.

        Args:
            num_points (int): Number of points to randomly generate. Must be > 0.

        """
        self._points = []
        for pnt_index in range(num_points):
            made_unique_points = False
            while not made_unique_points:
                x, y = random.randint(0, self.width-1), random.randint(0, self.length-1)
                if (x, y) not in self._points:
                    self._points.append((x, y))
                    made_unique_points = True
        self._init_regions()

    def lloyd_relax(self, iters=1):
        """Perform iteration of Lloyd relaxation on center points.

        This involves points being moved to the centroids of their regions,
        making regions more uniformly distributed.

        Args:
            iters (int): Number of iterations of Lloyd relaxation to do in sequence.

        """
        for _ in range(iters):
            for point_index, region_points in enumerate(self._point_regions):
                centroid_x = sum(pnt[0] for pnt in region_points) / len(region_points)
                centroid_y = sum(pnt[1] for pnt in region_points) / len(region_points)
                self._points[point_index] = (centroid_x, centroid_y)
            self._init_regions()

    def get_region_edge(self, region_x, region_y):
        """Get list of all positions on edge of region contained within it.

        Args:
            region_x (int): X ccordinate of center point of region.
            region_y (int): Y coordinate of center point of region.

        Returns:
            list[tuple(int, int)]: List of positions within region on its edge.

        """
        edge = []
        for x, y in self.get_region(region_x, region_y):
            neighbours = [(x-1, y-1), (x-1, y), (x-1, y+1),
                          (x, y-1), (x, y+1),
                          (x+1, y-1), (x+1, y), (x+1, y+1)]
            bounded_neighbours = [(n[0] % self.width, n[1] % self.length) for n in neighbours]
            if not all(self.get_closest_point(*n) == (region_x, region_y) for n in bounded_neighbours):
                edge.append((x, y))
        return edge

    def get_region_corners(self, region_x, region_y):
        """Get list of all positions of corners of region.

        Corner of region is defined as position between 3 or more different regions.

        Args:
            region_x (int): X ccordinate of center point of region.
            region_y (int): Y coordinate of center point of region.

        Returns:
            list[tuple(int, int)]: List of positions within region on its edge.

        """
        corners = []
        for x, y in self.get_region_edge(region_x, region_y):
            neighbours = [(x-1, y-1), (x-1, y), (x-1, y+1),
                          (x, y-1), (x, y+1),
                          (x+1, y-1), (x+1, y), (x+1, y+1)]
            bounded_neighbours = [(n[0] % self.width, n[1] % self.length) for n in neighbours]
            adjacent_regions = []
            for nx, ny in bounded_neighbours:
                if self.get_closest_point(nx, ny) not in adjacent_regions:
                    adjacent_regions.append(self.get_closest_point(nx, ny))
                if len(adjacent_regions) >= 3:
                    corners.append((x, y))
                    break
        return corners

    def get_feature_points(self, x, y):
        """Get feature points within a particular region.

        Args:
            x (int): X coordinate of center point of region.
            y (int): Y coordinate of center point of region.

        Returns:
            list[tuple(int, int)]: List of all x-y coordinates of feature points in region.

        """
        return self._feature_points[self._points.index((x, y))]

    def add_feature_point(self, region_x, region_y, x, y):
        """Add a feature point to a region.

        Args:
            region_x (int): X coordinate of center point of desired region.
            region_y (int): Y coordinate of center point of desired region.
            x (int): X coordinate of feature point.
            y (int): Y coordinate of feature point.

        Raises:
            OutOfRegionError: x and y are outside the chosen region.

        """
        region = self.get_region(region_x, region_y)
        if (x, y) not in region:
            raise OutOfRegionError()
        else:
            self._feature_points[self._points.index((region_x, region_y))] += [(x, y)]

    def remove_feature_point(self, region_x, region_y, x, y):
        """Add a feature point to a region.

        Args:
            region_x (int): X coordinate of center point of desired region.
            region_y (int): Y coordinate of center point of desired region.
            x (int): X coordinate of feature point.
            y (int): Y coordinate of feature point.

        Raises:
            OutOfRegionError: x and y are outside the chosen region.

        """
        region = self.get_region(region_x, region_y)
        if (x, y) not in region:
            raise OutOfRegionError()
        else:
            self._feature_points[self._points.index(region_x, region_y)] += [(x, y)]

    def add_feature_point_factors(self, region_x, region_y, coeffs):
        """Add value to each position in region relative to distance from each feature point times a coefficient.

        Calculation is as follows:

        point_height = c0*d0 + c1*d1 + c2*d2 + ... + cn*dn

        for n feature points in the region. c(n) is the nth coefficient supplied,
        and d(n) is the distance of the nth closest feature point to the supplied point.
        (dn is divided by sqrt(region_length**2 + region_width**2), so is between 0 and 1.)

        Args:
            region_x (int): X coordinate of center point of desired region.
            region_y (int): Y coordinate of center point of desired region.
            coeffs (list[int]): List of all coefficients for distance to each feature point. (0th = closest, etc.)

        References:
            Realtime Procedural Terrain Generation: Jacob Olsen [http://web.mit.edu/cesium/Public/terrain.pdf]

        """
        if len(coeffs) != len(self.get_feature_points(region_x, region_y)):
            raise InvalidCoefficientCountError()
        else:
            for x, y in self.get_region(region_x, region_y):
                feat_points = self.get_feature_points(region_x, region_y)
                sorted_pnts = sorted(feat_points, key=lambda p: (x - p[0])**2 + (y - p[1])**2)
                for (feat_x, feat_y), coeff in zip(sorted_pnts, coeffs):
                    if x != feat_x or y != feat_y:     # distance factor is 0 at feature point, don't bother
                        dist_to_point_squared = (x - feat_x)**2 + (y - feat_y)**2
                        # get distance in same direction to edge of region
                        feat_to_pnt_len = math.sqrt((x - feat_x)**2 + (y - feat_y)**2)
                        x_diff = (x - feat_x) / float(feat_to_pnt_len)
                        y_diff = (y - feat_y) / float(feat_to_pnt_len)
                        temp_x = x
                        temp_y = y
                        # move in same dir as feat pnt => (x, y) until at edge of region / edge of terrain
                        # once there, distance to reached point from feat pnt = dist to edge of region
                        while self._points[self.get_closest_point(int(temp_x), int(temp_y))] == (region_x, region_y):
                            temp_x += x_diff
                            temp_y += y_diff
                            if not ((0 <= temp_x < self.width) and (0 <= temp_y < self.length)):
                                break
                        dist_to_edge_squared = (temp_x + x_diff - feat_x)**2 + (temp_y + y_diff - feat_y)**2
                        # divide distance to point by distance to edge to ensure 0 <= height <= 1
                        dist_factor = math.sqrt(dist_to_point_squared / float(dist_to_edge_squared))
                        self[x, y] += dist_factor * coeff

    def add_random_feature_points(self, region_x, region_y, num_points):
        """Add a set number of randomly placed feature points in a region.

        Args:
            region_x (int): X coordinate of center point of desired region.
            region_y (int): Y coordinate of center point of desired region.
            num_points (int): Number of feature points to create.

        """
        pnts = self.get_region(region_x, region_y)
        chosen_indices = random.sample(range(0, len(pnts)), num_points)
        chosen_feat_points = [pnts[i] for i in chosen_indices]
        for x, y in chosen_feat_points:
            self.add_feature_point(region_x, region_y, x, y)

    def save_terrain(self, path, fname):
        """Save terrain to a location, using .vterr extension.

        .terr extension has width, length, and number of regions on first line, space delimited.
        Next lines all contain heights, with each row on a new line, and separate elements in row space delimited.
        Each value is set to 4 decimal points, with no accidental sign from rounding errors.
        After this, each region center is on a separate line, with x and y coordinates space delimited.
        On each region's line, a series of feature point x-y coordinates for said region are space delimited.

        Args:
            path (str): Path to folder containing terrain. Must end with slash.
            fname (str): Name of file, minus extension.

        Raises:
            IOError: Cannot get path.

        """
        if not os.path.isdir(path):
            raise IOError()
        else:
            terr_file = open(path + fname + ".vterr", mode="w")
            terr_file.write(str(self.width) + " " + str(self.length) + " " + str(len(self._points)) + "\n")
            for row in self._height_map:
                terr_file.write(" ".join(str(round(x, 4)) for x in row) + "\n")
            for x, y in self._points:
                terr_file.write(str(x) + " " + str(y))
                for feat_x, feat_y in self.get_feature_points(x, y):
                    terr_file.write(" " + str(feat_x) + " " + str(feat_y))
                terr_file.write("\n")
            terr_file.close()

    @classmethod
    def load_terrain(cls, path, fname):
        """Load voronoi terrain from a .vterr file.

        Args:
            path (str): Path to folder containing terrain. Must end with slash.
            fname (str): Name of file, minus extension.

        Returns:
            VoronoiTerrain: VoronoiTerrain from .vterr file.

        Raises:
            IOError: Cannot get given file from path.
            InvalidFileFormatError: File does not conform to .terr extension format.

        """
        if not os.path.isdir(path + fname + ".vterr"):
            raise IOError()
        else:
            terr_file = open(path + fname + ".vterr", mode="r")
            terr_file_lines = terr_file.read().split("\n")
            terr_file.close()
            width = int(terr_file_lines[0].split(" ")[0])
            length = int(terr_file_lines[0].split(" ")[1])
            num_regions = int(terr_file_lines[0].split(" ")[2])
            if not len(terr_file_lines) == 1 + length + num_regions:
                raise InvalidFileFormatError()
            heights = [[float(x) for x in terr_file_lines[1:length][y].split(" ")] for y in range(length)]
            if not all(len(line) == width for line in heights):
                raise InvalidFileFormatError()
            region_lines = [line.split(" ") for line in terr_file_lines[length:]]
            points = []
            feat_points = []
            for line in region_lines:
                points.append((int(line[0]), int(line[1])))
                feat_points.append([(int(line[i]), int(line[i+1])) for i in range(2, len(line), 2)])
            terr = VoronoiTerrain(width, length, points)
            for y in range(length):
                for x in range(width):
                    terr[x, y] = heights[y][x]
            for i, (x, y) in enumerate(points):
                for feat_x, feat_y in feat_points[i]:
                    terr.add_feature_point(x, y, feat_x, feat_y)
            return terr
