#version 430


// MIT License
//
// Copyright (c) 2021 Leterax
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.


// local group size
layout( local_size_x = 1, local_size_y = 1 ) in;

// input texture (format!)
layout( rgba8, location = 0 ) uniform image2D destTex;

// data type: agent - each agent has a position and an angle
struct Agent {
    float x, y, angle, species;
};

// buffer containing agent data
layout( std430, binding = 1 ) restrict buffer buffer_agent_data {
    Agent agents[];
} AgentBuffer;

// constants
#define pi 3.141592653
#define width 1920  // the following constants will be updated by the python program running this
#define height 1080
#define nOA 1000000 // number of agents

// variables to get from the python program running this
uniform float frame_time;
uniform vec3 clr_fg;
uniform float movement_speed;  // slime-specific values from here on
uniform float rotation_speed;
uniform float sensor_angle;  // spacing between the sensors (offset)
uniform int sensor_distance;
uniform int sensor_size;

// generating pseudo random numbers
// TODO: better random function
float random( vec2 position ){
    return fract( sin( dot( position.xy, vec2( 12.9898, 78.233 ) ) ) * 43758.5453 );
}

// TODO: make the agents smarter
float get_sensor_value( Agent agent, float sensor_angle ) {
    float agent_sensor_angle = agent.angle + sensor_angle;
    vec2 sensor_direction = vec2( cos( agent_sensor_angle ), sin( agent_sensor_angle ));
    ivec2 sensor_center = ivec2( agent.x, agent.y ) + ivec2( sensor_direction * sensor_distance);

    float sensor_value = 0;
    for ( int offset_x = -sensor_size; offset_x <= sensor_size; offset_x++ ) {
        for ( int offset_y = -sensor_size; offset_y <= sensor_size; offset_y++ ) {
            ivec2 position = sensor_center + ivec2( offset_x, offset_y );

            if ( position.x >= 0 && position.x < width && position.y >=0 && position.y < height ) {
                sensor_value += imageLoad( destTex, position ).a;
            }
        }
    }
    return sensor_value;
}

// what will be done for each agent
void main() {
    // get coordinates of the textel
    int index = int( gl_GlobalInvocationID );
    if (index >= nOA) {
        return;
    }
    Agent agent = AgentBuffer.agents[index];

    // get the sensor values and determine the weights
    float weight_left = get_sensor_value( agent, sensor_angle );
    float weight_forward = get_sensor_value( agent, 0 );
    float weight_right = get_sensor_value( agent, -sensor_angle );

    float random_steer_strentgh = random( vec2( agent.x, agent.y )* frame_time * agent.angle );

    // adjust the agents angle based on those values
    if ( weight_forward > weight_left && weight_forward > weight_right ) {  // weight forward
        // keep angle
    }
    else if ( weight_forward < weight_left && weight_forward < weight_right ) {  // weight left or right is the biggest
        agent.angle += ( random_steer_strentgh - 0.5 ) * 2 * rotation_speed * frame_time;  // a bit of random steering
    }
    else if ( weight_right > weight_left ) {  // weight right is the biggest
        agent.angle -= random_steer_strentgh * rotation_speed * frame_time;  // subtract from the current angle
    }
    else if ( weight_left > weight_right ) {  // weigh left is the biggest
        agent.angle += random_steer_strentgh * rotation_speed * frame_time;  // add to the current angle
    }

    // calculate the direction and position
    vec2 direction = vec2( cos( agent.angle ), sin( agent.angle ) );
    vec2 new_position = vec2( agent.x, agent.y ) + ( direction * movement_speed * frame_time );

    // handle wall collision
    if ( new_position.x < 0.0 || new_position.x >= width || new_position.y < 0.0 || new_position.y >= height ) {
        new_position.x = min( width - 0.1, max( 0.0, new_position.x ) );
        new_position.y = min( height - 0.1, max( 0.0, new_position.y ) );
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
