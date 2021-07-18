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


#include "gpubvh.h"
#include "hashedgrid.h"
#include "color_conversion.h"
#include "vec3.h"
#include "mat4.h"
#include "particledata.h"
#include "memview.h"
#include "parallel.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/numpy.h"

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

template<class T>
inline MemView<T> toMemView(const pybind11::array_t<T>& data)
{
	pybind11::buffer_info dataBuf = data.request();
	if(dataBuf.ndim != 1) {
		throw std::runtime_error("Error. Number of dimensions must be one.");
	}
	size_t length = dataBuf.shape[0];
    size_t stride = dataBuf.strides[0];
	return MemView<T>(dataBuf.ptr, length, stride);
}

inline MemView<Vec3f> toMemView3D(const pybind11::array_t<float>& data)
{
	pybind11::buffer_info dataBuf = data.request();
	if(dataBuf.ndim != 2) {
		throw std::runtime_error("Error. Number of dimensions must be 2.");
	}
    if(dataBuf.shape[1]!=3) {
        throw std::runtime_error("Error. Need 3-dimensional vector data.");
    }
	size_t length = dataBuf.shape[0];
    size_t stride = dataBuf.strides[0];
	return MemView<Vec3f>(dataBuf.ptr, length, stride);
}

/** A parallel numpy supported version of the closest_point function of the BVH. */
pybind11::array_t<BVH::SurfaceInfo> closest_points_bvh(BVH& bvh, pybind11::array_t<Vec3f> points)
{
    auto points_view = toMemView(points);
    pybind11::array_t<BVH::SurfaceInfo> results(points_view.size());
    auto results_view = toMemView(results);

    bvh.closestPoints(points_view, results_view);
    return results;
}

/** A parallel numpy supported version of the shoot_ray function of the BVH. */
pybind11::array_t<BVH::SurfaceInfo>
shootRays_bvh(BVH& bvh, pybind11::array_t<float> origins, pybind11::array_t<float> directions,
              const Mat4f& toObjectTransform)
{
    auto origins_view = toMemView3D(origins);
    auto directions_view = toMemView3D(directions);
    pybind11::array_t<BVH::SurfaceInfo> results(origins_view.size());
    auto results_view = toMemView(results);

    bvh.shootRays(origins_view, directions_view, toObjectTransform, results_view);
    return results;
}

void build_hashedGrid(HashedGrid& hashedGrid, pybind11::array_t<float> positions)
{
    auto positions_view = toMemView3D(positions);
    hashedGrid.build(positions_view);
}

/** A parallel numpy supported version of the rgb2hsv function. */
pybind11::array_t<Vec3f> rgb2hsv_py(pybind11::array_t<Vec3f> rgb)
{
    auto rgb_view = toMemView(rgb);
    pybind11::array_t<Vec3f> results(rgb_view.size());
    auto results_view = toMemView(results);
    rgb2hsv(rgb_view, results_view);
    return results;
}

/** A parallel numpy supported version of the hsv2rgb function. */
pybind11::array_t<Vec3f> hsv2rgb_py(pybind11::array_t<Vec3f> hsv)
{
    auto hsv_view = toMemView(hsv);
    pybind11::array_t<Vec3f> results(hsv_view.size());
    auto results_view = toMemView(results);
    hsv2rgb(hsv_view, results_view);
    return results;
}

/** A parallel numpy supported version of the hsv2rgb function. */
pybind11::array_t<Vec3f> apply_hsv_offset_py(pybind11::array_t<float> rgb, pybind11::array_t<float> hsv_offsets)
{
    auto rgb_view = toMemView3D(rgb);
    auto hsvOffsets_view = toMemView3D(hsv_offsets);

    pybind11::array_t<Vec3f> results(hsvOffsets_view.size());
    auto results_view = toMemView(results);
    applyHsvOffset(rgb_view, hsvOffsets_view, results_view);

    return results;
}

void add_particles_from_rays(ParticleData& p,
                                pybind11::array_t<float> ray_origins, pybind11::array_t<float> ray_directions,
                                const Mat4f& to_object_transform, const BVH& bvh,
                                const Vec2f& speed_range, const Vec3f& speed_random,
                                const Vec2f& size_range, const Vec2f& mass_range, const Vec2f& age_range,
                                const Vec3f& avg_color, const Vec3f& hsv_color_range)
{
    p.addParticlesFromRays(toMemView3D(ray_origins), toMemView3D(ray_directions), to_object_transform, bvh,
                           speed_range, speed_random, size_range, mass_range, age_range, avg_color, hsv_color_range);
}

template<typename T>
inline
pybind11::array getVector(const std::vector<T>& v)
{
    auto dtype = pybind11::dtype::of<T>();
    auto base = pybind11::array(dtype, {0}, {sizeof(T)});
    return pybind11::array(dtype, {v.size()}, {sizeof(T)}, v.data(), base);
}


template<typename T>
inline
pybind11::array getParticleFieldData(ParticleField<T>& f)
{
    auto dtype = pybind11::dtype::of<T>();
    auto base = pybind11::array(dtype, {0}, {sizeof(T)});
    return pybind11::array(dtype, {f.length()}, {sizeof(T)}, f.data(), base);
}

template<typename T>
inline
void setParticleFieldData(ParticleField<T>& f, pybind11::array_t<T> other)
{
    pybind11::buffer_info info = other.request();
    if(info.itemsize != sizeof(T))
        throw std::runtime_error("Incompatible datatypes.");
    if(info.ndim>1)
        throw std::runtime_error("Invalid shape.");
    if(info.ndim==1 && info.size!=static_cast<pybind11::ssize_t>(f.length()))
        throw std::runtime_error("Invalid number of elements assigned.");
    if(info.ndim==0) {
        f.assignConstant(*static_cast<const T*>(info.ptr));
    } else if(info.strides[0] != info.itemsize) {
        T* field_ptr = f.data();
        const Byte* byte_ptr = static_cast<const Byte*>(info.ptr);
        for(size_t i=0; i<f.length(); ++i) {
            field_ptr[i] = *reinterpret_cast<const T*>(byte_ptr + i*info.strides[0]);
        }
    } else {
        memcpy(f.data(), info.ptr, f.length()*sizeof(T));
    }
}

}

PYBIND11_NAMESPACE_BEGIN(PYBIND11_NAMESPACE)
PYBIND11_NAMESPACE_BEGIN(detail)

// We cast to Vec2 just as arrays from/to python
template <typename Type> struct type_caster<Vec2<Type>>
 : array_caster<Vec2<Type>, Type, false, 2> { };


// We cast to Vec3 just as arrays from/to python
template <typename Type> struct type_caster<Vec3<Type>>
 : array_caster<Vec3<Type>, Type, false, 3> { };


// We cast to Mat4 just as arrays from/to python
template <typename Type> struct type_caster<Mat4<Type>>
 : array_caster<Mat4<Type>, Type, false, 16> { };


PYBIND11_NAMESPACE_END(detail)
PYBIND11_NAMESPACE_END(PYBIND11_NAMESPACE)


PYBIND11_MODULE(accel, m) {
    namespace py = pybind11;
    m.doc() = "A specific acceleration module for PAINTicle";

    // Numpy support
    PYBIND11_NUMPY_DTYPE(HashedGrid::IDRelation, cellID, particleID);
    PYBIND11_NUMPY_DTYPE(Vec2f, x,y);
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
        .def("shoot_ray", &BVH::shootRay)
        .def("shoot_rays", &shootRays_bvh);

    py::class_<HashedGrid>(m, "HashedGrid")
        .def(py::init<float>())
        .def_property_readonly("voxel_size", &HashedGrid::voxelSize)
        .def("hash_coord", &HashedGrid::hashCoord)
        .def("hash_grid", &HashedGrid::hashGrid)
        .def("build", &build_hashedGrid)
        .def_property_readonly("sorted_particle_ids",
                               [](HashedGrid& g) -> py::array
                               { return getVector(g.sortedParticleIDs()); } )
        .def_property_readonly("cell_offsets",
                               [](HashedGrid& g) -> py::array
                               { return getVector(g.cellOffsets()); } );
    m.attr("num_hashed_grid_entries") = py::int_(HashedGrid::NUM_HASHED_GRID_ENTRIES);
    m.attr("id_none") = py::int_(ID_NONE);


    m.def("build_bvh", &buildBVH_py, "Build the BVH acceleration structure");
    m.def("rgb2hsv", &rgb2hsv_py, "Convert a numpy array of colors from rgb to hsv");
    m.def("hsv2rgb", &hsv2rgb_py, "Convert a numpy array of colors from rgb to hsv");
    m.def("apply_hsv_offsets", &apply_hsv_offset_py, "Apply an offset to a color in HSV color space");

// This macro allows numpy access to a particle field. Unfortunately it's not clear how to bass the ParticleData
// object as a base, so it's lifetime is bound to the last accessed field being destroyed. We need to ensure, that
// all field accessors are destroyed when the ParticleData gets destroyed.
#define PARTICLE_DATA_ACCESS(field) \
        .def_property(#field, \
                      [](ParticleData& p) -> py::array \
                      { return getParticleFieldData(p.field); }, \
                      [](ParticleData& p, py::array_t<decltype(ParticleData::field)::ElementType> other) \
                      { setParticleFieldData(p.field, other); })


    py::class_<ParticleData>(m, "ParticleData", py::buffer_protocol())
        .def(py::init<>())
        .def("reserve", &ParticleData::reserve)
        .def("resize", &ParticleData::resize)
        .def("append", &ParticleData::append)
        .def_property_readonly("num_particles", &ParticleData::numParticles)
        .def("del_dead", &ParticleData::delDead)
        .def("add_particles_from_rays", &add_particles_from_rays,
             "Create particles by shooting the rays to given geometry")
        PARTICLE_DATA_ACCESS(location)
        PARTICLE_DATA_ACCESS(acceleration)
        PARTICLE_DATA_ACCESS(speed)
        PARTICLE_DATA_ACCESS(normal)
        PARTICLE_DATA_ACCESS(uv)
        PARTICLE_DATA_ACCESS(size)
        PARTICLE_DATA_ACCESS(mass)
        PARTICLE_DATA_ACCESS(age)
        PARTICLE_DATA_ACCESS(max_age)
        PARTICLE_DATA_ACCESS(color);
}
