#version 430

// local group size
layout( local_size_x = 1, local_size_y = 1 ) in;

// input texture (format!)
layout( rgba8, location = 0 ) uniform image2D destTex;

// data type: agent - each agent has a position and an angle
struct Agent {
    float x, y, angle;
};

// buffer containing agent data
layout( std430, binding = 1 ) restrict buffer buffer_agent_data {
    Agent agents[];
} AgentBuffer;

// constants
#define pi 3.141592653
#define width 1920  // the following constants woll be updated by the python program running this
#define height 1080
#define nOA 1000000 // number of agents

// variables to get from the python program running this
uniform float frame_time;
uniform vec3 clr_fg;
uniform float movement_speed;  // slime-specific values from here on
// uniform float rotation_speed;
// uniform float sensor_distance;
// uniform float sensor_angle;  // spacing between the sensors
// uniform float sensor_size;

// generating pseudo random numbers
float random( vec2 position ){
    return fract( sin( dot( position.xy, vec2( 12.9898, 78.233 ) ) ) * 43758.5453 );
}

// what will be done for each agent
void main() {
    // get coordinates of the textel
    int index = int( gl_GlobalInvocationID );
    if (index >= nOA) {
        return;
    }
    Agent agent = AgentBuffer.agents[index];

    // calculate the direction and position
    vec2 direction = vec2( cos( agent.angle ), sin( agent.angle ) );
    vec2 new_position = vec2( agent.x, agent.y ) + ( direction * movement_speed * frame_time );

    // handle wall collision
    if ( new_position.x < 0. || new_position.x >= width || new_position.y < 0. || new_position.y >= height ) {
        new_position.x = min( width - 0.01, max( 0., new_position.x ) );
        new_position.y = min( height - 0.01, max( 0., new_position.y ) );
        agent.angle = random( new_position ) * 2 * pi;
    }

    // ...
    agent.x = new_position.x;
    agent.y = new_position.y;

    // store the calculated values in the buffer and the texture
    AgentBuffer.agents[index] = agent;
    imageStore(
        destTex,
        ivec2( agent.x, agent.y ),
        vec4( clr_fg.r, clr_fg.g, clr_fg.b, 1.0 )
    );
}
