from __future__ import annotations
from typing import Tuple
from enum import Enum

class Position(Enum):
    BELOW = -1
    ON = 0
    ABOVE = 1

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def to_tuple(self) -> Tuple:
        return self.x, self.y

    def __lt__(self, other: Point) -> bool:
        return self.x < other.x

    def __gt__(self, other: Point) -> bool:
        return self.x > other.x

    def is_left(self, q: Point) -> bool:
        return self < q

    @staticmethod
    def cross_product(p: Point, q: Point, r: Point) -> float:
        return (q.x - p.x) * (r.y - q.y) - (q.y - p.y) * (r.x - q.x)

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y

class Segment:
    eps = 10 ** -16

    def __init__(self, p: Point, q: Point):
        if p.x < q.x:
            self.left = p
            self.right = q
        else:
            self.left = q
            self.right = p

        self.a = (self.left.y - self.right.y) / (self.left.x - self.right.x)
        self.b = self.right.y - self.right.x * self.a

    def __repr__(self) -> str:
        return f"[{self.left}, {self.right}]"

    def position(self, q: Point) -> Position:
        cross_product = Point.cross_product(self.left, self.right, q)
        if cross_product > Segment.eps:
            return Position.ABOVE
        elif cross_product < -Segment.eps:
            return Position.BELOW
        return Position.ON

    def to_tuple(self):
        return (self.left.x, self.left.y), (self.right.x, self.right.y)

    def get_points(self):
        return self.left, self.right

    def get_y_from_x(self, x):
        return self.a * x + self.b

    def __eq__(self, other: Segment) -> bool:
        return self.left == other.left and self.right == other.right

class Trapezoid:
    def __init__(self, left: Point, right: Point, up: Segment, down: Segment):
        self.left = left
        self.right = right
        self.up = up
        self.down = down

        self.top_left = None
        self.bottom_left = None
        self.top_right = None
        self.bottom_right = None

        self.node = None

    def get_neighbours(self):
        return [self.top_left, self.bottom_left, self.top_right, self.bottom_right]

    def __repr__(self) -> str:
        return f"[{self.left}, {self.right}, {self.up}, {self.down}]"

    def get_points(self, as_tuples = False) -> tuple:
        p1 = Point(self.left.x, self.down.get_y_from_x(self.left.x))
        p2 = Point(self.right.x, self.down.get_y_from_x(self.right.x))
        p3 = Point(self.right.x, self.up.get_y_from_x(self.right.x))
        p4 = Point(self.left.x, self.up.get_y_from_x(self.left.x))
        if not as_tuples:
            return p1, p2, p3, p4
        return p1.to_tuple(), p2.to_tuple(), p3.to_tuple(), p4.to_tuple()

    def get_segments(self, as_tuples = False) -> tuple:
        p = self.get_points(as_tuples)
        if not as_tuples:
            return Segment(p[0], p[1]), Segment(p[1], p[2]), Segment(p[2], p[3]), Segment(p[3], p[0])
        return (p[1], p[2]), (p[3], p[0])

    def connect_to_top_left(self, trapezoid: (Trapezoid, None)):
        self.top_left = trapezoid
        if trapezoid is not None:
            trapezoid.top_right = self

    def connect_to_top_right(self, trapezoid: (Trapezoid, None)):
        self.top_right = trapezoid
        if trapezoid is not None:
            trapezoid.top_left = self

    def connect_to_bottom_left(self, trapezoid: (Trapezoid, None)):
        self.bottom_left = trapezoid
        if trapezoid is not None:
            trapezoid.bottom_right = self

    def connect_to_bottom_right(self, trapezoid: (Trapezoid, None)):
        self.bottom_right = trapezoid
        if trapezoid is not None:
            trapezoid.bottom_left = self

    def __eq__(self, other: Trapezoid) -> bool:
        return self.up == other.up and self.down == other.down and self.left == other.left and self.right == other.right

    def __hash__(self):
        return id(self)

class Leaf:
    def __init__(self, trapezoid: Trapezoid):
        if trapezoid is not None:
            self.trapezoid = trapezoid
            self.trapezoid.leaf = self

    def __repr__(self) -> str:
        return f"{self.trapezoid}"

    def __eq__(self, other: Leaf) -> bool:
        return self.trapezoid == other.trapezoid

class Node:
    def __init__(self, node: (XNode, YNode, Leaf)):
        self.node = node

    def is_x_node(self) -> bool:
        return isinstance(self.node, XNode)

    def is_y_node(self) -> bool:
        return isinstance(self.node, YNode)

    def is_leaf(self) -> bool:
        return isinstance(self.node, Leaf)

    def are_same_type(self, second: Node):
        if (self.is_leaf() and second.is_leaf()) or (self.is_y_node() and second.is_y_node()) or (
                self.is_x_node() and second.is_x_node()):
            return True

        return False

    def __eq__(self, other: Node):
        if self.are_same_type(other):
            return self.node == other.node
        return False

class XYNode:
    def __init__(self):
        self.left = None
        self.right = None


class XNode(XYNode):
    def __init__(self, p: Point):
        super().__init__()
        self.p = p

    def __eq__(self, other: XNode):
        return self.p == other.p

class YNode(XYNode):
    def __init__(self, s: Segment):
        super().__init__()
        self.s = s

    def __eq__(self, other: YNode):
        return self.s == other.s

class DTree:
    def __init__(self):
        self.root = None

    def find(self, node: Node, point: Point, a: float = None):
        if node.is_leaf():
            return node
        elif node.is_x_node():
            if node.node.p > point:
                return self.find(node.node.left, point, a)
            else:
                return self.find(node.node.right, point, a)
        else:
            position = node.node.s.position(point)
            if position == Position.ABOVE:
                return self.find(node.node.left, point, a)
            elif position == Position.BELOW:
                return self.find(node.node.right, point, a)
            else:
                if node.node.s.a < a:
                    return self.find(node.node.left, point, a)
                else:
                    return self.find(node.node.right, point, a)

    def find_node(self, target_node: Node):
        trapezoid = target_node.node.trapezoid
        mid_x = (trapezoid.left.x+trapezoid.right.x) / 2
        mid_upper_y = trapezoid.up.a * mid_x + trapezoid.up.b
        mid_lower_y = trapezoid.down.a * mid_x + trapezoid.down.b
        mid_point = Point(mid_x, mid_lower_y + (mid_upper_y - mid_lower_y) / 2)

        node_found = self.find(self.root, mid_point, trapezoid.down.a)

        return node_found

    def update_single(self, trapezoid: Trapezoid, s: Segment, up: Trapezoid, down: Trapezoid, left: (Trapezoid, None), right: (Trapezoid, None)):
        to_swap = self.find_node(trapezoid.node)
        p, q = s.get_points()

        segment_left = Node(XNode(p))
        segment_right = Node(XNode(q))
        segment = Node(YNode(s))


        if left and right:
            if to_swap == self.root:
                self.root.node = segment_left.node
            else:
                to_swap.node = segment_left.node

            segment_left.node.left = left.node
            segment_left.node.right = segment_right

            segment_right.node.left = segment
            segment_right.node.right = right.node

            segment.node.left = up.node
            segment.node.right = down.node

        elif left and not right:
            if to_swap == self.root:
                self.root.node = segment_left.node
            else:
                to_swap.node = segment_left.node

            segment_left.node.left = left.node
            segment_left.node.right = segment

            segment.node.left = up.node
            segment.node.right = down.node

        elif not left and right:
            if to_swap == self.root:
                self.root.node = segment_right.node
            else:
                to_swap.node = segment_right.node

            segment_right.node.left = segment
            segment_right.node.right = right.node

            segment.node.left = up.node
            segment.node.right = down.node
        else:
            if to_swap == self.root:
                self.root.node = segment.node
            else:
                to_swap.node = segment.node

            segment.node.left = up.node
            segment.node.right = down.node


    def update_multiple(self, trapezoids: list[Trapezoid], s: Segment, splitted_trapezoids: dict):
        n = len(trapezoids)

        for i in range(n):
            trapezoid = trapezoids[i]
            to_swap = self.find_node(trapezoid.node)
            segment = Node(YNode(s))

            to_swap.node = segment.node

            segment.node.left = splitted_trapezoids[trapezoids[i]][0].node
            segment.node.right = splitted_trapezoids[trapezoids[i]][1].node