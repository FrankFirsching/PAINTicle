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
class Vec2
{
public:
    Vec2()
    {}

    Vec2(T x_, T y_)
    : x(x_), y(y_)
    {}

    inline Vec2 operator-(const Vec2& other) const
    { return Vec2(x-other.x, y-other.y); }

    inline T dot(const Vec2& other) const
    { return x*other.x + y*other.y; }

    inline Vec2 operator*(T f) const
    { return Vec2(f*x, f*y); }

    inline Vec2 operator+(const Vec2& other) const
    { return Vec2(x+other.x, y+other.y); }

    inline void operator+=(const Vec2& other)
    { x+=other.x; y+=other.y; }

    inline T distance(const Vec2& other) const
    { return (other-*this).length(); }

    inline T length() const
    { return sqrt(sqrLength()); }

    inline T sqrLength() const
    { return this->dot(*this); }

    inline void normalize()
    {
        T factor = T(1) / this->length();
        x *= factor;
        y *= factor;
    }

    inline T& operator[](std::size_t idx)
    { return (&x)[idx]; }

    inline const T& operator[](std::size_t idx) const
    { return (&x)[idx]; }

    inline std::size_t size() const
    { return 2; }

    typedef const float* const_iterator;

    inline const_iterator begin() const
    { return &x; }

    inline const_iterator end() const
    { return begin()+size(); }

    T x;
    T y;
};

template<class T>
inline Vec2<T> operator*(T x, const Vec2<T>& v)
{ return v*x; }

template<class T>
inline std::ostream& operator<<(std::ostream& s, const Vec2<T>& v)
{
    s << "[" << v[0] << ", " << v[1] << "]"; 
    return s;
}

typedef Vec2<float> Vec2f;
typedef Vec2<ID> Vec2u;

END_PAINTICLE_NAMESPACE
