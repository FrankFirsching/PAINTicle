// Particle Paint shader
//
// Project the particle positions into homogeneous clip space

in Particle p;
out Particle p_frag;

uniform mat4 model_view_projection;

void main()
{
    gl_Position = model_view_projection * vec4(p.location, 1);

    p_frag = p;
}
