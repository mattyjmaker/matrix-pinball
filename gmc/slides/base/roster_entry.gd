extends Label

## One name in the FREED roster.
##
## Dim until the player has freed that character, then lit. Bound to the player
## variable `freed_<key>`, so it starts working the moment a mode sets that
## variable and simply stays dim until then.

@export var key: String = ""
@export var freed: bool = false
@export var dim_color: Color = Color(0.28, 0.62, 0.34, 0.6)
@export var lit_color: Color = Color(0.82, 1.0, 0.86, 1.0)

func _ready() -> void:
	_apply()
	if MPF.game:
		MPF.game.connect("player_update", _on_player_update)

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == "freed_%s" % key.to_lower():
		freed = bool(value)
		_apply()

func _apply() -> void:
	text = ("[+] " if freed else "[ ] ") + key.to_upper()
	add_theme_color_override("font_color", lit_color if freed else dim_color)
