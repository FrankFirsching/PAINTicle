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

#include <vector>
#include <string>
#include <cassert>

BEGIN_PAINTICLE_NAMESPACE

//! A containter class for a single field of the particle's data
template<class T>
class ParticleField
{
    // This class works in collaboration with ParticleData
    friend class ParticleData;

public:
    //! The type of a single element of the field
    typedef T ElementType;

    //! Constructor for an empty field container
    ParticleField(const std::string& name);

    //! Get the name of the field
    const std::string name() const
    { return m_name; }

    //! Get the element size in bytes
    size_t elementSize() const
    { return sizeof(ElementType); }
    
    //! Get length of the field's data
    size_t length() const
    { return m_data.size(); }

    //! Append the data of another field
    void append(const ParticleField& other)
    { m_data.insert(m_data.end(), other.m_data.begin(), other.m_data.end()); }

    //! Assign a constant value
    void assignConstant(const ElementType value)
    { m_data.assign(length(), value); }

    //! Access the i-th element
    const T& operator[](size_t i) const
    { return m_data[i]; }

    //! Access the last element
    const T& back() const
    { return m_data.back(); }

    //! Access the data of the field
    const T* data() const
    { return &m_data.front(); }

    //! Access the data of the field
    T* data()
    { return &m_data.front(); }

protected:
    //! Reservea new size for the the field (only allowed through ParticleData to prevent field size divergence)
    void reserve(size_t newSize)
    { m_data.reserve(newSize); }

    //! Resize the field (only allowed through ParticleData to prevent field size divergence)
    void resize(size_t newSize)
    { m_data.resize(newSize); }

    //! Delete the i-th element
    void del(size_t i);

    void push_back(const T& element)
    { m_data.push_back(element); }

    template<typename... Args>
    void emplace_back(Args&&... args)
    { m_data.emplace_back(args...); }

private:
    //! The data of the field
    std::vector<T> m_data;

    //! The name of the field
    std::string m_name;
};


template<class T>
ParticleField<T>::ParticleField(const std::string& name)
: m_name(name)
{}

template<class T>
void ParticleField<T>::del(size_t i)
{
    assert(i<m_data.size());
    m_data[i] = m_data.back(); m_data.resize(m_data.size()-1);
}


END_PAINTICLE_NAMESPACE
