extends CanvasItem

## Shows this node only while one game is being played.
##
## Both games share the gameplay HUD. The parts that belong to one of them
## (the ACT marker and FREED roster for the Matrix, the CHAPTER marker and
## SAVED roster for Terminator 2) carry this script with `game` set to that
## game's key, and follow the player variable `game`, which game_select sets
## on every player.

@export var game: String = "matrix"

func _ready() -> void:
	if MPF.game:
		MPF.game.connect("player_update", _on_player_update)

func _on_player_update(var_name: String, value: Variant) -> void:
	if var_name == "game":
		visible = str(value) == game
