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

#pragma once

#include "embree3/rtcore.h"

#include <assert.h>
#include <tuple>
#include <vector>
#include <iostream>

#include "painticle.h"
#include "vec3.h"
#include "mat4.h"
#include "memview.h"

BEGIN_PAINTICLE_NAMESPACE

//! A class, that provides us with the collision detection algorithms
class BVH
{
public:
    //! The user data we pass on to the point query function
    struct PointQueryUserData
    {
        Vec3f p;
        Vec3f barycentrics;
        ID primID;
        const BVH* bvh;
    };

    //! A structure, representing a point on the surface
    /**! Elements are location, normal, tri_index, barycentrics */
    struct SurfaceInfo {
        Vec3f location;
        Vec3f normal;
        ID tri_index;
        Vec3f barycentrics;
    };


    //! Default constructor
    BVH();

    //! Constructor for a mesh 
    BVH(const Vec3f* points, size_t numPoints, const Vec3u* triangles, size_t numTriangles,
        const Vec3f* normals, size_t numNormals);

    //! Destructor
    ~BVH();

    //! Compute the closest point on the mesh for given point p
    /**! @returns location, normal, tri_index, barycentrics */
    SurfaceInfo closestPoint(float x, float y, float z) const;

    //! Compute the closest points on the mesh for a set of given points p
    /**! @param results array of location, normal, tri_index, barycentrics */
    void closestPoints(MemView<Vec3f> points, MemView<SurfaceInfo> results) const;

    //! Shoot a ray and return the intersection
    /**! @returns location, normal, tri_index, barycentrics */
    SurfaceInfo shootRay(const Vec3f& origin, const Vec3f& direction) const;

    //! Shoot a ray and return the intersection
    /**! @param results location, normal, tri_index, barycentrics */
    void shootRays(MemView<Vec3f> origins, MemView<Vec3f> directions, const Mat4f& toObjectTransform,
                   MemView<SurfaceInfo> results) const;

    //! Get the coordinates of a corner of a triangle
    inline Vec3f point(const ID& primId, const ID& corner) const;

    //! Get the coordinates of a corner of a triangle
    inline Vec3f normal(const ID& primId, const ID& corner) const;

private:
    //! The embree device to use
    RTCDevice m_device;

    //! The scene representation
    RTCScene m_scene;

    //! The points buffer, if filled, else nullptr (managed by embree)
    Vec3f* m_points;

    //! The triangles buffer, if filled, else nullptr (managed by embree)
    Vec3u* m_triangles;

    //! The normal indices of the mesh
    std::vector<Vec3f> m_normals;
};


inline Vec3f BVH::point(const ID& primId, const ID& corner) const
{
    assert(m_triangles!=nullptr);
    Vec3u tri = m_triangles[primId];

    assert(m_points!=nullptr);
    return m_points[tri[corner]];
}

inline Vec3f BVH::normal(const ID& primId, const ID& corner) const
{
    assert(corner<3);
    assert(m_normals.size() > primId*3);
    return m_normals[primId*3+corner];
}


END_PAINTICLE_NAMESPACE
