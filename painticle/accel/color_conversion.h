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

#pragma once

#include "vec3.h"
#include "memview.h"

BEGIN_PAINTICLE_NAMESPACE

Vec3f rgb2hsv(const Vec3f& rgb);
void rgb2hsv(MemView<Vec3f> rgb, MemView<Vec3f> results);

Vec3f hsv2rgb(const Vec3f& hsv);
void hsv2rgb(MemView<Vec3f> hsv, MemView<Vec3f> results);

Vec3f applyHsvOffset(const Vec3f& rgb, const Vec3f& hsvOffset);
void applyHsvOffset(MemView<Vec3f> rgb, MemView<Vec3f> hsvOffsets,  MemView<Vec3f> results);

END_PAINTICLE_NAMESPACE
