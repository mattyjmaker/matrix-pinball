extends Label

## Pulses a label's opacity. Used for attract-mode prompts such as "PRESS START"
## so the slide has motion without needing an AnimationPlayer per slide.

@export var cycles_per_second: float = 0.6
@export var min_alpha: float = 0.25
@export var max_alpha: float = 1.0

func _process(_delta: float) -> void:
	var phase := Time.get_ticks_msec() / 1000.0 * cycles_per_second * TAU
	modulate.a = lerp(min_alpha, max_alpha, 0.5 + 0.5 * sin(phase))
