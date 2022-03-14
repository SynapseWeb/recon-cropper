import numpy as np
from skimage import transform as tf


def get_skimage_transform(xcoef=None, ycoef=None, dim=None):
    """ Returns a skimage.transform.
    """
    if not xcoef or not ycoef or dim is None:
        return None
    a = xcoef
    b = ycoef
    # Affine transform
    if dim in range(0, 4):
        if dim == 0:
            tmatrix = np.array(
                [1, 0, 0, 0, 1, 0, 0, 0, 1]
            ).reshape((3, 3))
        elif dim == 1:
            tmatrix = np.array(
                [1, 0, a[0], 0, 1, b[0], 0, 0, 1]
            ).reshape((3, 3))
        elif dim == 2:
            # Special case, swap b[1] and b[2]
            # look at original Reconstruct code: nform.cpp
            tmatrix = np.array(
                [a[1], 0, a[0], 0, b[1], b[0], 0, 0, 1]
            ).reshape((3, 3))
        elif dim == 3:
            tmatrix = np.array(
                [a[1], a[2], a[0], b[1], b[2], b[0], 0, 0, 1]
            ).reshape((3, 3))
        return tf.AffineTransform(np.linalg.inv(tmatrix))
    # Polynomial transform
    elif dim in range(4, 7):
        tmatrix = np.array(
            [a[0], a[1], a[2], a[4], a[3], a[5], b[0], b[1], b[2], b[4], b[3], b[5]]
        ).reshape((2, 6))
        # create matrix of coefficients
        tforward = tf.PolynomialTransform(tmatrix)

        def getrevt(pts):  # pts are a np.array
            newpts = []  # list of final estimates of (x,y)
            for i in range(len(pts)):
                # (u,v) for which we want (x,y)
                u, v = pts[i, 0], pts[i, 1]  # input pts
                # initial guess of (x,y)
                x0, y0 = 0.0, 0.0
                # get forward tform of initial guess
                uv0 = tforward(np.array([x0, y0]).reshape([1, 2]))[0]
                u0 = uv0[0]
                v0 = uv0[1]
                e = 1.0  # reduce error to this limit
                epsilon = 5e-10
                i = 0
                while e > epsilon and i < 100:  # NOTE: 10 -> 100
                    i += 1
                    # compute Jacobian
                    l = a[1] + a[3] * y0 + 2.0 * a[4] * x0
                    m = a[2] + a[3] * x0 + 2.0 * a[5] * y0
                    n = b[1] + b[3] * y0 + 2.0 * b[4] * x0
                    o = b[2] + b[3] * x0 + 2.0 * b[5] * y0
                    p = l * o - m * n  # determinant for inverse
                    if abs(p) > epsilon:
                        # increment x0,y0 by inverse of Jacobian
                        x0 = x0 + ((o * (u - u0) - m * (v - v0)) / p)
                        y0 = y0 + ((l * (v - v0) - n * (u - u0)) / p)
                    else:
                        # try Jacobian transpose instead
                        x0 = x0 + (l * (u - u0) + n * (v - v0))
                        y0 = y0 + (m * (u - u0) + o * (v - v0))
                    # get forward tform of current guess
                    uv0 = tforward(np.array([x0, y0]).reshape([1, 2]))[0]
                    u0 = uv0[0]
                    v0 = uv0[1]
                    # compute closeness to goal
                    e = abs(u - u0) + abs(v - v0)
                # append final estimate of (x,y) to newpts list
                newpts.append((x0, y0))
            newpts = np.asarray(newpts)
            return newpts
        tforward.inverse = getrevt
        return tforward # JF: THIS HAS TO BE EDITED TO RETURN INVERSE TFORM

##def invert_polynomial_transform(tform, w, h):
##    """ Return the inverse of a skimage polynomial transform.
##    """
##    # simulate points to obtain inverse
##    points = []
##    points.append([0,0])
##    points.append([w,0])
##    points.append([0,h])
##    points.append([w,h])
##    points.append([w,h/2])
##    points.append([w/2,h])
##    points = np.array(points)
##    tform_points = tform(points)
##    inv_tform = tf.PolynomialTransform()
##    inv_tform.estimate(tform_points, points)
##    return inv_tform 


class Transform(object):
    """ Class representing a RECONSTRUCT Transform.
    """        

    def __init__(self, **kwargs):
        """ Assign instance attributes to provided args/kwargs.
        """
        # self.dim = kwargs.get("dim")
        self.xcoef = kwargs.get("xcoef")
        self.ycoef = kwargs.get("ycoef")
    
    @property
    def dim(self):
        xcheck = self.xcoef[3:6]
        ycheck = self.ycoef[3:6]
        for elem in xcheck:
            if elem != 0:
                return 6
        for elem in ycheck:
            if elem != 0:
                return 6
        return 3


    @property
    def _tform(self):
        """ Return a skimage transform object.
        """
        return get_skimage_transform(
            xcoef=self.xcoef,
            ycoef=self.ycoef,
            dim=self.dim
        )

    def __eq__(self, other):
        """ Allow use of == operator.
        """
        to_compare = ["dim", "xcoef", "ycoef"]
        for k in to_compare:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __ne__(self, other):
        """ Allow use of != operator.
        """
        return not self.__eq__(other)
    
    def compose(self, other):
        """ Compose two transforms.
        """
        if self.isAffine() and other.isAffine():
            # multiply the two matrices together if both are affine
            combined_tform = self._tform + other._tform
            a = np.linalg.inv(combined_tform.params)
            xcoef = [a[0,2], a[0,0], a[0,1], 0, 0, 0]
            ycoef = [a[1,2], a[1,0], a[1,1], 0, 0, 0]
            return Transform(xcoef=xcoef, ycoef=ycoef)
##        else:
##            # simulate points for non-affine transformations
##            points = []
##            points.append([0,0])
##            points.append([w,0])
##            points.append([0,h])
##            points.append([w,h])
##            points.append([w,h/2])
##            points.append([w/2,h])
##            points = np.array(points)
##            points_self = self._tform(points)
##            points_other = other._tform(points_self)
##            new_tform = tf.PolynomialTransform()
##            new_tform.estimate(points, points_other)
##            inv_new_tform = invert_polynomial_transformation(new_tform)
##            xcoef = list(inv_new_tform.params[0])
##            ycoef = list(inv_new_tform.params[1])
##            return Transform(xcoef=xcoef, ycoef=ycoef, dim=6)

    def invert(self):
        """ Return the inverse of the transform.
        """
        if self.isAffine():
            # return inverted matrix if affine
            a = self._tform.params
            xcoef = [a[0,2], a[0,0], a[0,1], 0, 0, 0]
            ycoef = [a[1,2], a[1,0], a[1,1], 0, 0, 0]
            return Transform(xcoef=xcoef, ycoef=ycoef)
    
    def noTranslation(self):
        if self.isAffine():
            a = self._tform.params
            a[0,2] = 0
            a[1,2] = 0
            a = np.linalg.inv(a)
            xcoef = [a[0,2], a[0,0], a[0,1], 0, 0, 0]
            ycoef = [a[1,2], a[1,0], a[1,1], 0, 0, 0]
            return Transform(xcoef=xcoef, ycoef=ycoef)

    def scaleTranslation(self, factor):
        if self.isAffine():
            tform = self._tform.params
            tform[0,2] *= factor
            tform[1,2] *= factor
            a = np.linalg.inv(tform)
            xcoef = [a[0,2], a[0,0], a[0,1], 0, 0, 0]
            ycoef = [a[1,2], a[1,0], a[1,1], 0, 0, 0]
            return Transform(xcoef=xcoef, ycoef=ycoef)

    def translate(self, x, y, strict=False):
        """ Return the transform translated by x, y.
        If translation is strict, x and y are directly addd to transform.
        If translation is not strict, x and y are transformed and then added.
        """
        if self.isAffine():
            # use matrix if affine
            tform = self._tform.params
            tform[0,2] += x
            tform[1,2] += y
            a = np.linalg.inv(tform)
            xcoef = [a[0,2], a[0,0], a[0,1], 0, 0, 0]
            ycoef = [a[1,2], a[1,0], a[1,1], 0, 0, 0]
            return Transform(xcoef=xcoef, ycoef=ycoef)


##        else:
##            # use polynomial transform if non-affine
##            tform = self._tform.params
##            tform[0,0] += x
##            tform[1,0] += y
##            new_tform = tf.PolynomialTransform(tform)
##            inv_new_tform = invert_polynomial_transformation(new_tform)
##            xcoef = list(inv_new_tform.params[0])
##            ycoef = list(inv_new_tform.params[1])
##            return Transform(xcoef=xcoef, ycoef=ycoef, dim=3)

    def transformPoints(self, points):
        """ Transform a list of points.
        """
        return self._tform(np.array(points))

    def isAffine(self):
        """ Returns True if the transform is affine.
        """
        xcheck = self.xcoef[3:6]
        ycheck = self.ycoef[3:6]
        for elem in xcheck:
            if elem != 0:
                return False
        for elem in ycheck:
            if elem != 0:
                return False
        return True
