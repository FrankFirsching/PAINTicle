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

#include <array>
#include <cmath>
#include <iostream>

#include "painticle.h"

BEGIN_PAINTICLE_NAMESPACE

//! A simple 3 dimensional vector class
template<class T>
class Vec3
{
public:
    Vec3()
    {}

    Vec3(T x_, T y_, T z_)
    : x(x_), y(y_), z(z_)
    {}

    inline Vec3 operator-(const Vec3& other) const
    { return Vec3(x-other.x, y-other.y, z-other.z); }

    inline T dot(const Vec3& other) const
    { return x*other.x + y*other.y + z*other.z; }

    inline Vec3 operator*(T f) const
    { return Vec3(f*x, f*y, f*z); }

    inline Vec3 operator+(const Vec3& other) const
    { return Vec3(x+other.x, y+other.y, z+other.z); }

    inline void operator+=(const Vec3& other)
    { x+=other.x; y+=other.y; z+=other.z; }

    inline void operator-=(const Vec3& other)
    { x-=other.x; y-=other.y; z-=other.z; }

    inline T distance(const Vec3& other) const
    { return (other-*this).length(); }

    inline T length() const
    { return sqrt(sqrLength()); }

    inline T sqrLength() const
    { return this->dot(*this); }

    inline Vec3<T> projected(const Vec3<T>& onto) const
    {
        return (this->dot(onto) / onto.sqrLength()) * onto;
    }

    inline void normalize()
    {
        T factor = T(1) / this->length();
        x *= factor;
        y *= factor;
        z *= factor;
    }

    inline Vec3<T> normalized() const
    {
        Vec3<T> result = *this;
        result.normalize();
        return result;
    }

    inline T& operator[](std::size_t idx)
    { return (&x)[idx]; }

    inline const T& operator[](std::size_t idx) const
    { return (&x)[idx]; }

    inline std::size_t size() const
    { return 3; }

    typedef const float* const_iterator;

    inline const_iterator begin() const
    { return &x; }

    inline const_iterator end() const
    { return begin()+size(); }

    T x;
    T y;
    T z;
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
typedef Vec3<int> Vec3i;
typedef Vec3<ID> Vec3u;

END_PAINTICLE_NAMESPACE
