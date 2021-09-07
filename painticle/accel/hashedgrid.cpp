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

#include "hashedgrid.h"
#include "parallel.h"

#include <algorithm>
#include <cassert>

BEGIN_PAINTICLE_NAMESPACE

HashedGrid::HashedGrid(float voxelSize)
: m_cellOffsets(NUM_HASHED_GRID_ENTRIES, ID_NONE),
  m_voxelSize(voxelSize)
{}

HashedGrid::~HashedGrid()
{}

void HashedGrid::build(MemView<Vec3f> positions)
{
    m_sortedParticleIDs.resize(positions.size());

    BEGIN_PARALLEL_FOR(i, positions.size()) {
        IDRelation& sortedEntry = m_sortedParticleIDs[i];
        sortedEntry.particleID = i;
        sortedEntry.cellID = hashCoord(positions[i]);
    } END_PARALLEL_FOR

    std::sort(m_sortedParticleIDs.begin(), m_sortedParticleIDs.end(),
              [](const IDRelation& a, const IDRelation& b) { return a.cellID < b.cellID; });
    size_t lastSortedCell = 0;
    if(m_sortedParticleIDs.size() > 0)
        m_cellOffsets[m_sortedParticleIDs[0].cellID] = 0;
    for(size_t sortedID = 0; sortedID<m_sortedParticleIDs.size(); ++sortedID) {
        while(sortedID < m_sortedParticleIDs.size() && m_sortedParticleIDs[sortedID].cellID == lastSortedCell) {
            sortedID++;
        }
        size_t nextSortedCell = NUM_HASHED_GRID_ENTRIES;
        if(sortedID<m_sortedParticleIDs.size())
            nextSortedCell = m_sortedParticleIDs[sortedID].cellID;
        for(size_t cell = lastSortedCell+1; cell < nextSortedCell; cell++) {
            m_cellOffsets[cell] = ID_NONE;
        }
        if(nextSortedCell < m_cellOffsets.size())
            m_cellOffsets[nextSortedCell] = sortedID;
        lastSortedCell = nextSortedCell;
    }

#ifdef DEBUG_PRINT_HASHED_GRID_CONSTRUCTION
    using namespace std;
    cout << "SortedParticleIDs:" << endl;
    size_t i = 0;
    for(auto x : m_sortedParticleIDs)
        cout << i++ << ": " << x.particleID << ", " << x.cellID << endl;
    cout << "Offsets:" << endl;
    i=0;
    for(auto x : m_cellOffsets)
        cout << i++ << ": " << x << endl;
#endif
}

void HashedGrid::clear()
{
    m_sortedParticleIDs.clear();
}

void HashedGrid::setVoxelSize(float voxelSize)
{ m_voxelSize = voxelSize; }

END_PAINTICLE_NAMESPACE
