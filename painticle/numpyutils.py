# This file is part of PAINTicle.
#
# PAINTicle is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAINTicle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

# <pep8 compliant>

# Utility classes for numpy

import numpy as np
import numpy.lib.recfunctions as recfunctions


def unstructured(a):
    if a.dtype.names is None:
        return a
    else:
        return recfunctions.structured_to_unstructured(a)

def to_structured(a, dtype):
    return recfunctions.unstructured_to_structured(a, dtype=dtype)


class UnstructuredHolder:
    def __init__(self, structured_array):
        for n in structured_array.dtype.names:
            setattr(self, n, unstructured(structured_array[n]))


def repeated_vec(vec, n, dtype=None):
    """ Repeat the given vector n times and return an array """
    result = np.empty(n, dtype=dtype)
    result.fill(vec)
    return result


def vec_length(a):
    """ Calculate the vector length of each entry in the list of 3 or 2-dimensional vectors """
    ua = unstructured(a)
    # einsum approach is fastest.
    # basically it's: np.sqrt(np.sum(ua**2, axis=1))
    return np.sqrt(np.einsum('ij,ij->i', ua, ua))
