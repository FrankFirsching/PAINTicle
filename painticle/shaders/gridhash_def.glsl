
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

uint hashGrid(ivec3 gridCoord) {
    // some large primes
    const uint p1 = 73856093u;
    const uint p2 = 19349663u;
    const uint p3 = 83492791u;
    uint n = p1*uint(gridCoord.x) ^ p2*uint(gridCoord.y) ^ p3*uint(gridCoord.z);
    n %= NUM_HASHED_GRID_ENTRIES;
    return n;
}


uint hashCoord(vec3 coord, float voxelSize) {
    ivec3 gridCoord = ivec3(floor(coord / voxelSize));
    return hashGrid(gridCoord);
}
