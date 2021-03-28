// Definitions shader

struct Particle
{
    vec3 location;
    vec2 uv;
    float size;
    float age;
    float max_age;
    vec3 color;
};

float particle_alpha(in Particle p, in vec2 offset)
{
    float dist = length(offset);
    float main_alpha = 1-p.age/p.max_age;
    return main_alpha*(1-dist*dist);
}