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

out Particle p_geo;

uniform vec2 image_size;

void main()
{
  p_geo = Particle(CONSTRUCT_PARTICLE_ARGS);
  p_geo.size /= image_size[0];
  vec2 pos = 2*uv - vec2(1);
  gl_Position = vec4(pos, 0.0f, 1.0f);
}
