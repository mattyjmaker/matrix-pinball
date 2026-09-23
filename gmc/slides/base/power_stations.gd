extends HBoxContainer

## Power station lock indicator: one cell per ball locked.
##
## Colours its ColorRect children from the player variable named below, so the
## number of stations is whatever the scene contains.

@export var variable_name: String = "balls_locked"
@export var locked: int = 0
@export var empty_color: Color = Color(0.16, 0.9, 0.32, 0.2)
@export var filled_color: Color = Color(0.55, 1.0, 0.65, 0.95)

func _ready() -> void:
	_apply()
	if MPF.game:
		MPF.game.connect("player_update", _on_player_update)

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
