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

layout (local_size_x = 32, local_size_y = 32) in;

uniform int step;

layout(binding=0, rgba32f) uniform coherent image2D texture;
layout(binding=1, r8ui) uniform coherent uimage2D mask;

void main()
{
    ivec2 pixelPos = ivec2(gl_GlobalInvocationID.xy);    

    uvec4 centerMaskValue = imageLoad(mask, pixelPos);

    float numAccumulated = 0.0;
    vec4 accumulated = vec4(0,0,0,0);
    if(centerMaskValue.r==0) {
        for(int y=-1; y<=1; ++y) {
            for(int x=-1; x<=1; ++x) {
                ivec2 offset = ivec2(x,y);
                ivec2 p = pixelPos + offset;
                uvec4 maskValue = imageLoad(mask, p);
                if(maskValue.r>0 && maskValue.r<step) {
                    float weight = 1.0/length(offset);
                    accumulated += weight * imageLoad(texture, p);
                    numAccumulated += weight;
                }
            }
        }
        accumulated /= numAccumulated;
    }

    barrier();

    if(numAccumulated>0 && centerMaskValue.r==0) {
        imageStore(texture, pixelPos, accumulated);
        imageStore(mask, pixelPos, uvec4(step,1,1,1));
    }
}