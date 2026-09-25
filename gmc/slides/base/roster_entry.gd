extends Label

## One name in a roster: the Matrix's FREED list or Terminator 2's SAVED list.
##
## Dim until the player has earned that name, then lit. Bound to the player
## variable `<prefix>_<key>` (`freed_trinity`, `saved_john`): it reads the
## current value when the slide is created, since the slide is rebuilt every
## ball, and follows updates from then on.

@export var key: String = ""
@export var prefix: String = "freed"
@export var freed: bool = false
@export var dim_color: Color = Color(0.28, 0.62, 0.34, 0.6)
@export var lit_color: Color = Color(0.82, 1.0, 0.86, 1.0)

func _ready() -> void:
	if MPF.game:
		var current = MPF.game.player.get(_variable())
		if current != null:
			freed = bool(current)
		MPF.game.connect("player_update", _on_player_update)
	_apply()

func _variable() -> String:
	return "%s_%s" % [prefix, key.to_lower()]

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == _variable():
		freed = bool(value)
		_apply()

func _apply() -> void:
	text = ("[+] " if freed else "[ ] ") + key.to_upper()
	add_theme_color_override("font_color", lit_color if freed else dim_color)
