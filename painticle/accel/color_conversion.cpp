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

#include "color_conversion.h"
#include "parallel.h"

BEGIN_PAINTICLE_NAMESPACE

Vec3f rgb2hsv(const Vec3f& rgb)
{
    float maxc = std::max(std::max(rgb[0], rgb[1]), rgb[2]);
    float minc = std::min(std::min(rgb[0], rgb[1]), rgb[2]);

    Vec3f hsv(0.0f, 0.0f, maxc);
    
    if(minc == maxc)
        return hsv;
    
    hsv[1] = (maxc-minc) / maxc;
    float rc = (maxc-rgb[0]) / (maxc-minc);
    float gc = (maxc-rgb[1]) / (maxc-minc);
    float bc = (maxc-rgb[2]) / (maxc-minc);
    if(rgb[0] == maxc)
        hsv[0] = bc-gc;
    else if(rgb[1] == maxc)
        hsv[0] = 2.0+rc-bc;
    else
        hsv[0] = 4.0+gc-rc;
    hsv[0] /= 6.0f;
    if(hsv[0] < 0.0f)
        hsv[0] += 1.0f;
    if(hsv[0] > 1.0f)
        hsv[0] -= 1.0f;
    return hsv;
}

void rgb2hsv(MemView<Vec3f> rgb, MemView<Vec3f> results)
{
    BEGIN_PARALLEL_FOR(i, rgb.size()) {
        results[i] = rgb2hsv(rgb[i]);
    } END_PARALLEL_FOR
}

Vec3f hsv2rgb(const Vec3f& hsv)
{
    if(hsv[1] == 0.0f)
        return Vec3f(hsv[2], hsv[2], hsv[2]);
    
    float hh = hsv[0]*6.0f;
    int i = static_cast<int>(hh);
    float f = hh - i;
    float p = hsv[2]*(1.0f - hsv[1]);
    float q = hsv[2]*(1.0f - hsv[1]*f);
    float t = hsv[2]*(1.0f - hsv[1]*(1.0f-f));
    switch(i) {
    case 0:
        return Vec3f(hsv[2], t, p);
    case 1:
        return Vec3f(q, hsv[2], p);
    case 2:
        return Vec3f(p, hsv[2], t);
    case 3:
        return Vec3f(p, q, hsv[2]);
    case 4:
        return Vec3f(t, p, hsv[2]);
    case 5:
        return Vec3f(hsv[2], p, q);
    }
    
    return Vec3f(0.0f, 0.0f, 0.0f);
}

void hsv2rgb(MemView<Vec3f> hsv, MemView<Vec3f> results)
{
    BEGIN_PARALLEL_FOR(i, hsv.size()) {
        results[i] = hsv2rgb(hsv[i]);
    } END_PARALLEL_FOR
}

Vec3f applyHsvOffset(const Vec3f& rgb, const Vec3f& hsvOffset)
{
    // Convert to hsv
    Vec3f result = rgb2hsv(rgb);
    // Apply offset
    result += hsvOffset;
    // clamp to [0:1] range, hue is cyclic
    while(result.x<0.0f) result.x += 1.0f;
    while(result.x>1.0f) result.x -= 1.0f;
    result.y = std::min(1.0f, std::max(0.0f, result.y));
    result.z = std::min(1.0f, std::max(0.0f, result.z));
    // Convert back to rgb
    result = hsv2rgb(result);

    return result;
}

void applyHsvOffset(MemView<Vec3f> rgb, MemView<Vec3f> hsvOffsets,  MemView<Vec3f> results)
{
    if(rgb.size() == 1) {
        if(results.size()!=hsvOffsets.size())
            throw std::runtime_error("If rgb is of length 1, results needs to have same length as hsvOffsets.");
        BEGIN_PARALLEL_FOR(i, results.size()) {
            results[i] = applyHsvOffset(rgb[0], hsvOffsets[i]);
        } END_PARALLEL_FOR
    } else if(hsvOffsets.size() == 1) {
        if(results.size()!=rgb.size())
            throw std::runtime_error("If hsvOffsets is of length 1, results needs to have same length as rgb.");
        BEGIN_PARALLEL_FOR(i, results.size()) {
            results[i] = applyHsvOffset(rgb[i], hsvOffsets[0]);
        } END_PARALLEL_FOR

    } else {
        if(rgb.size()!=results.size())
            throw std::runtime_error("rgb and hsvOffsets need to have same size of be of length 1");        
        BEGIN_PARALLEL_FOR(i, rgb.size()) {
            results[i] = applyHsvOffset(rgb[i], hsvOffsets[i]);
        } END_PARALLEL_FOR
    }
}

END_PAINTICLE_NAMESPACE
