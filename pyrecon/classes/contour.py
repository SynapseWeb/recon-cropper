import numpy
# from shapely.geometry import LineString, Point, Polygon


class Contour(object):
    """ Class representing a RECONSTRUCT Contour.
    """

    def __init__(self, **kwargs):
        """ Apply given keyword arguments as instance attributes.
        """
        self.name = kwargs.get("name")
        self.comment = kwargs.get("comment")
        self.hidden = kwargs.get("hidden")
        self.closed = kwargs.get("closed")
        self.simplified = kwargs.get("simplified")
        self.mode = kwargs.get("mode")
        self.border = kwargs.get("border")
        self.fill = kwargs.get("fill")
        self.points = list(kwargs.get("points", []))
        # Non-RECONSTRUCT attributes
        self.transform = kwargs.get("transform")

    def __repr__(self):
        """ Return a string representation of this Contour's data.
        """
        return (
            "Contour name={name} hidden={hidden} closed={closed} "
            "simplified={simplified} border={border} fill={fill} "
            "mode={mode}\npoints={points}"
        ).format(
            name=self.name,
            hidden=self.hidden,
            closed=self.closed,
            simplified=self.simplified,
            border=self.border,
            fill=self.fill,
            mode=self.mode,
            points=self.points,
        )

    def __eq__(self, other):
        """ Allow use of == between multiple contours.
        """
        to_compare = [
            "border",
            "closed",
            "fill",
            "mode",
            "name",
            "points",
            "simplified",
            "transform",
        ]
        for k in to_compare:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __ne__(self, other):
        """ Allow use of != between multiple contours.
        """
        return not self.__eq__(other)

    def overlaps(self, other):
        """ Check if contour completely overlaps another in Reconstruct space.
        """
        if len(self.points) != len(other.points):
            return False
        self_tform_points = self.transform.transformPoints(self.points)
        other_tform_points = other.transform.transformPoints(other.points)
        for i in range(len(self_tform_points)):
            if abs(self_tform_points[i] - other_tform_points[i]) > 1e-7:
                return False
        return True