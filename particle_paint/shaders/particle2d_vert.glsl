// Particle Paint shader
//
// Project the particle positions into homogeneous clip space

in Particle p;
out Particle p_geo;

uniform vec2 image_size;

void main()
{
  p_geo = p;
  p_geo.size /= image_size[0];
  vec2 pos = 2*p.uv - vec2(1);
  gl_Position = vec4(pos, 0.0f, 1.0f);
}
