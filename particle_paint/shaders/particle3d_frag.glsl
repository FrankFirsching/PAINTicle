// Particle Paint shader
//
// Texturize the blown-up particle quad with a soft falloff

in vec2 center;
in Particle p_frag;

out vec4 frag_color;

uniform vec2 image_size;

vec3 srgb_to_linear(in vec3 c)
{
    bvec3 cutoff = lessThan(c, vec3(0.04045));
    vec3 higher = pow((c + vec3(0.055))/vec3(1.055), vec3(2.4));
    vec3 lower = c/vec3(12.92);

    return mix(higher, lower, cutoff);
}

void main()
{
  // Discard everything outside of the circular point shape
  vec2 offset = 2*gl_PointCoord.xy - vec2(1);
  // Set the particles's color (drawing to viewport, which is linear color space)
  frag_color = vec4(srgb_to_linear(p_frag.color), particle_alpha(p_frag, offset));
  if(frag_color.a<0)
    discard;
}
