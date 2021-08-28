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


// Gather particles at given location texel_pos and accumulate

#extension GL_ARB_shader_storage_buffer_object : enable

in vec3 texel_pos;

out vec4 frag_color;

uniform vec2 image_size;
uniform float strength;
uniform float time_step;
uniform float particle_size_age_factor;

HASHED_GRID_BUFFER(0, hashedGrid);

layout(std430, binding=1) readonly buffer ParticlesBuffer {
  Particle particles[];
};

void main()
{
  frag_color = vec4(0,0,0,0);
  ivec3 texelCoord = gridCoord(texel_pos, hashedGrid_voxelSize);
  int numFound = 0;
  for(int x=-1; x<=1; ++x) {
    for(int y=-1; y<=1; ++y) {
      for(int z=-1; z<=1; ++z) {
        uint hash = hashGrid(texelCoord+ivec3(x,y,z));
        uint offset = hashedGrid_cellOffsets[hash];
        if(offset==ID_NONE)
          continue;

        while(offset<hashedGrid_numParticles && hashedGrid_sortedParticleIDs[offset].cellID == hash) {
          uint particleID = hashedGrid_sortedParticleIDs[offset].particleID;
          Particle p = particles[particleID];
          float dist = distance(texel_pos, p.location);
          float norm_age = p.age/p.max_age;
          float current_particle_size = p.size*mix(1, particle_size_age_factor, norm_age);
          if(dist<current_particle_size) {
            float norm_dist = 2*dist/current_particle_size;
            float factor = (1-norm_age)*smoothstep(1,0, norm_dist);
            frag_color = (1-factor)*frag_color + factor*vec4(p.color, 1);
            ++numFound;
          }
          ++offset;
        }
      }
    }
  }
  if(numFound==0)
    discard;

  // Default timestep is 1/25th of a second. Normalize the brush strength to that value.
  frag_color *= 25 * time_step * strength;
}
