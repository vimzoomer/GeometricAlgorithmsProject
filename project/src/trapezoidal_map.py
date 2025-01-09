from .data_structures import *
from .visualizer.main import Visualizer
import random

class TrapezoidalMap:

    def __init__(self, S: list[tuple[tuple[float, float], tuple[float, float]]]):
        #permuted_s = S
        permuted_s = random.sample(S, len(S))
        self.segments = self.__create_segments(permuted_s)
        self.rect_bound = self.__create_rect_bound()
        self.tree = DTree()
        self.tree.root = Node(Leaf(self.rect_bound))

        self.vis = Visualizer()
        self.vis.add_line_segment([self.rect_bound.up.to_tuple(), self.rect_bound.down.to_tuple()], color='red')
        ls = self.vis.add_line_segment(self.rect_bound.get_segments(as_tuples=True))
        self.get_remove_handle = {self.rect_bound : ls}

    def build_trapezoidal_map(self):
        for i in range(len(self.segments)):
            intersected_trapezoids = self.follow_segment(self.segments[i])
            self.update_map(intersected_trapezoids, self.segments[i])

        return self.tree

    def follow_segment(self, s: Segment):
        p, q = s.get_points()
        intersected_trapezoids = []
        first_trapezoid = self.tree.find(self.tree.root, p, s.a).node.trapezoid
        self.vis.show()
        intersected_trapezoids.append(first_trapezoid)

        j = 0
        while intersected_trapezoids[j].right < q:
            if s.position(intersected_trapezoids[j].right) == Position.BELOW:
                intersected_trapezoids.append(intersected_trapezoids[j].top_right)
            else:
                intersected_trapezoids.append(intersected_trapezoids[j].bottom_right)
            j += 1

        return intersected_trapezoids

    @staticmethod
    def get_left_trapezoid(trapezoid, top, bottom, s):
        p, q = s.get_points()
        top_left = trapezoid.top_left
        bottom_left = trapezoid.bottom_left
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down
        left = None

        if trapezoid.left.x < p.x - Segment.eps:
            left = Trapezoid(trapezoid.left, p, upper_segment, lower_segment)
            if top_left is not None:
                left.connect_to_top_left(top_left)
            left.connect_to_bottom_left(bottom_left)
            left.connect_to_top_right(top)
            left.connect_to_bottom_right(bottom)
        else:
            top.connect_to_top_left(top_left)
            bottom.connect_to_bottom_left(bottom_left)

        return left

    @staticmethod
    def get_right_trapezoid(trapezoid, top, bottom, s):
        p, q = s.get_points()
        top_right = trapezoid.top_right
        bottom_right = trapezoid.bottom_right
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down
        right = None

        if trapezoid.right.x > q.x + Segment.eps:
            right = Trapezoid(q, trapezoid.right, upper_segment, lower_segment)
            right.connect_to_top_right(top_right)
            right.connect_to_bottom_right(bottom_right)
            right.connect_to_top_left(top)
            right.connect_to_bottom_left(bottom)
        else:
            top.connect_to_top_right(top_right)
            bottom.connect_to_bottom_right(bottom_right)

        return right

    @staticmethod
    def divide_single_trapezoid(trapezoid: Trapezoid, s: Segment):
        p, q = s.get_points()
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down

        top = Trapezoid(p, q, upper_segment, s)
        bottom = Trapezoid(p, q, s, lower_segment)

        left = TrapezoidalMap.get_left_trapezoid(trapezoid, top, bottom, s)
        right = TrapezoidalMap.get_right_trapezoid(trapezoid, top, bottom, s)

        return top, bottom, left, right

    @staticmethod
    def divide_leftmost_trapezoid(trapezoid: Trapezoid, s:Segment):
        p, _ = s.get_points()
        top_right = trapezoid.top_right
        bottom_right = trapezoid.bottom_right
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down
        right_point = trapezoid.right

        top = Trapezoid(p, right_point, upper_segment, s)
        bottom = Trapezoid(p, right_point, s, lower_segment)

        top.connect_to_top_right(top_right)
        bottom.connect_to_bottom_right(bottom_right)

        left = TrapezoidalMap.get_left_trapezoid(trapezoid, top, bottom, s)

        return top, bottom, left

    @staticmethod
    def connect_or_merge_to_previous_trapezoids(trapezoid, top, bottom, top_prev, bottom_prev, s):
        top_right = trapezoid.top_right
        top_left = trapezoid.top_left
        bottom_left = trapezoid.bottom_left
        bottom_right = trapezoid.bottom_right
        left_point = trapezoid.left
        is_top_merged = False
        is_bottom_merged = False

        if top_prev.up is top.up and top_prev.down is top.down:
            top = Trapezoid(top_prev.left, top.right, top.up, top.down)
            top.connect_to_top_left(top_prev.top_left)
            top.connect_to_bottom_left(top_prev.bottom_left)
            is_top_merged = True
        else:
            top.connect_to_top_left(top_left)
            if s.position(left_point) == Position.ABOVE:
                top.connect_to_bottom_left(top_prev)

        top.connect_to_top_right(top_right)

        if bottom_prev.up is bottom.up and bottom_prev.down is bottom.down:
            bottom = Trapezoid(bottom_prev.left, bottom.right, bottom.up, bottom.down)
            bottom.connect_to_top_left(bottom_prev.top_left)
            bottom.connect_to_bottom_left(bottom_prev.bottom_left)
            is_bottom_merged = True
        else:
            bottom.connect_to_bottom_left(bottom_left)
            if s.position(left_point) == Position.BELOW:
                bottom.connect_to_top_left(bottom_prev)

        bottom.connect_to_bottom_right(bottom_right)

        return top, bottom, is_top_merged, is_bottom_merged

    @staticmethod
    def divide_middle_trapezoid(trapezoid: Trapezoid, s: Segment, top_prev: Trapezoid, bottom_prev: Trapezoid):
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down
        right_point = trapezoid.right
        left_point = trapezoid.left

        top = Trapezoid(left_point, right_point, upper_segment, s)
        bottom = Trapezoid(left_point, right_point, s, lower_segment)

        top, bottom, is_top_merged, is_bottom_merged = TrapezoidalMap.connect_or_merge_to_previous_trapezoids(trapezoid, top, bottom, top_prev, bottom_prev, s)

        return top, bottom, is_top_merged, is_bottom_merged

    @staticmethod
    def divide_rightmost_trapezoid(trapezoid: Trapezoid, s: Segment, top_prev: Trapezoid, bottom_prev: Trapezoid):
        _, q = s.get_points()
        top_right = trapezoid.top_right
        bottom_right = trapezoid.bottom_right
        upper_segment = trapezoid.up
        lower_segment = trapezoid.down
        left_point = trapezoid.left

        top = Trapezoid(left_point, q, upper_segment, s)
        bottom = Trapezoid(left_point, q, s, lower_segment)

        top.top_right = top_right
        bottom.bottom_right = bottom_right

        top, bottom, is_top_merged, is_bottom_merged = TrapezoidalMap.connect_or_merge_to_previous_trapezoids(trapezoid, top, bottom, top_prev, bottom_prev, s)

        right = TrapezoidalMap.get_right_trapezoid(trapezoid, top, bottom, s)

        return top, bottom, right, is_top_merged, is_bottom_merged

    def update_map(self, trapezoids: list[Trapezoid], s: Segment):
        if len(trapezoids) == 1:
            top, bottom, left, right = TrapezoidalMap.divide_single_trapezoid(trapezoids[0], s)
            list_to_visualize = [left, top, bottom, right]
            dict_to_visualize = {}
            for t in list_to_visualize:
                dict_to_visualize[t] = {trapezoids[0]}
            self.update_visualizer([left, top, bottom, right], s, dict_to_visualize)

            trapezoids[0].node = Node(Leaf(trapezoids[0]))
            top.node = Node(Leaf(top))
            bottom.node = Node(Leaf(bottom))
            if left:
                left.node = Node(Leaf(left))
            if right:
                right.node = Node(Leaf(right))
            self.tree.update_single(trapezoids[0], s, top, bottom, left, right)
        else:
            tops = []
            bottoms = []
            from_trapezoid = {}
            splitted_trapezoids = {}

            top_prev, bottom_prev, left = TrapezoidalMap.divide_leftmost_trapezoid(trapezoids[0], s)

            tops.append(top_prev)
            bottoms.append(bottom_prev)

            from_trapezoid[top_prev] = {trapezoids[0]}
            from_trapezoid[bottom_prev] = {trapezoids[0]}
            from_trapezoid[left] = {trapezoids[0]}

            for i in range(1, len(trapezoids) - 1):
                top_prev, bottom_prev, is_top_merged, is_bottom_merged = TrapezoidalMap.divide_middle_trapezoid(trapezoids[i], s, top_prev, bottom_prev)
                from_trapezoid[top_prev] = {trapezoids[i]}
                from_trapezoid[bottom_prev] = {trapezoids[i]}

                if is_top_merged:
                    top_to_remove = tops.pop()
                    top_to_remove_trapezoids = from_trapezoid[top_to_remove]
                    del from_trapezoid[top_to_remove]
                    from_trapezoid[top_prev] |= top_to_remove_trapezoids
                if is_bottom_merged:
                    bottom_to_remove = bottoms.pop()
                    bottom_to_remove_trapezoids = from_trapezoid[bottom_to_remove]
                    del from_trapezoid[bottom_to_remove]
                    from_trapezoid[bottom_prev] |= bottom_to_remove_trapezoids

                tops.append(top_prev)
                bottoms.append(bottom_prev)

            top_prev, bottom_prev, right, is_top_merged, is_bottom_merged = TrapezoidalMap.divide_rightmost_trapezoid(trapezoids[-1], s, top_prev, bottom_prev)

            from_trapezoid[top_prev] = {trapezoids[-1]}
            from_trapezoid[bottom_prev] = {trapezoids[-1]}

            if is_top_merged:
                top_to_remove = tops.pop()
                top_to_remove_trapezoids = from_trapezoid[top_to_remove]
                del from_trapezoid[top_to_remove]
                from_trapezoid[top_prev] |= top_to_remove_trapezoids
            if is_bottom_merged:
                bottom_to_remove = bottoms.pop()
                bottom_to_remove_trapezoids = from_trapezoid[bottom_to_remove]
                del from_trapezoid[bottom_to_remove]
                from_trapezoid[bottom_prev] |= bottom_to_remove_trapezoids

            tops.append(top_prev)
            bottoms.append(bottom_prev)

            for top in tops:
                for trapezoid in from_trapezoid[top]:
                    splitted_trapezoids[trapezoid] = [top]
                    if top.node is None:
                        top.node = Node(Leaf(top))

            for bot in bottoms:
                for trapezoid in from_trapezoid[bot]:
                    splitted_trapezoids[trapezoid].append(bot)
                    if bot.node is None:
                        bot.node = Node(Leaf(bot))

            if left:
                left.node = Node(Leaf(left))
            if right:
                right.node = Node(Leaf(right))

            self.update_visualizer([left] + tops + bottoms + [right], s, from_trapezoid)

            self.tree.update_single(trapezoids[0], s, splitted_trapezoids[trapezoids[0]][0], splitted_trapezoids[trapezoids[0]][1], left, None)
            self.tree.update_multiple(trapezoids[1:-1], s, splitted_trapezoids)
            self.tree.update_single(trapezoids[-1], s, splitted_trapezoids[trapezoids[-1]][0], splitted_trapezoids[trapezoids[-1]][1], None, right)

    @staticmethod
    def __create_segments(permuted_s) -> list[Segment]:
        result = []
        for line in permuted_s:
            start = Point(line[0][0], line[0][1])
            end = Point(line[1][0], line[1][1])
            result.append(Segment(start, end))
        return result

    def __create_rect_bound(self) -> Trapezoid:
        # assuming that segments is list of Segments objects
        min_x = min(self.segments, key=lambda x: x.left.x).left.x
        max_x = max(self.segments, key=lambda x: x.right.x).right.x

        min_y_start = min(self.segments, key=lambda y: y.left.y).left.y
        min_y_end = min(self.segments, key=lambda y: y.right.y).right.y
        max_y_start = max(self.segments, key=lambda y: y.left.y).left.y
        max_y_end = max(self.segments, key=lambda y: y.right.y).right.y

        min_y = min(min_y_start, min_y_end)
        max_y = max(max_y_start, max_y_end)

        topSegment = Segment(Point(min_x, max_y), Point(max_x, max_y))
        bottomSegment = Segment(Point(min_x, min_y), Point(max_x, min_y))

        return Trapezoid(Point(min_x, min_y), Point(max_x, max_y), topSegment, bottomSegment)

    def update_visualizer(self, trapezoids: list[Trapezoid], s: Segment, split_trapezoids: dict[Trapezoid, set[Trapezoid]]):
        self.vis.add_line_segment(s.to_tuple(), color='red')
        for trapezoid in trapezoids:
            if trapezoid in split_trapezoids:
                for trapezoid_to_remove in split_trapezoids[trapezoid]:
                    if trapezoid_to_remove in self.get_remove_handle:
                        to_remove = self.get_remove_handle[trapezoid_to_remove]
                        self.vis.remove_figure(to_remove)
                        del self.get_remove_handle[trapezoid_to_remove]
                    to_remove = []
            if trapezoid is not None:
                ls = self.vis.add_line_segment(trapezoid.get_segments(as_tuples=True))
                self.get_remove_handle[trapezoid] = ls








