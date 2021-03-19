// Particle Paint shader
//
// Emits a quad for each point to draw the particles

#version 330

layout(points) in;
layout(triangle_strip, max_vertices=4) out;

out vec2 center;

uniform vec2 image_size;
uniform float particle_size;

void main()
{
    vec4 p = gl_in[0].gl_Position;

    center = (p.xy+vec2(1))*0.5*image_size;

    float aspect = image_size[0]/image_size[1];
    float size_x = particle_size*aspect;
    float size_y = particle_size*aspect;

    gl_Position = p + vec4(-size_x, -size_y, 0, 0);
    EmitVertex();


    gl_Position = p + vec4(-size_x,  size_y, 0, 0);
    EmitVertex();

    gl_Position = p + vec4( size_x, -size_y, 0, 0);
    EmitVertex();

    gl_Position = p + vec4( size_x,  size_y, 0, 0);
    EmitVertex();

    EndPrimitive();
}