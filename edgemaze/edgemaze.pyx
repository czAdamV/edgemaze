# cython: boundscheck=False, wraparound=False
from libcpp.deque cimport deque
from libcpp.pair cimport pair
from operator import add
import numpy
cimport numpy


class PathIterator:
    def __init__(self, directions, start):
        if directions[start] == b' ': 
            raise ValueError(f"No finish point reachable from {start}.")

        self.map = directions
        self.next = start

        self.key = {
            b'>': (0, 1),
            b'v': (1, 0),
            b'<': (0, -1),
            b'^': (-1, 0)
        }


    def __iter__(self):
        return self


    def __next__(self):
        if not self.next:
            raise StopIteration

        ret = self.next

        if self.map[ret] == b'X':
            self.next = None
        else:
            self.next = tuple(map(add, ret, self.key[self.map[ret]]))

        return ret


class Solution:
    def __init__(self, distances, directions, is_reachable):
        self.distances = distances
        self.directions = directions
        self.is_reachable = is_reachable


    def path(self, row, column):
        return PathIterator(self.directions, (row, column))


def maze_tarets(maze):
    return zip(*numpy.where(maze & 0b001))


def analyze(maze):
    cdef int                                    count, x, y
    cdef pair[int, int]                         current
    cdef deque[pair[int, int]]                  flood_queue
    cdef numpy.ndarray[char, ndim=2]            directions
    cdef numpy.ndarray[numpy.int8_t, ndim=2]    maze_int
    cdef numpy.ndarray[numpy.int64_t, ndim=2]   distances
    cdef pair[int[2], char]                     nexts[4]

    if maze.ndim != 2:
        raise TypeError(f'Maze dimension must be two, {maze.ndim} given.')

    if not numpy.issubdtype(maze.dtype, numpy.integer):
        raise TypeError(f'Maze type must be integral, {maze.dtype} given.')

    distances = numpy.full_like(maze, -1, dtype=numpy.int64)
    directions = numpy.full_like(maze, b' ', dtype=('a', 1))
    maze_int = maze.astype(dtype=numpy.int8)

    for target in maze_tarets(maze_int):
        distances[target] = 0
        directions[target] = b'X'

        flood_queue.push_back(target)

    while not flood_queue.empty():
        current = flood_queue.front()
        flood_queue.pop_front()

        count = 0

        x = current.first
        y = current.second

        # Can I go to the left?
        if y > 0 and not maze_int[x, y] & 0b010:
            nexts[count].first[0] = x
            nexts[count].first[1] = y - 1
            nexts[count].second = b'>'
            count += 1

        # Can I go up?
        if x > 0 and not maze_int[x, y] & 0b100:
            nexts[count].first[0] = x  - 1
            nexts[count].first[1] = y
            nexts[count].second = b'v'
            count += 1

        # Can I go to the right?
        if y + 1 < maze_int.shape[1] and not maze_int[x, y+1] & 0b010:
            nexts[count].first[0] = x
            nexts[count].first[1] = y + 1
            nexts[count].second = b'<'
            count += 1

        # Can I go down?
        if x + 1 < maze_int.shape[0] and not maze_int[x+1, y] & 0b100:
            nexts[count].first[0] = x  + 1
            nexts[count].first[1] = y
            nexts[count].second = b'^'
            count += 1

        for i in range(count):
            x = nexts[i].first[0]
            y = nexts[i].first[1]
            if distances[x, y] != -1:
                continue

            distances[x, y] = distances[current.first, current.second] + 1
            directions[x, y] = nexts[i].second

            flood_queue.push_back(pair[int, int](x, y))

    return Solution(distances, directions, numpy.all(distances != -1))