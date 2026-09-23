shader_type canvas_item;

// CRT phosphor overlay: scanlines plus a vignette, drawn as a dark full-rect
// ColorRect above the slide content. Alpha only, so it darkens what is behind
// it rather than tinting it, unless `tint` is changed from black.

uniform float scanline_count = 720.0;
uniform float scanline_depth : hint_range(0.0, 1.0) = 0.18;
uniform float vignette_strength : hint_range(0.0, 2.0) = 0.9;
uniform float vignette_softness : hint_range(0.05, 1.5) = 0.65;
uniform vec3 tint : source_color = vec3(0.0, 0.0, 0.0);

void fragment() {
	// Scanlines: a sine across the vertical axis, 0 at the line, 1 between.
	float scan = 0.5 + 0.5 * sin(UV.y * scanline_count * 6.2831853);
	float darken = scanline_depth * scan;

	// Vignette: darkens towards the corners.
	vec2 d = UV - vec2(0.5);
	float r = length(d * vec2(1.05, 1.0)) * 1.4142136;
	float vig = smoothstep(vignette_softness, 1.0, r) * vignette_strength;

	COLOR = vec4(tint, clamp(darken + vig, 0.0, 1.0));
}
