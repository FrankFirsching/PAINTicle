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

uniform mat4 model_view_projection;

in vec3 vertex;
in vec2 uv;

out vec2 texture_uv;

void main()
{
  gl_Position = model_view_projection * vec4(vertex, 1.0);
  // Add a little polygon offset, since we draw the overlay directly over the original mesh
  gl_Position.z -= 0.000001;
  texture_uv = uv;
}
