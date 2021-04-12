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
uniform float strength;
uniform float time_step;

void main()
{
  // We already did aspect correction in the geometry shader, so we divide by width of image
  vec2 offset = (gl_FragCoord.xy - center)/image_size.xx;
  offset *= 2/p_frag.size;
  frag_color = vec4(p_frag.color, time_step*strength*particle_alpha(p_frag, offset));
  if(frag_color.a<0)
    discard;
}
