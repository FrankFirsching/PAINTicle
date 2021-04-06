// Particle Paint shader
//
// Emits a quad for each point to draw the particles

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

in Particle p_geo[];
out vec2 center;
out Particle p_frag;

uniform vec2 image_size;
uniform float particle_size_age_factor;

void main()
{
    Particle particle = p_geo[0];
    vec4 pos = gl_in[0].gl_Position;

    p_frag = particle;
    center = particle.uv * image_size;

    float size = particle_size(particle, particle_size_age_factor);
    

    float aspect = image_size[0] / image_size[1];
    float size_x = size * aspect;
    float size_y = size * aspect;

    gl_Position = pos + vec4(-size_x, -size_y, 0, 0);
    EmitVertex();


    gl_Position = pos + vec4(-size_x,  size_y, 0, 0);
    EmitVertex();

    gl_Position = pos + vec4( size_x, -size_y, 0, 0);
    EmitVertex();

    gl_Position = pos + vec4( size_x,  size_y, 0, 0);
    EmitVertex();

    EndPrimitive();
}