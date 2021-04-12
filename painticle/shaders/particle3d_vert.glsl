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


// Project the particle positions into homogeneous clip space

in Particle p;
out Particle p_frag;

uniform float particle_size_age_factor;
uniform mat4 model_view_projection;

void main()
{
    gl_Position = model_view_projection * vec4(p.location, 1);
    gl_Position.z -= 0.001; // Use a small offset to draw points in front of surface
    gl_PointSize = particle_size(p, particle_size_age_factor);
    p_frag = p;
}
