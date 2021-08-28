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

#include "particledata.h"
#include "color_conversion.h"

BEGIN_PAINTICLE_NAMESPACE

ParticleData::ParticleData()
: location("location"),
  acceleration("acceleration"),
  speed("speed"),
  normal("normal"),
  uv("uv"),
  size("size"),
  mass("mass"),
  age("age"),
  max_age("max_age"),
  color("color")
{
}

ParticleData::~ParticleData()
{
}


void ParticleData::resize(size_t numParticles)
{
    location.resize(numParticles);
    acceleration.resize(numParticles);
    speed.resize(numParticles);
    normal.resize(numParticles);
    uv.resize(numParticles);
    size.resize(numParticles);
    mass.resize(numParticles);
    age.resize(numParticles);
    max_age.resize(numParticles);
    color.resize(numParticles);
}

void ParticleData::reserve(size_t numParticles)
{
    location.reserve(numParticles);
    acceleration.reserve(numParticles);
    speed.reserve(numParticles);
    normal.reserve(numParticles);
    uv.reserve(numParticles);
    size.reserve(numParticles);
    mass.reserve(numParticles);
    age.reserve(numParticles);
    max_age.reserve(numParticles);
    color.reserve(numParticles);
}

size_t ParticleData::numParticles() const
{
  return location.length();
}

void ParticleData::append(const ParticleData& other)
{
    location.append(other.location);
    acceleration.append(other.acceleration);
    speed.append(other.speed);
    normal.append(other.normal);
    uv.append(other.uv);
    size.append(other.size);
    mass.append(other.mass);
    age.append(other.age);
    max_age.append(other.max_age);
    color.append(other.color);
}

void ParticleData::delDead()
{
    size_t i=0;
    while(i<numParticles()) {
        if(age[i]>=max_age[i]) {
            location.del(i);
            acceleration.del(i);
            speed.del(i);
            normal.del(i);
            uv.del(i);
            size.del(i);
            mass.del(i);
            age.del(i);
            max_age.del(i);
            color.del(i);
        } else {
            // If we delete the i-th element, we need to recheck the i-th entry, so only increment i if we don't delete.
            ++i;
        }
    }
}

void ParticleData::addParticlesFromRays(MemView<Vec3f> rayOrigins, MemView<Vec3f> rayDirections,
                                           const Mat4f& toObjectTransform, const BVH& bvh,
                                           const Vec2f& speedRange, const Vec3f& speedRandom,
                                           const Vec2f& sizeRange, const Vec2f& massRange,
                                           const Vec2f& ageRange, const Vec3f& avgColor, const Vec3f& hsvColorRange)
{
    if(rayDirections.size() != rayDirections.size())
        throw std::runtime_error("rayOrigins and rayDirections need to have same size");
  
    size_t numRays = rayOrigins.size();

    if(numRays == 0)
        return; // Nothing to do

    std::vector<BVH::SurfaceInfo> surface_infos;
    surface_infos.resize(numRays);
    bvh.shootRays(rayOrigins, rayDirections, toObjectTransform, MemView<BVH::SurfaceInfo>(surface_infos));


    std::uniform_real_distribution<float> speedDistribution(speedRange[0], speedRange[1]);
    std::uniform_real_distribution<float> speedXDistribution(-speedRandom[0], speedRandom[0]);
    std::uniform_real_distribution<float> speedYDistribution(-speedRandom[1], speedRandom[1]);
    std::uniform_real_distribution<float> speedZDistribution(-speedRandom[2], speedRandom[2]);
    std::uniform_real_distribution<float> sizeDistribution(sizeRange[0], sizeRange[1]);
    std::uniform_real_distribution<float> massDistribution(massRange[0], massRange[1]);
    std::uniform_real_distribution<float> ageDistribution(ageRange[0], ageRange[1]);
    std::uniform_real_distribution<float> hDistribution(-hsvColorRange[0], hsvColorRange[0]);
    std::uniform_real_distribution<float> sDistribution(-hsvColorRange[1], hsvColorRange[1]);
    std::uniform_real_distribution<float> vDistribution(-hsvColorRange[2], hsvColorRange[2]);
    
    this->reserve(this->numParticles() + numRays);
    
    for(size_t i = 0; i<numRays; ++i) {
        const BVH::SurfaceInfo& surface_info = surface_infos[i];
        if(surface_info.tri_index != ID_NONE) {
            const Vec3f& rayDirection = rayDirections[i];
            location.push_back(surface_info.location);
            acceleration.emplace_back(0,0,0);
            Vec3f particleSpeed = rayDirection.normalized() * speedDistribution(m_generator);
            particleSpeed -= particleSpeed.projected(surface_info.normal);
            Vec3f speedRnd(speedXDistribution(m_generator),
                           speedYDistribution(m_generator),
                           speedZDistribution(m_generator));
            speed.push_back(particleSpeed + speedRnd);
            normal.push_back(surface_info.normal);
            uv.emplace_back(0,0);
            size.emplace_back(sizeDistribution(m_generator));
            mass.emplace_back(massDistribution(m_generator));
            age.emplace_back(0);
            max_age.emplace_back(ageDistribution(m_generator));
            Vec3f hsvOffset(hDistribution(m_generator), sDistribution(m_generator), vDistribution(m_generator));
            Vec3f particleColor = applyHsvOffset(avgColor, hsvOffset);
            color.push_back(particleColor);
        }
    }
}


END_PAINTICLE_NAMESPACE
