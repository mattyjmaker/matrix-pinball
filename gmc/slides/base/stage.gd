extends Control

## The idle centre stage of the gameplay slide.
##
## Holds the ambient effects that play when nothing else is happening, and gets
## out of the way when a mode pushes a widget. MPFSlide creates its widget
## container lazily and names it "_<slide>_widgets", so this watches the parent
## slide for that node rather than needing the modes to know about it.
##
## If the addon ever renames that container the effects simply stay visible,
## which is the safe way to fail.

@export var fade_seconds: float = 0.35

var _slide: Node

func _ready() -> void:
	_slide = get_parent()

func _process(delta: float) -> void:
	var target := 0.0 if _widget_active() else 1.0
	if not is_equal_approx(modulate.a, target):
		modulate.a = move_toward(modulate.a, target, delta / maxf(fade_seconds, 0.01))

func _widget_active() -> bool:
	if not is_instance_valid(_slide):
		return false
	for child in _slide.get_children():
		if child.name.ends_with("_widgets") and child.get_child_count() > 0:
			return true
	return false
