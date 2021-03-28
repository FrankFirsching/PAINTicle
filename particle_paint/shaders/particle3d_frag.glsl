// Particle Paint shader
//
// Texturize the blown-up particle quad with a soft falloff

in vec2 center;
in Particle p_frag;

out vec4 frag_color;

uniform vec2 image_size;
uniform float strength;

void main()
{
  // Discard everything outside of the circular point shape
  vec2 offset = 2*gl_PointCoord.xy - vec2(1);
  // Set the particles's color
  frag_color = vec4(p_frag.color, strength*particle_alpha(p_frag, offset));
  if(frag_color.a<0)
    discard;
}
