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

// Some useful utility functions used in every shader

vec3 srgb_to_linear(in vec3 c)
{
    bvec3 cutoff = lessThan(c, vec3(0.04045));
    vec3 higher = pow((c + 0.055)/1.055, vec3(2.4));
    vec3 lower = c/12.92;

    return mix(higher, lower, cutoff);
}
