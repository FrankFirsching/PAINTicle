// This file is part of PAINTicle.
//
// PAINTicle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// PAINTicle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

#include <Python.h>
#include <cstddef>

#include "gpubvh.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include <pybind11/numpy.h>

#include <tbb/parallel_for.h>

using namespace painticle;

namespace {

/** Factory function to create a BVH from numpy arrays specifying the geometry. */
BVH buildBVH_py(pybind11::array_t<float> points, pybind11::array_t<unsigned int> triangles,
                pybind11::array_t<float> normals)
{
    if(points.size() %3 != 0)
        throw std::runtime_error("Points buffer needs 3-dimensional coordinates");
    if(triangles.size() %3 != 0)
        throw std::runtime_error("Triangles buffer needs 3-dimensional indices");
    if(normals.size() %3 != 0)
        throw std::runtime_error("Normals buffer needs 3-dimensional indices");

    pybind11::buffer_info points_buf = points.request();
    pybind11::buffer_info triangles_buf = triangles.request();
    pybind11::buffer_info normals_buf = normals.request();

    return BVH(static_cast<Vec3f*>(points_buf.ptr), points.size()/3,
               static_cast<Vec3u*>(triangles_buf.ptr), triangles.size()/3,
               static_cast<Vec3f*>(normals_buf.ptr), normals.size()/3);
}

/** A parallel numpy supported version of the closest_point function of the BVH. */
pybind11::array_t<BVH::SurfaceInfo> closest_points_bvh(BVH& bvh, pybind11::array_t<float> points)
{
    if(points.size() %3 != 0)
        throw std::runtime_error("Points buffer needs 3-dimensional coordinates");
    size_t numPoints = points.size() / 3;
    pybind11::buffer_info points_buf = points.request();
    size_t stride = points_buf.strides[0];
    const Byte* buffer_ptr = static_cast<const Byte*>(points_buf.ptr);

    pybind11::array_t<BVH::SurfaceInfo> result(numPoints);
    pybind11::buffer_info result_buf = result.request();
    BVH::SurfaceInfo* result_ptr = static_cast<BVH::SurfaceInfo*>(result_buf.ptr);

#ifdef PAINTICLE_RUN_SINGLE_THREADED
    for(size_t i=0; i<numPoints; ++i) {
        const Vec3f& point = *reinterpret_cast<const Vec3f*>(buffer_ptr+i*stride);
        result_ptr[i] = bvh.closestPoint(point.x, point.y, point.z);
    }
#else
    tbb::parallel_for(tbb::blocked_range<size_t>(0,numPoints), [&](tbb::blocked_range<size_t> r) {
        for(size_t i=r.begin(); i<r.end(); ++i) {
            const Vec3f& point = *reinterpret_cast<const Vec3f*>(buffer_ptr+i*stride);
            result_ptr[i] = bvh.closestPoint(point.x, point.y, point.z);
        }
    });
#endif

    return result;
}

}

PYBIND11_NAMESPACE_BEGIN(PYBIND11_NAMESPACE)
PYBIND11_NAMESPACE_BEGIN(detail)

// We cast to Vec3 just as arrays from/to python
template <typename Type> struct type_caster<Vec3<Type>>
 : array_caster<Vec3<Type>, Type, false, 3> { };


PYBIND11_NAMESPACE_END(detail)
PYBIND11_NAMESPACE_END(PYBIND11_NAMESPACE)


PYBIND11_MODULE(bvh, m) {
    namespace py = pybind11;
    m.doc() = "A specific BVH acceleration module for PAINTicle";

    // Numpy support
    PYBIND11_NUMPY_DTYPE(Vec3f, x,y,z);
    PYBIND11_NUMPY_DTYPE(BVH::SurfaceInfo, location, normal, tri_index, barycentrics);

    // Class definitions
    py::class_<BVH::SurfaceInfo>(m, "SurfaceInfo")
        .def_readonly("location", &BVH::SurfaceInfo::location)
        .def_readonly("normal", &BVH::SurfaceInfo::normal)
        .def_readonly("tri_index", &BVH::SurfaceInfo::tri_index)
        .def_readonly("barycentrics", &BVH::SurfaceInfo::barycentrics);


    py::class_<BVH>(m, "BVH")
        .def(py::init<>())
        .def("closest_point", &BVH::closestPoint)
        .def("closest_points", &closest_points_bvh)
        .def("shoot_ray", &BVH::shootRay);

    m.def("build_bvh", &buildBVH_py, "Build the BVH acceleration structure");
}
