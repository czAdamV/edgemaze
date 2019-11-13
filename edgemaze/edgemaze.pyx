from collections import deque
from operator import add
import numpy


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


# This feels kinda ugly but I couldn't think of a more elegant way to do this.
def neighbours(maze, tile):
    ret = []

    # Can I go to the left?
    if tile[1] > 0 and not maze[tile] & 0b010:
        ret.append(((tile[0], tile[1] - 1), b'>'))

    # Can I go up?
    if tile[0] > 0 and not maze[tile] & 0b100:
        ret.append(((tile[0] - 1, tile[1]), b'v'))

    # Can I go to the right?
    if tile[1] + 1 < maze.shape[1] and not maze[tile[0]][tile[1]+1] & 0b010:
        ret.append(((tile[0] , tile[1] + 1), b'<'))

    # Can I go down?
    if tile[0] + 1 < maze.shape[0] and not maze[tile[0]+1][tile[1]] & 0b100:
        ret.append(((tile[0] + 1, tile[1]), b'^'))

    return ret


def step_flood(maze, distances, directions, queue):
    current = queue.popleft()

    for next, direction in neighbours(maze, current):
        if distances[next] != -1:
            continue

        distances[next] = distances[current] + 1
        directions[next] = direction

        queue.append(next)


def analyze(maze):
    if maze.ndim != 2:
        raise TypeError(f'Maze dimension must be two, {maze.ndim} given.')

    if not numpy.issubdtype(maze.dtype, numpy.integer):
        raise TypeError(f'Maze type must be integral, {maze.dtype} given.')

    distances = numpy.full_like(maze, -1, dtype=numpy.int64)
    directions = numpy.full_like(maze, b' ', dtype=('a', 1))

    flood_queue = deque()

    for target in maze_tarets(maze):
        distances[target] = 0
        directions[target] = b'X'

        flood_queue.append(target)

    while flood_queue:
        step_flood(maze, distances, directions, flood_queue)

    return Solution(distances, directions, numpy.all(distances != -1))