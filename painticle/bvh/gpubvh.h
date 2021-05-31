#pragma once

#include "embree3/rtcore.h"

#include <assert.h>
#include <tuple>
#include <vector>
#include <iostream>

#include "painticle.h"
#include "vec3.h"

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
        ID primId;
        const BVH* bvh;
    };

    //! Default constructor
    BVH();

    //! Constructor for a mesh 
    BVH(const Vec3f* points, size_t numPoints, const Vec3u* triangles, size_t numTriangles,
        const Vec3f* normals, size_t numNormals);

    //! Destructor
    ~BVH();

    //! Compute the closes point on the mesh for given point p
    /**! @returns location, normal, tri_index, barycentrics */
    std::tuple<Vec3f, Vec3f, ID, Vec3f> closestPoint(const Vec3f& p) const;

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
