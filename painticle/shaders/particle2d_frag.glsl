// PAINTicle shader
//
// Texturize the blown-up particle quad with a soft falloff

in vec2 center;
in Particle p_frag;

out vec4 frag_color;

uniform vec2 image_size;
uniform float strength;

void main()
{
  // We already did aspect correction in the geometry shader, so we divide by width of image
  vec2 offset = (gl_FragCoord.xy - center)/image_size.xx;
  offset *= 2/p_frag.size;
  frag_color = vec4(p_frag.color, strength*particle_alpha(p_frag, offset));
  if(frag_color.a<0)
    discard;
}
