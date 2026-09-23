shader_type canvas_item;

// Occasional "deja vu" tear: every `interval` seconds the slide beneath this
// overlay is sliced into bands, a few of them are shifted sideways and the
// colour channels are pulled apart for a fraction of a second.
//
// Reads the back buffer, so this node must sit above everything it should
// tear. Between glitches it samples straight through and is a no-op.

uniform sampler2D screen_texture : hint_screen_texture, repeat_disable, filter_nearest;

uniform float interval = 9.0;                         // seconds between tears
uniform float duration = 0.22;                        // seconds a tear lasts
uniform float band_count = 26.0;
uniform float displacement : hint_range(0.0, 0.2) = 0.03;
uniform float channel_split : hint_range(0.0, 0.05) = 0.006;
uniform float band_share : hint_range(0.0, 1.0) = 0.4;  // fraction of bands that move

float hash1(float n) {
	return fract(sin(n * 12.9898) * 43758.5453123);
}

void fragment() {
	float cycle = floor(TIME / interval);
	float t = TIME - cycle * interval;

	// Ease the tear in and out so it does not pop.
	float active = (1.0 - smoothstep(0.0, duration, t)) * step(t, duration);

	float seed = hash1(cycle * 7.13 + 2.0);
	float band = floor(UV.y * band_count + seed * 13.0);
	float moves = step(1.0 - band_share, hash1(band * 2.31 + cycle * 17.0));
	float shift = (hash1(band * 5.77 + cycle * 3.1) - 0.5) * displacement * moves * active;

	float split = channel_split * active;
	vec2 uv = SCREEN_UV + vec2(shift, 0.0);

	COLOR = vec4(
		texture(screen_texture, uv + vec2(split, 0.0)).r,
		texture(screen_texture, uv).g,
		texture(screen_texture, uv - vec2(split, 0.0)).b,
		1.0
	);
}
