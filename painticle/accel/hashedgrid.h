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

    //! Copute the hash value of a position
    inline uint32_t hashCoord(const Vec3f& position) const;

    //! Copute the hash value of a grid position
    inline uint32_t hashGrid(const Vec3i& gridCoord) const;

    //! The number of hash entries we manage. This is a trade off between accuracy and memory usage.
    static const uint32_t NUM_HASHED_GRID_ENTRIES = 1000000;
    //static const uint32_t NUM_HASHED_GRID_ENTRIES = 32;

protected:

private:
    //! Define a relation between e.g. a particle ID to a cell ID
    struct IDRelation {
        ID particleID;
        ID cellID;
    };

    //! The particle IDs and cell IDs
    std::vector<IDRelation> m_sortedParticleIDs;

    //! The cell IDs and cell offsets
    std::vector<ID> m_cellOffsets;

    //! The size of a voxel, that gets mapped to the same hash entry
    float m_voxelSize;
};

inline uint32_t HashedGrid::hashCoord(const Vec3f& position) const
{
    Vec3i gridCoord(static_cast<int>(floor(position.x/m_voxelSize)),
                    static_cast<int>(floor(position.y/m_voxelSize)),
                    static_cast<int>(floor(position.z/m_voxelSize)));
    return hashGrid(gridCoord);
}

inline uint32_t HashedGrid::hashGrid(const Vec3i& gridCoord) const
{
    // some large primes
    const uint32_t p1 = 73856093;
    const uint32_t p2 = 19349663;
    const uint32_t p3 = 83492791;
    uint32_t n = p1*gridCoord.x ^ p2*gridCoord.y ^ p3*gridCoord.z;
    n %= NUM_HASHED_GRID_ENTRIES;
    return n;
}


END_PAINTICLE_NAMESPACE
