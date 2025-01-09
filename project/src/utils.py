import random

import numpy as np


def generateParallelSegments(maxX, maxY, n):
    delta_y = maxY / n
    y = maxY
    segments = []
    x = np.linspace(0, maxX, 2 * n)
    x = list(map(float, x))

    for _ in range(n):
        x1 = random.choice(x)
        x.remove(x1)
        x2 = random.choice(x)
        x.remove(x2)
        y -= delta_y
        segments.append(((min(x1, x2), y), (max(x1, x2), y)))

    return segments


def calculateDSize(node, count, visited):
    if node is None or node in visited:
        return
    count[0] += 1
    visited.add(node)
    calculateDSize(node.left, count, visited)
    calculateDSize(node.right, count, visited)


def generateUniformPoints(maxX, maxY, n):
    x_coord = np.random.uniform(1, maxX, n)
    y_coord = np.random.uniform(1, maxY, n)

    res = [(x, y) for x, y in zip(x_coord, y_coord)]
    return res