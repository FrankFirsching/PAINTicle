#include <Python.h>

#include "gpubvh.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include <pybind11/numpy.h>

using namespace painticle;

namespace {

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



    py::class_<BVH>(m, "BVH")
        .def(py::init<>())
        .def("closest_point", &BVH::closestPoint)
        .def("shoot_ray", &BVH::shootRay);

    m.def("build_bvh", &buildBVH_py, "Build the BVH acceleration structure");

}
