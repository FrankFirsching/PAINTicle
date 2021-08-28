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

#include "painticle.h"
#include "traits.h"

#include <vector>

BEGIN_PAINTICLE_NAMESPACE

//! A class, that encapsulates typed access to a numpy one-dimensional arrays
template<typename T>
class MemView
{
public:
    //! Define a const compatible void type
    typedef typename MatchConst<T, void >::type VoidType;

    //! Construct with pointer and length in counted elements and an element stride in bytes
    MemView(VoidType* ptr, size_t length, size_t stride = sizeof(T))
    : m_ptr(static_cast<ByteType*>(ptr)), m_length(length), m_stride(stride)
    {}

    //! Constructor for an STL vector container
    explicit MemView(std::vector<T>& data)
    : m_ptr(reinterpret_cast<Byte*>(&data[0])), m_length(data.size()), m_stride(sizeof(T))
    {}

    //! Get the number of elements managed in this mem view
    inline size_t size() const
    { return m_length; }

    //! Get a pointer to the data
    inline T* data()
    { return static_cast<T*>(m_ptr); }

    //! Get a pointer to the data
    inline const T* data() const
    { return static_cast<T*>(m_ptr); }

    //! Access one element managed by the mem view
    inline T& operator[](size_t i)
    { return *reinterpret_cast<T*>(m_ptr + i*m_stride); }

    //! Access one element managed by the mem view
    inline const T& operator[](size_t i) const
    { return *reinterpret_cast<T*>(m_ptr + i*m_stride); }

private:
    //! Define a const compatible byte type
    typedef typename MatchConst<T, Byte>::type ByteType;

    //! The data pointer
    ByteType* m_ptr;

    //! The length of the data
    size_t m_length;

    //! The byte stride of the individual elements
    size_t m_stride;
};

END_PAINTICLE_NAMESPACE
