#pragma once

#include <array>
#include <cmath>

#include "painticle.h"

BEGIN_PAINTICLE_NAMESPACE

typedef unsigned int ID;
const ID ID_NONE = static_cast<ID>(-1);

template<class T>
class Vec3 : public std::array<T, 3>
{
    //! Don't repeat the full parent class everytime
    typedef std::array<T, 3> Inherited;

public:
    Vec3()
    {}

    Vec3(T x, T y,T z)
    : Inherited{x,y,z}
    {}

    inline Vec3 operator-(const Vec3& other) const
    { return Vec3(x()-other.x(), y()-other.y(), z()-other.z()); }

    inline T dot(const Vec3& other) const
    { return x()*other.x() + y()*other.y() + z()*other.z(); }

    inline Vec3 operator*(T f) const
    { return Vec3(f*x(), f*y(), f*z()); }

    inline Vec3 operator+(const Vec3& other) const
    { return Vec3(x()+other.x(), y()+other.y(), z()+other.z()); }

    inline T distance(const Vec3& other) const
    { return (other-*this).length(); }

    inline T length() const
    { return sqrt(sqrLength()); }

    inline T sqrLength() const
    { return this->dot(*this); }

    inline T x() const
    { return (*this)[0]; }

    inline T y() const
    { return (*this)[1]; }

    inline T z() const
    { return (*this)[2]; }
};

template<class T>
inline Vec3<T> operator*(T x, const Vec3<T>& v)
{ return v*x; }

template<class T>
inline std::ostream& operator<<(std::ostream& s, const Vec3<T>& v)
{
    s << "[" << v[0] << ", " << v[1] << ", " << v[2] << "]"; 
    return s;
}

typedef Vec3<float> Vec3f;
typedef Vec3<ID> Vec3u;

END_PAINTICLE_NAMESPACE
