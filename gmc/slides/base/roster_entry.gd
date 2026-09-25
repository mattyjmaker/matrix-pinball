extends Label

## One name in a roster: the Matrix's FREED list or Terminator 2's SAVED list.
##
## Dim until the player has earned that name, then lit. Bound to the player
## variable `<prefix>_<key>` (`freed_trinity`, `saved_john`), so it starts
## working the moment a mode sets that variable and simply stays dim until then.

@export var key: String = ""
@export var prefix: String = "freed"
@export var freed: bool = false
@export var dim_color: Color = Color(0.28, 0.62, 0.34, 0.6)
@export var lit_color: Color = Color(0.82, 1.0, 0.86, 1.0)

func _ready() -> void:
	_apply()
	if MPF.game:
		MPF.game.connect("player_update", _on_player_update)

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == "%s_%s" % [prefix, key.to_lower()]:
		freed = bool(value)
		_apply()

func _apply() -> void:
	text = ("[+] " if freed else "[ ] ") + key.to_upper()
	add_theme_color_override("font_color", lit_color if freed else dim_color)
