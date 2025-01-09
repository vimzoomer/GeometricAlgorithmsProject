def generateParallelSegments(maxX, maxY, n):
    delta_x = maxX / (2 * n + 2)
    delta_y = maxY / n
    y = maxY
    x_max = maxX
    x_min = 0
    segments = []

    for _ in range(n):
        y -= delta_y
        x_max -= delta_x
        x_min += delta_x
        segments.append(((x_min, y), (x_max, y)))

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