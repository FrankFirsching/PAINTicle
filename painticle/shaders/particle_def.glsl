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

// Definitions shader

#define EMPTY

// When changing the order of the fields or adding/removing fields ensure to also adapt
// particle_painter_gpu accordingly.
// IMPORTANT: Ensure, that GLSL is going to tightly pack those fields in std430 layout.
// Otherwise our python code for filling the buffers would create wrong data, since the padding rules
// would be pretty inefficient to implement in numpy.
#define PARTICLE_FIELDS(x) \
    x vec3 location; \
    x float size; \
    x vec2 uv; \
    x float age; \
    x float max_age; \
    x vec3 color;

#define CONSTRUCT_PARTICLE_ARGS location, size, uv, age, max_age, color

struct Particle
{
    PARTICLE_FIELDS(EMPTY)
};

float particle_alpha(in Particle p, in vec2 offset)
{
    float dist = length(offset);
    float main_alpha = 1-p.age/p.max_age;
    return main_alpha*(1-dist*dist);
}

float particle_size(in Particle p, in float particle_size_age_factor)
{
    float rel_age = p.age / p.max_age;
    return (1-rel_age)*p.size + rel_age*p.size*particle_size_age_factor;
}
