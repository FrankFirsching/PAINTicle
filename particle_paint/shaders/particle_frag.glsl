// Particle Paint shader
//
// Texturize the blown-up particle quad with a soft falloff

in vec2 center;
in Particle p_frag;

out vec4 frag_color;

uniform vec2 image_size;

void main()
{
  // We already did aspect correction in the geometry shader, so we divide by width of image
  vec2 offset = (gl_FragCoord.xy - center)/image_size.xx;
  offset *= 2/p_frag.size;
  float dist = length(offset);
  float alpha = 1-p_frag.age/p_frag.max_age;
  frag_color = vec4(p_frag.color, alpha*(1-dist*dist));
}
