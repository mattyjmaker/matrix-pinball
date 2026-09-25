extends HBoxContainer

## Lock indicator: one cell per ball locked.
##
## Colours its ColorRect children from the player variable named below, so the
## number of cells is whatever the scene contains. Reads the current value when
## the slide is created, since the slide is rebuilt every ball, and follows
## updates from then on.

@export var variable_name: String = "balls_locked"
@export var locked: int = 0
@export var empty_color: Color = Color(0.16, 0.9, 0.32, 0.2)
@export var filled_color: Color = Color(0.55, 1.0, 0.65, 0.95)

func _ready() -> void:
	if MPF.game:
		var current = MPF.game.player.get(variable_name)
		if current != null:
			locked = int(current)
		MPF.game.connect("player_update", _on_player_update)
	_apply()

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == variable_name:
		locked = int(value)
		_apply()

func _apply() -> void:
	var index := 0
	for cell in get_children():
		if cell is ColorRect:
			cell.color = filled_color if index < locked else empty_color
			index += 1
