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

struct Particle
{
    vec3 location;
    vec2 uv;
    float size;
    float age;
    float max_age;
    vec3 color;
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
