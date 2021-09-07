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
#include "memview.h"
#include "vec3.h"

#include <vector>
#include <utility>

BEGIN_PAINTICLE_NAMESPACE

//! A HashedGrid represents a possibility to perform O(1) spatial queries (also on the GPU)
class HashedGrid
{
public:
    //! Constructor
    HashedGrid(float voxelSize);

    //! Destructor
    ~HashedGrid();

    //! Build the hashed grid from the positions
    void build(MemView<Vec3f> positions);

    //! Clear the hashed grid
    void clear();

    //! Query the voxel size we're using for the coordinate hashing
    inline float voxelSize() const;

    //! Query the voxel size we're using for the coordinate hashing
    void setVoxelSize(float voxelSize);

    //! Query the number of hashed particles
    inline size_t numParticles() const;

    //! Copute the hash value of a position
    inline uint32_t hashCoord(const Vec3f& position) const;

    //! Copute the hash value of a grid position
    inline uint32_t hashGrid(const Vec3i& gridCoord) const;

    //! Compute the grid coordinate for given position
    inline Vec3i gridCoord(const Vec3f& position) const;

    //! Define a relation between e.g. a particle ID to a cell ID
    struct IDRelation {
        ID cellID;
        ID particleID;
    };

    //! Access the sorted particle IDs
    inline const std::vector<IDRelation>& sortedParticleIDs() const;

    //! Access the cell offsets
    inline const std::vector<ID>& cellOffsets() const;

    //! The number of hash entries we manage. This is a trade off between accuracy and memory usage.
    static const uint32_t NUM_HASHED_GRID_ENTRIES = 1000000;
    //static const uint32_t NUM_HASHED_GRID_ENTRIES = 32;

protected:

private:
    //! The particle IDs and cell IDs
    std::vector<IDRelation> m_sortedParticleIDs;

    //! The cell IDs and cell offsets
    std::vector<ID> m_cellOffsets;

    //! The size of a voxel, that gets mapped to the same hash entry
    float m_voxelSize;
};


inline float HashedGrid::voxelSize() const
{ return m_voxelSize; }

inline size_t HashedGrid::numParticles() const
{ return m_sortedParticleIDs.size(); }

inline Vec3i HashedGrid::gridCoord(const Vec3f& position) const
{
    return Vec3i(static_cast<int>(floor(position.x/m_voxelSize)),
                 static_cast<int>(floor(position.y/m_voxelSize)),
                 static_cast<int>(floor(position.z/m_voxelSize)));
}

inline uint32_t HashedGrid::hashCoord(const Vec3f& position) const
{
    return hashGrid(gridCoord(position));
}

inline uint32_t HashedGrid::hashGrid(const Vec3i& gridCoord) const
{
    // Hash function is originally based on this blog post:
    // https://wickedengine.net/2018/05/21/scalabe-gpu-fluid-simulation/
    // However, those original numbers calculate the same hash value for e.g. (-1 -1 1) and (-1 1 -1)
    // Since those are within the search radius for the cell (0 0 0), they needed to be changed.
    // some large primes
    //    const uint32_t p1 = 73856093;
    //    const uint32_t p2 = 19349663;
    //    const uint32_t p3 = 83492791;

    const uint32_t p1 = 917935420;
    const uint32_t p2 = 659095552;
    const uint32_t p3 = 698673843;

    uint32_t n = p1*gridCoord.x ^ p2*gridCoord.y ^ p3*gridCoord.z;
    n %= NUM_HASHED_GRID_ENTRIES;
    return n;
}

inline const std::vector<HashedGrid::IDRelation>& HashedGrid::sortedParticleIDs() const
{ return m_sortedParticleIDs; }

inline const std::vector<ID>& HashedGrid::cellOffsets() const
{ return m_cellOffsets; }

END_PAINTICLE_NAMESPACE
