#include "gpubvh.h"

#include <cstring>
#include <iostream>
#include <iterator>
#include <limits>

#include "vec3.h"

BEGIN_PAINTICLE_NAMESPACE

namespace {

Vec3f closestPointTriangleBary(Vec3f const& p, Vec3f const& a, Vec3f const& b, Vec3f const& c)
{
    const Vec3f ab = b - a;
    const Vec3f ac = c - a;
    const Vec3f ap = p - a;

    const float d1 = ab.dot(ap);
    const float d2 = ac.dot(ap);
    if (d1 <= 0.f && d2 <= 0.f) return {1,0,0};

    const Vec3f bp = p - b;
    const float d3 = ab.dot(bp);
    const float d4 = ac.dot(bp);
    if (d3 >= 0.f && d4 <= d3) return {0,1,0};

    const Vec3f cp = p - c;
    const float d5 = ab.dot(cp);
    const float d6 = ac.dot(cp);
    if (d6 >= 0.f && d5 <= d6) return {0,0,1};

    const float vc = d1 * d4 - d3 * d2;
    if (vc <= 0.f && d1 >= 0.f && d3 <= 0.f)
    {
        const float v = d1 / (d1 - d3);
        return {1-v, v, 0};
    }

    const float vb = d5 * d2 - d1 * d6;
    if (vb <= 0.f && d2 >= 0.f && d6 <= 0.f)
    {
        const float v = d2 / (d2 - d6);
        return {1-v, 0, v};
    }

    const float va = d3 * d6 - d5 * d4;
    if (va <= 0.f && (d4 - d3) >= 0.f && (d5 - d6) >= 0.f)
    {
        const float v = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        return {0, 1-v, v};
    }

    const float denom = 1.f / (va + vb + vc);
    const float v = vb * denom;
    const float w = vc * denom;
    return {1-v-w, v, w};
}

Vec3f applyBarycentics(const Vec3f& baries, const Vec3f& a, const Vec3f& b, const Vec3f& c)
{
    return baries[0]*a + baries[1]*b + baries[2]*c;
}

bool queryFunc(struct RTCPointQueryFunctionArguments* args)
{
    auto userData = static_cast<BVH::PointQueryUserData*>(args->userPtr);
    assert(args->geomID == 0);
    
    Vec3f p(args->query->x, args->query->y, args->query->z);
    Vec3f a = userData->bvh->point(args->primID, 0);
    Vec3f b = userData->bvh->point(args->primID, 1);
    Vec3f c = userData->bvh->point(args->primID, 2);
    Vec3f closestBarycentics = closestPointTriangleBary(p, a, b, c);
    Vec3f closest = applyBarycentics(closestBarycentics, a, b, c);
    float d = closest.distance(p);

    if (d < args->query->radius)
    {
        args->query->radius = d;
        userData->p = closest;
        userData->barycentrics = closestBarycentics;
        userData->primID = args->primID;
        return true; // Return true to indicate that the query radius changed.
    }
    return false;
}

}


BVH::BVH()
{
    m_device = rtcNewDevice("");
    m_scene = rtcNewScene(m_device);
}


template <class T, std::size_t N>
std::ostream& operator<<(std::ostream& o, const std::array<T, N>& arr)
{
    std::copy(arr.cbegin(), arr.cend(), std::ostream_iterator<T>(o, " "));
    return o;
}

BVH::BVH(const Vec3f* points, size_t numPoints, const Vec3u* triangles, size_t numTriangles,
         const Vec3f* normals, size_t numNormals)
    : m_normals(numNormals)
{
    assert(normals!=nullptr || numNormals==0);
    assert(numNormals==3*numTriangles || numNormals==0);
    
    m_device = rtcNewDevice("");
    m_scene = rtcNewScene(m_device);

    RTCGeometry mesh = rtcNewGeometry(m_device, RTC_GEOMETRY_TYPE_TRIANGLE);
    m_points = static_cast<Vec3f*>(rtcSetNewGeometryBuffer(mesh, RTC_BUFFER_TYPE_VERTEX, 0,
                                                           RTC_FORMAT_FLOAT3, sizeof(Vec3f), numPoints));
    memcpy(m_points, points, numPoints*sizeof(Vec3f));

    m_triangles = static_cast<Vec3u*>(rtcSetNewGeometryBuffer(mesh, RTC_BUFFER_TYPE_INDEX, 0,
                                                              RTC_FORMAT_UINT3, sizeof(Vec3u), numTriangles));
    memcpy(m_triangles, triangles, numTriangles*sizeof(Vec3u));

    if(normals!=nullptr) {
        m_normals.assign(normals, normals+numNormals);
    }

    rtcCommitGeometry(mesh);
    rtcAttachGeometryByID(m_scene, mesh, 0);
    rtcReleaseGeometry(mesh);

    rtcCommitScene(m_scene);
}

BVH::~BVH()
{
    rtcReleaseDevice(m_device);
}

BVH::SurfaceInfo BVH::closestPoint(const Vec3f& p) const
{
    RTCPointQuery query;
    query.x = p[0];
    query.y = p[1];
    query.z = p[2];
    query.time = 0;
    query.radius = 10;

    RTCPointQueryContext context;
    rtcInitPointQueryContext(&context);
    PointQueryUserData userData;
    userData.p = {0,0,0};
    userData.barycentrics = {0,0,0};
    userData.primID = ID_NONE;
    userData.bvh = this;
    rtcPointQuery(m_scene, &query, &context, &queryFunc, &userData);

    Vec3f n(0,0,0);
    if(userData.primID!=ID_NONE && !m_normals.empty()) {
        Vec3f n0 = normal(userData.primID, 0);
        Vec3f n1 = normal(userData.primID, 1);
        Vec3f n2 = normal(userData.primID, 2);
        n = applyBarycentics(userData.barycentrics, n0, n1, n2);
    }
    return std::make_tuple(userData.p, n, userData.primID, userData.barycentrics);
}


BVH::SurfaceInfo BVH::shootRay(const Vec3f& origin, const Vec3f& direction) const
{
    RTCIntersectContext context;
    rtcInitIntersectContext(&context);
    RTCRayHit rayHit;
    rayHit.ray.org_x = origin[0];
    rayHit.ray.org_y = origin[1];
    rayHit.ray.org_z = origin[2];
    rayHit.ray.dir_x = direction[0];
    rayHit.ray.dir_y = direction[1];
    rayHit.ray.dir_z = direction[2];
    rayHit.ray.tnear = 0.0f;
    rayHit.ray.tfar = std::numeric_limits<float>::infinity();
    rayHit.ray.time = 0.0f;
    rayHit.ray.id = 0;
    rayHit.ray.mask = static_cast<unsigned int>(-1); // -1 means: don't mask anything, 0 means: mask everything
    rayHit.ray.flags = 0;
    rayHit.hit.primID = RTC_INVALID_GEOMETRY_ID;
    rayHit.hit.geomID = RTC_INVALID_GEOMETRY_ID;
    rtcIntersect1(m_scene, &context, &rayHit);
    Vec3f p(0,0,0);
    Vec3f n(0,0,0);
    ID tri_id = ID_NONE;
    Vec3f barycentrics(0,0,0);
    if(rayHit.hit.geomID!=RTC_INVALID_GEOMETRY_ID) {
        tri_id = rayHit.hit.primID;
        p = origin + rayHit.ray.tfar * direction;
        barycentrics = {1-rayHit.hit.u-rayHit.hit.v, rayHit.hit.u, rayHit.hit.v};
        Vec3f n0 = normal(tri_id, 0);
        Vec3f n1 = normal(tri_id, 1);
        Vec3f n2 = normal(tri_id, 2);
        n = applyBarycentics(barycentrics, n0, n1, n2);
    }
    return std::make_tuple(p, n, tri_id, barycentrics);
}

END_PAINTICLE_NAMESPACE
