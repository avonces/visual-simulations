#version 430

// local group size
layout( local_size_x = 1, local_size_y = 1 ) in;

// input texture (format!)
layout( rgba8, location = 0 ) uniform image2D destTex;

// variables to get from the python program running this
uniform float time;
uniform vec3 clr_fg;
// uniform vec3 clr_bg;

// what will be done for each texel
void main() {
    // get coordinates of the textel
    ivec2 texelPos = ivec2( gl_GlobalInvocationID.xy );

    // get the value that is stored for the texel in the image
    float texelOldVal = imageLoad( destTex, texelPos ).a;

    // waveeeeeee
    float texelNewVal = sin(float(gl_WorkGroupID.x + gl_WorkGroupID.y) * 0.01 + time) / 2.0 + 0.5;

    // store the value that has been calculated for the texel in the image
    imageStore(destTex, texelPos, vec4(clr_fg.r, clr_fg.g, clr_fg.b, texelNewVal));
}
