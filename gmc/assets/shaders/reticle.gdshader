shader_type canvas_item;

// Targeting reticle for the idle centre stage of the Terminator 2 slide: two
// rings, a gapped crosshair, corner brackets, ticks around the outer ring, a
// marker sweeping round it and a pulsing centre. The T-800 acquiring a target
// rather than a decoration.
//
// Drawn on a ColorRect. `aspect` must be the node's width / height or the
// rings will be ellipses.

uniform float aspect = 1.0;
uniform float spin_speed = 0.08;                         // revolutions per second
uniform float intensity : hint_range(0.0, 2.0) = 1.0;
uniform vec3 line_color : source_color = vec3(0.9, 0.14, 0.1);
uniform vec3 mark_color : source_color = vec3(0.96, 0.96, 0.96);

const float TAU_ = 6.2831853;

float ring(float r, float radius, float w) {
	return 1.0 - smoothstep(0.0, w, abs(r - radius));
}

void fragment() {
	// Normalised so the short axis spans -1..1 and circles stay round.
	vec2 p = (UV - vec2(0.5)) * vec2(aspect, 1.0) * 2.0;
	float r = length(p);
	float a01 = fract((atan(p.y, p.x) + PI) / TAU_);
	float dish = smoothstep(1.0, 0.9, r);

	float outer = ring(r, 0.86, 0.008) * 0.55;
	float inner = ring(r, 0.30, 0.006) * 0.5;

	// Crosshair, with a gap inside the inner ring and stopping at the outer.
	float hx = 1.0 - smoothstep(0.0, 0.006, abs(p.y));
	float vx = 1.0 - smoothstep(0.0, 0.006, abs(p.x));
	float span = step(0.34, r) * step(r, 0.82);
	float cross = max(hx, vx) * span * 0.35;

	// Corner brackets on a square of half-size 0.62.
	vec2 a = abs(p);
	float on_square = 1.0 - smoothstep(0.0, 0.008, abs(max(a.x, a.y) - 0.62));
	float near_corner = step(0.44, min(a.x, a.y));
	float brackets = on_square * near_corner * 0.7;

	// Ticks every 15 degrees on the outer ring.
	float t = fract(a01 * 24.0);
	float tick = 1.0 - smoothstep(0.0, 0.1, min(t, 1.0 - t));
	float ticks = tick * step(0.80, r) * step(r, 0.86) * 0.5;

	// Marker sweeping round the outer ring, with a short trail.
	float behind = fract(a01 - TIME * spin_speed);
	float marker = exp(-behind * 40.0) * ring(r, 0.86, 0.02);

	// Pulsing centre.
	float pulse = 0.5 + 0.5 * sin(TIME * 2.0);
	float dot = (1.0 - smoothstep(0.0, 0.03, r)) * (0.4 + 0.6 * pulse);

	float lines = (outer + inner + cross + brackets + ticks) * dish * intensity;
	float marks = (marker + dot) * dish * intensity;
	vec3 col = line_color * lines + mark_color * marks;
	COLOR = vec4(col, clamp(lines + marks, 0.0, 1.0));
}
