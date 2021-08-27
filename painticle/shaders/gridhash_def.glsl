
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


// The hashed grid function to get a grid hash from a given position

//! IMPORTANT: This definition in GLSL needs to be compatible with the C++ definition in hashedgrid.h
//             If changes happen here, also perform then in hashedgrid.h!

const uint NUM_HASHED_GRID_ENTRIES = 1000000u;
//const uint NUM_HASHED_GRID_ENTRIES = 32u;

const uint ID_NONE = uint(4294967295);

uint hashGrid(ivec3 gridCoord)
{
    // Hash function is originally based on this blog post:
    // https://wickedengine.net/2018/05/21/scalabe-gpu-fluid-simulation/
    // However, those original numbers calculate the same hash value for e.g. (-1 -1 1) and (-1 1 -1)
    // Since those are within the search radius for the cell (0 0 0), they needed to be changed.

    // some large primes
    //    const uint p1 = 73856093u;
    //    const uint p2 = 19349663u;
    //    const uint p3 = 83492791u;

    const uint p1 = 917935420u;
    const uint p2 = 659095552u;
    const uint p3 = 698673843u;

    uint n = p1*uint(gridCoord.x) ^ p2*uint(gridCoord.y) ^ p3*uint(gridCoord.z);
    n %= NUM_HASHED_GRID_ENTRIES;
    return n;
}

ivec3 gridCoord(vec3 coord, float voxelSize)
{ return ivec3(floor(coord / voxelSize)); }

uint hashCoord(vec3 coord, float voxelSize)
{ return hashGrid(gridCoord(coord, voxelSize)); }

// Define a relation between e.g. a particle ID to a cell ID. Needs to be synchronized to C++ definition
struct IDRelation
{
    uint cellID;
    uint particleID;
};

#define HASHED_GRID_BUFFER(BIND_ID, NAME) \
    layout(std430, binding=BIND_ID) readonly buffer NAME { \
        float NAME##_voxelSize; \
        uint NAME##_numParticles; \
        uint NAME##_cellOffsets[NUM_HASHED_GRID_ENTRIES]; \
        IDRelation NAME##_sortedParticleIDs[]; \
    }
