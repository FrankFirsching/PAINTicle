// Particle Paint shader
//
// Texturize the blown-up particle quad with a soft falloff

#version 330

in vec2 center;

out vec4 fragColor;

uniform vec2 image_size;
uniform float particle_size;
uniform vec3 color;

void main()
{
  // We already did aspect correction in the geometry shader, so we divide by width of image
  vec2 offset = (gl_FragCoord.xy - center)/image_size.xx;
  offset *= 2/particle_size;
  float dist = length(offset);

  vec2 uv = offset*0.5+vec2(0.5);

  fragColor = vec4(color, 1-dist*dist);
}
