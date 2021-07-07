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

#include "vec3.h"
#include "painticle.h"

BEGIN_PAINTICLE_NAMESPACE

//! A column major matrix class
template<class T>
struct Mat4
{
    Mat4()
    {}

    //! Constructor for an affine matrix with linear 3x3 columns a,b,c and translation t
    Mat4(const Vec3<T>& a, const Vec3<T>& b, const Vec3<T>& c, const Vec3<T>& t)
    : m_data{a[0],a[1],a[2],0, b[0],b[1],b[2],0, c[0],c[1],c[2],0, t[0],t[1],t[2],1 }
    {}

    //! Access an individual element of the matrix
    T operator[](size_t i) const
    { return m_data[i]; }

    //! Access an individual element of the matrix
    T& operator[](size_t i)
    { return m_data[i]; }

    //! Transform given direction vector with matrix
    Vec3<T> multAffineMatDir(const Vec3<T>& v) const;

    //! Transform given point with matrix
    Vec3<T> multAffineMatPoint(const Vec3<T>& p) const;

private:
    //! The 16 numbers, that make up the matrix
    T m_data[16];
};


template<class T>
Vec3<T> Mat4<T>::multAffineMatDir(const Vec3<T>& v) const
{
  return Vec3<T>((*this)[0]*v[0] + (*this)[4] *v[1] + (*this)[8]*v[2],
                 (*this)[1]*v[0] + (*this)[5] *v[1] + (*this)[9]*v[2],
                 (*this)[2]*v[0] + (*this)[6] *v[1] + (*this)[10]*v[2]);
}

template<class T>
Vec3<T> Mat4<T>::multAffineMatPoint(const Vec3<T>& p) const
{
  return Vec3<T>((*this)[0]*p[0] + (*this)[4] *p[1] + (*this)[8]*p[2] +
                 (*this)[12],
                 
                 (*this)[1]*p[0] + (*this)[5] *p[1] + (*this)[9]*p[2] +
                 (*this)[13],
                 
                 (*this)[2]*p[0] + (*this)[6] *p[1] + (*this)[10]*p[2] +
                 (*this)[14]);
}


typedef Mat4<float> Mat4f;

END_PAINTICLE_NAMESPACE
