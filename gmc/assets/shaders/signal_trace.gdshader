shader_type canvas_item;

// Signal trace: a sonar-style sweep for the idle centre stage of the gameplay
// slide. The story is Morpheus tracing Neo, so the idle screen is a search in
// progress rather than a decoration.
//
// Drawn on a ColorRect. `aspect` must be set to the node's width / height or
// the sweep will be an ellipse.

uniform float aspect = 1.78;
uniform float sweep_speed = 0.22;                          // revolutions per second
uniform float ring_count = 4.0;
uniform float contact_count : hint_range(0.0, 8.0) = 6.0;
uniform float intensity : hint_range(0.0, 2.0) = 1.0;
uniform vec3 grid_color : source_color = vec3(0.16, 0.9, 0.32);
uniform vec3 sweep_color : source_color = vec3(0.7, 1.0, 0.78);

const float TAU_ = 6.2831853;

float hash1(float n) {
	return fract(sin(n * 12.9898) * 43758.5453123);
}

void fragment() {
	// Normalised so the short axis spans -1..1 and circles stay round.
	vec2 p = (UV - vec2(0.5)) * vec2(aspect, 1.0) * 2.0;
	float r = length(p);
	float a01 = fract((atan(p.y, p.x) + PI) / TAU_);

	// Everything fades out at the edge of the dish.
	float dish = smoothstep(1.0, 0.86, r);

	// Range rings.
	float rr = r * ring_count;
	float d_ring = min(fract(rr), 1.0 - fract(rr));
	float rings = (1.0 - smoothstep(0.0, 0.035, d_ring)) * 0.30;

	// Crosshair.
	float crosshair = max(
		1.0 - smoothstep(0.0, 0.006, abs(p.y)),
		1.0 - smoothstep(0.0, 0.006, abs(p.x))
	) * 0.18;

	// Sweep arm with a decaying trail behind it.
	float sweep_pos = fract(TIME * sweep_speed);
	float behind = fract(a01 - sweep_pos);
	float trail = exp(-behind * 6.0) * 0.34;
	float arm = (1.0 - smoothstep(0.0, 0.004, behind)) * 0.6;

	// Contacts light as the arm passes them, then decay until it comes round.
	float contacts = 0.0;
	for (int i = 0; i < 8; i++) {
		float fi = float(i);
		float live = step(fi, contact_count - 1.0);
		float cr = 0.22 + 0.66 * hash1(fi * 3.7 + 1.0);
		float ca = hash1(fi * 9.1 + 4.0);
		vec2 cp = vec2(cos(ca * TAU_ - PI), sin(ca * TAU_ - PI)) * cr;
		float age = fract(sweep_pos - ca);
		float blip = 1.0 - smoothstep(0.0, 0.045, length(p - cp));
		contacts += blip * exp(-age * 5.0) * live;
	}

	float lum = (rings + crosshair + trail + arm + contacts) * dish * intensity;
	vec3 col = grid_color * (rings + crosshair) + sweep_color * (trail + arm + contacts);
	COLOR = vec4(col, clamp(lum, 0.0, 1.0));
}
