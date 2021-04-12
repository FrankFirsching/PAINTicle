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


// Emits a quad for each point to draw the particles

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in Particle p_geo[];
out vec2 center;
out Particle p_frag;

uniform vec2 image_size;
uniform float particle_size_age_factor;

void main()
{
    Particle particle = p_geo[0];
    vec4 pos = gl_in[0].gl_Position;

    p_frag = particle;
    center = particle.uv * image_size;

    float size = particle_size(particle, particle_size_age_factor);
    

    float aspect = image_size[0] / image_size[1];
    float size_x = size * aspect;
    float size_y = size * aspect;

    gl_Position = pos + vec4(-size_x, -size_y, 0, 0);
    EmitVertex();


    gl_Position = pos + vec4(-size_x,  size_y, 0, 0);
    EmitVertex();

    gl_Position = pos + vec4( size_x, -size_y, 0, 0);
    EmitVertex();

    gl_Position = pos + vec4( size_x,  size_y, 0, 0);
    EmitVertex();

    EndPrimitive();
}