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

PARTICLE_FIELDS(in)
out Particle p_frag;

uniform float particle_size_age_factor;
uniform mat4 model_view_projection;
uniform mat4 projection;
uniform float image_height;

void main()
{
    p_frag = Particle(CONSTRUCT_PARTICLE_ARGS);
    gl_Position = model_view_projection * vec4(location, 1);
    // Convert particle world size into a pixel size
    gl_PointSize = 0.5*image_height*projection[1][1]*particle_size(p_frag, particle_size_age_factor) / gl_Position.w;
    // Use a small offset based on the point size to draw points in front of surface
    gl_Position.z -= gl_PointSize * 0.0001;
}
