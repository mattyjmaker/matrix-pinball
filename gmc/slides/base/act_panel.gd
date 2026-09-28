extends Control

## A HUD panel that belongs to some acts of the Matrix: the FREED roster in
## Act I, the ALLIES roster from Act II. Shown only while the player variable
## `act` is one of `acts`. Reads the current value when the slide is created,
## since the slide is rebuilt every ball, and follows updates from then on.
## With no game (the editor), it shows while "I" is in `acts`.

@export var acts: PackedStringArray = ["I"]

func _ready() -> void:
	var act = "I"
	if MPF.game:
		var current = MPF.game.player.get("act")
		if current != null:
			act = str(current)
		MPF.game.connect("player_update", _on_player_update)
	_apply(act)

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == "act":
		_apply(str(value))

func _apply(act: String) -> void:
	visible = act in acts
