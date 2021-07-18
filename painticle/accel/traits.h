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

#include "painticle.h"

#include <type_traits>

BEGIN_PAINTICLE_NAMESPACE

template<typename BASE_T, typename TARGET_T>
struct MatchConst
{
    typedef typename std::conditional<std::is_const<BASE_T>::value, const TARGET_T, TARGET_T>::type type;
};

END_PAINTICLE_NAMESPACE
