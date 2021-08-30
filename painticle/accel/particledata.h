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

#include "particlefield.h"
#include "vec2.h"
#include "vec3.h"
#include "gpubvh.h"
#include "memview.h"

#include <random>

BEGIN_PAINTICLE_NAMESPACE

//! The container class for all particles
class ParticleData
{
public:
    //! Constructor
    ParticleData();

    //! Destructor
    ~ParticleData();

    //! Set the number of particles
    void resize(size_t numParticles);

    //! Reserve a minimum number of particles
    void reserve(size_t numParticles);

    //! Get the number of particles
    size_t numParticles() const;

    //! Append another set of particles
    void append(const ParticleData& other);

    //! Delete the dead particles
    void delDead();

    //! Create particles from the given rays
    void addParticlesFromRays(MemView<Vec3f> rayOrigins, MemView<Vec3f> rayDirections,
                              const Mat4f& toObjectTransform, const BVH& bvh,
                              const Vec2f& speedRange,  const Vec3f& speedRandom,
                              const Vec2f& sizeRange, const Vec2f& massRange, const Vec2f& ageRange,
                              const Vec3f& avgColor, const Vec3f& hsvColorRange);

    //! The location of the particles
    ParticleField<Vec3f> location;

    //! The accelleration of the particles
    ParticleField<Vec3f> acceleration;

    //! The speed of the particles
    ParticleField<Vec3f> speed;

    //! The normal of the particles
    ParticleField<Vec3f> normal;

    //! The uv of the particles
    ParticleField<Vec2f> uv;

    //! The size of the particles
    ParticleField<float> size;

    //! The mass of the particles
    ParticleField<float> mass;

    //! The age of the particles
    ParticleField<float> age;

    //! The max_age of the particles
    ParticleField<float> max_age;

    //! The color of the particles
    ParticleField<Vec3f> color;

private:
    //! The randon number generator to use when adding particles
    static std::default_random_engine m_generator;
};


END_PAINTICLE_NAMESPACE
