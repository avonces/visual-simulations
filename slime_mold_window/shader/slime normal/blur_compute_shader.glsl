#version 430

// local group size
layout( local_size_x = 1, local_size_y = 1 ) in;

// input texture (format!)
layout( rgba8, location = 0 ) uniform image2D destTex;

// variables to get from the python program running this
uniform float frame_time;
uniform float diffusion_speed;  // blur-specific values from here on
uniform float evaporation_speed;

float blur( ivec2 xy ) {  // weighted average of the eight pixel sourrounding the pixel at xy and the pixel itself
    return (  // devide the sum of all values by the number of values
        imageLoad( destTex, xy).a +
        imageLoad( destTex, xy + ivec2( -1, -1 ) ).a +
        imageLoad( destTex, xy + ivec2( -1, 0 ) ).a +
        imageLoad( destTex, xy + ivec2( -1, 1 ) ).a +
        imageLoad( destTex, xy + ivec2( 0, -1 ) ).a +
        imageLoad( destTex, xy + ivec2( 0, 1 ) ).a +
        imageLoad( destTex, xy + ivec2( 1, -1 ) ).a +
        imageLoad( destTex, xy + ivec2( 1, 0 ) ).a +
        imageLoad( destTex, xy + ivec2( 1, 1 ) ).a
    ) / 9;
}

float diffuse( float value, float value_blurred ) {  // linearly interpolate between the values
    return mix(
        value,  // start of the interpolation range
        value_blurred,  // end of the interpolation range
        diffusion_speed * frame_time  // value to use to interpolate
    );
}

float evaporate( float value_diffused ) {
    return max(
        0,  // the lowest possible value should be 0
        value_diffused - evaporation_speed * frame_time  // subtract the evaporated quantity
    );
}

// what will be done for each texel
void main() {
    // get coordinates of the textel
    ivec2 texelPos = ivec2( gl_GlobalInvocationID.xy );

    // get the value that is stored for the texel in the image
    float texelOldVal = imageLoad( destTex, texelPos ).a;

    // calculate the new value: blur -> diffusion -> evaporation
    float texelNewVal = evaporate( diffuse( texelOldVal, blur( texelPos ) ) );

    // store the value that has been calculated for the texel in the image
    imageStore(
        destTex,
        texelPos,
        vec4(
            imageLoad( destTex, texelPos ).r,
            imageLoad( destTex, texelPos ).g,
            imageLoad( destTex, texelPos ).b,
            texelNewVal
        )
    );
}
