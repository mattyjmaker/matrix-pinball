shader_type canvas_item;

// Terminator 2 backdrop: the T-800's view. Near-black with a deep red cast
// that is brightest at the centre, scanlines, a faint targeting grid and a
// slow interference band drifting down the frame. Opaque, so it is the
// bottom layer of the slide. `aspect` must be the node's width / height or
// the grid cells will not be square.

uniform float aspect = 1.78;
uniform vec3 base_color : source_color = vec3(0.03, 0.0, 0.0);
uniform vec3 glow_color : source_color = vec3(0.17, 0.02, 0.02);
uniform float scanline_count = 540.0;
uniform float scanline_depth : hint_range(0.0, 1.0) = 0.22;
uniform float grid_cells = 22.0;
uniform float grid_alpha : hint_range(0.0, 1.0) = 0.06;
uniform float band_speed = 0.05;

void fragment() {
	vec2 d = UV - vec2(0.5);
	float r = length(d * vec2(aspect, 1.0));
	vec3 col = mix(glow_color, base_color, smoothstep(0.05, 1.05, r));

	// Targeting grid.
	vec2 g = fract(vec2(UV.x * aspect, UV.y) * grid_cells);
	float line = min(min(g.x, 1.0 - g.x), min(g.y, 1.0 - g.y));
	float grid = (1.0 - smoothstep(0.0, 0.03, line)) * grid_alpha;
	col += vec3(0.7, 0.12, 0.1) * grid;

	// Interference band.
	float band = fract(UV.y - TIME * band_speed);
	float band_v = exp(-pow((band - 0.5) * 14.0, 2.0)) * 0.06;
	col += vec3(0.6, 0.1, 0.08) * band_v;

	// Scanlines.
	float scan = 0.5 + 0.5 * sin(UV.y * scanline_count * 6.2831853);
	col *= 1.0 - scanline_depth * scan;

	COLOR = vec4(col, 1.0);
}
