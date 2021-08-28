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

#define BEGIN_PAINTICLE_NAMESPACE namespace painticle {
#define END_PAINTICLE_NAMESPACE }

BEGIN_PAINTICLE_NAMESPACE

typedef unsigned int ID;
const ID ID_NONE = static_cast<ID>(-1);

typedef unsigned char Byte;

END_PAINTICLE_NAMESPACE
