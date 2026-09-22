shader_type canvas_item;

// Matrix-style digital rain, generated procedurally.
//
// Drawn on a full-rect ColorRect. Procedural rather than a video loop so it
// stays sharp at any display size, costs no video decode during gameplay and
// adds no LFS assets. Every parameter is exposed so a slide can dial the same
// effect from a bold attract background down to a quiet gameplay backdrop.

// Grid. 72 x 36 gives roughly square cells on a 16:9 display.
uniform float columns = 72.0;
uniform float rows = 36.0;

// Motion.
uniform float fall_speed = 0.20;                            // screens per second
uniform float trail_length : hint_range(0.05, 1.0) = 0.55;  // fraction of a screen
uniform float density : hint_range(0.0, 1.0) = 0.85;        // fraction of columns raining
uniform float glyph_rate = 8.0;                             // glyph changes per second
uniform float flicker : hint_range(0.0, 1.0) = 0.25;

// Colour.
uniform float intensity : hint_range(0.0, 4.0) = 1.0;
uniform vec3 head_color : source_color = vec3(0.85, 1.0, 0.9);
uniform vec3 trail_color : source_color = vec3(0.16, 0.9, 0.32);
uniform vec3 background_color : source_color = vec3(0.004, 0.024, 0.012);
uniform float background_alpha : hint_range(0.0, 1.0) = 1.0;

// Optional circular falloff, so the same shader can be a full-screen backdrop
// (0.0, the default) or a contained "code well" that fades out at the edge of
// a circle. `falloff_aspect` must be the node's width / height to stay round.
uniform float radial_falloff : hint_range(0.0, 1.0) = 0.0;
uniform float falloff_aspect = 1.0;

float hash1(float n) {
	return fract(sin(n * 12.9898) * 43758.5453123);
}

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// A pseudo-glyph on a 5x7 dot matrix, the low-res look of a katakana
// character. `seed` picks the character.
float glyph(vec2 cell, float seed) {
	// Inset so glyphs do not touch across cell boundaries.
	vec2 q = (cell - vec2(0.1, 0.08)) / vec2(0.8, 0.84);
	if (q.x < 0.0 || q.x > 1.0 || q.y < 0.0 || q.y > 1.0) {
		return 0.0;
	}
	vec2 grid = vec2(5.0, 7.0);
	vec2 id = floor(q * grid);
	vec2 f = fract(q * grid);
	float edge = min(min(f.x, 1.0 - f.x), min(f.y, 1.0 - f.y));
	float on = step(0.44, hash2(id + seed * 13.0));
	return on * step(0.14, edge);
}

void fragment() {
	float col = floor(UV.x * columns);
	float row = floor(UV.y * rows);
	vec2 cell = vec2(fract(UV.x * columns), fract(UV.y * rows));

	// Per-column stream: is it raining, how fast, and where is the head now.
	float active = step(1.0 - density, hash1(col * 3.13 + 1.7));
	float speed = fall_speed * (0.55 + 1.05 * hash1(col * 7.31 + 5.2));
	float head = fract(hash1(col * 1.97 + 11.3) + TIME * speed);

	// Brightness falls off behind the head, wrapping at the screen edge.
	float dist = fract(head - UV.y);
	float tail = 1.0 - smoothstep(0.0, trail_length, dist);
	float head_mask = smoothstep(0.03, 0.0, dist);

	// Glyphs mutate in place, independently of the stream.
	float step_id = floor(TIME * glyph_rate + hash2(vec2(col, row)) * 7.0);
	float g = glyph(cell, hash2(vec2(col, row) + step_id));

	float fl = 1.0 - flicker * hash2(vec2(col, floor(TIME * 11.0)));
	float lum = tail * active * fl;

	float mask = 1.0;
	if (radial_falloff > 0.0) {
		vec2 q = (UV - vec2(0.5)) * vec2(falloff_aspect, 1.0) * 2.0;
		mask = 1.0 - smoothstep(1.0 - radial_falloff, 1.0, length(q));
	}

	vec3 c = mix(trail_color, head_color, head_mask);
	COLOR = vec4((background_color + c * g * lum * intensity) * mask, background_alpha * mask);
}
