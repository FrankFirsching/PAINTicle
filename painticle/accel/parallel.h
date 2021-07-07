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

#include <tbb/parallel_for.h>


// #define PAINTICLE_RUN_SINGLE_THREADED

#ifdef PAINTICLE_RUN_SINGLE_THREADED
#define BEGIN_PARALLEL_FOR(variable, length)               \
    for(size_t variable=0; variable<length; ++variable) {

#define END_PARALLEL_FOR }
#else
#define BEGIN_PARALLEL_FOR(variable, length)                                                         \
    tbb::parallel_for(tbb::blocked_range<size_t>(0, length), [&](tbb::blocked_range<size_t> r) { \
        for(size_t variable=r.begin(); variable<r.end(); ++variable) {

#define END_PARALLEL_FOR } } );
#endif
