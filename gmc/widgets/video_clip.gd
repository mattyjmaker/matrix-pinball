extends MPFVideoPlayer

## Generic film-clip player: one widget scene serves the whole library.
##
## widget_player passes the clip name as a token and this loads
## `<video_root>/<name>.ogv` at play time, so adding a clip is one YAML line and
## one file rather than a new scene. One .tscn per clip does not scale to a
## library of film footage.
##
##     widget_player:
##       agent_battle_started:
##         video_clip:
##           tokens:
##             clip: agent_smith_intro
##
## The clips themselves are deliberately outside version control. See
## gmc/video/README.md.

## Folder holding the clips. Godot 4 plays Ogg Theora (.ogv) and nothing else.
@export var video_root: String = "res://video"
## The widget_player token, or event arg, naming the clip.
@export var token_name: String = "clip"
## Played when the requested clip is missing, so a gap is visible on the display
## rather than silent. Leave empty to show nothing.
@export var fallback_clip: String = ""

var _owner_scene: Node

func _ready() -> void:
	super()
	if Engine.is_editor_hint():
		return
	# Registering as an updater is what makes plain `widget_player` tokens
	# arrive here, with no `action: method` needed in the YAML.
	_owner_scene = MPF.util.find_parent_slide_or_widget(self)
	if _owner_scene:
		_owner_scene.register_updater(self)

func _exit_tree() -> void:
	if _owner_scene and is_instance_valid(_owner_scene):
		_owner_scene.remove_updater(self)

## Called by MPFSceneBase.action_update when the widget is played or updated.
func update(settings: Dictionary, kwargs: Dictionary = {}) -> void:
	var requested = kwargs.get(
		token_name,
		settings.get("tokens", {}).get(token_name, settings.get(token_name, ""))
	)
	play_clip(str(requested))

func play_clip(clip_name: String) -> void:
	if clip_name.is_empty():
		clip_name = fallback_clip
	if clip_name.is_empty():
		log.warning("No '%s' token supplied, so there is nothing to play." % token_name)
		return

	var path: String = "%s/%s.ogv" % [video_root, clip_name]
	if not ResourceLoader.exists(path):
		log.error("Clip '%s' not found at %s. Run tools/check_video.py." % [clip_name, path])
		if fallback_clip and clip_name != fallback_clip:
			play_clip(fallback_clip)
		return

	stream = load(path)
	_play()
