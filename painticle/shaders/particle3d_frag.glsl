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


// Texturize the blown-up particle quad with a soft falloff

in vec2 center;
in Particle p_frag;

out vec4 frag_color;

uniform vec2 image_size;

vec3 srgb_to_linear(in vec3 c)
{
    bvec3 cutoff = lessThan(c, vec3(0.04045));
    vec3 higher = pow((c + 0.055)/1.055, vec3(2.4));
    vec3 lower = c/12.92;

    return mix(higher, lower, cutoff);
}

void main()
{
  vec2 offset = 2*gl_PointCoord.xy - vec2(1);
  // Set the particles's color (drawing to viewport, which is linear color space)
  frag_color = vec4(srgb_to_linear(p_frag.color), particle_alpha(p_frag, offset));
  // Discard everything outside of the circular point shape
  if(frag_color.a<0)
    discard;
}
