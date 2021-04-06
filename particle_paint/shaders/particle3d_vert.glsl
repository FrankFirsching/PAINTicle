// Particle Paint shader
//
// Project the particle positions into homogeneous clip space

in Particle p;
out Particle p_frag;

uniform float particle_size_age_factor;
uniform mat4 model_view_projection;

void main()
{
    gl_Position = model_view_projection * vec4(p.location, 1);
    gl_Position.z -= 0.001; // Use a small offset to draw points in front of surface
    gl_PointSize = particle_size(p, particle_size_age_factor);
    p_frag = p;
}
