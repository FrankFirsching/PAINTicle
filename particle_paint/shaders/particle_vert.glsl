// Particle Paint shader
//
// Project the particle positions into homogeneous clip space

#version 330

in vec2 uv;

void main()
{
  vec2 pos = 2*uv - vec2(1);
  gl_Position = vec4(pos, 0.0f, 1.0f);
}
