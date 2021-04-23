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


// Draw the internal texture onto the object for preview

in vec2 texture_uv;

out vec4 fragColor;

uniform sampler2D image;

void main()
{
  fragColor = texture(image, texture_uv);
  fragColor.rgb = srgb_to_linear(fragColor.rgb);
  fragColor.a = 0.5;
}
