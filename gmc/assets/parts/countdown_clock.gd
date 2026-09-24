extends VBoxContainer

## A countdown clock for mode hurry-ups, drawn with the trace readout's
## number-lock: on every tick the digits churn and lock in, left to right.
##
## Not a widget itself. It sits inside a widget scene (countdown, pill_choice,
## act_select) and reads that widget's `widget_player` tokens:
##
##     widget_player:
##       mode_ch1_trinity_escape_started:
##         countdown:
##           key: ch1_clock
##           tokens:
##             label: THE TRUCK IS COMING
##             event: timer_ch1_rooftops_tick
##             seconds: "40"
##
## Tokens:
##   event      MPF event that carries the time, e.g. `timer_<name>_tick`.
##              The clock subscribes to it over BCP while it is on screen.
##   arg        Which argument of that event holds the seconds. Default `ticks`.
##   seconds    Shown until the first event arrives.
##   total      Full length, for the bar. Defaults to `seconds`.
##   label      Heading above the digits.
##   value_base, value_step
##              Optional. Adds a line showing value_base + value_step * seconds,
##              for a hurry-up whose award falls with the clock.

## At or below this many seconds the clock turns to the warning colour.
@export var warn_seconds: int = 5
@export var normal_color: Color = Color(0.85, 1.0, 0.88)
@export var normal_churn_color: Color = Color(0.2, 0.8, 0.35)
@export var warn_color: Color = Color(1.0, 0.42, 0.36)
@export var warn_churn_color: Color = Color(0.75, 0.16, 0.12)
@export var bar_color: Color = Color(0.16, 0.9, 0.32, 0.85)

@onready var _heading: Label = $Heading
@onready var _digits: RichTextLabel = $Digits
@onready var _fill: ColorRect = $Bar/Fill
@onready var _value: Label = $Value

var _owner_scene: Node
var _event: String = ""
var _arg: String = "ticks"
var _total: int = 0
var _value_base: int = 0
var _value_step: int = 0
var _has_value: bool = false

func _ready() -> void:
	_value.visible = false
	if Engine.is_editor_hint():
		return
	_owner_scene = MPF.util.find_parent_slide_or_widget(self)
	if _owner_scene:
		_owner_scene.register_updater(self)

func _exit_tree() -> void:
	if _owner_scene and is_instance_valid(_owner_scene):
		_owner_scene.remove_updater(self)
	_unsubscribe()

## Called by MPFSceneBase when the parent widget is played or updated.
func update(settings: Dictionary, kwargs: Dictionary = {}) -> void:
	_heading.text = _token(settings, kwargs, "label", "")
	_arg = _token(settings, kwargs, "arg", "ticks")
	var seconds := int(_token(settings, kwargs, "seconds", "0"))
	_total = int(_token(settings, kwargs, "total", str(seconds)))
	var base := _token(settings, kwargs, "value_base", "")
	_has_value = not base.is_empty()
	if _has_value:
		_value_base = int(base)
		_value_step = int(_token(settings, kwargs, "value_step", "0"))
	_value.visible = _has_value

	var event := _token(settings, kwargs, "event", "")
	if event != _event:
		_unsubscribe()
		_event = event
		if not _event.is_empty():
			MPF.server.add_event_handler(_event, _on_tick)
	show_seconds(seconds)

## Show a time, churning the digits into place.
func show_seconds(seconds: int) -> void:
	seconds = maxi(seconds, 0)
	var warn := seconds <= warn_seconds
	_digits.locked_color = warn_color if warn else normal_color
	_digits.scramble_color = warn_churn_color if warn else normal_churn_color
	_digits.set_target("%02d" % seconds)
	_digits.set_process(true)
	_fill.color = warn_color if warn else bar_color
	_fill.anchor_right = clampf(float(seconds) / float(maxi(_total, 1)), 0.0, 1.0)
	if _has_value:
		_value.text = _thousands(_value_base + _value_step * seconds)

func _on_tick(payload = null) -> void:
	if payload is Dictionary and payload.has(_arg):
		show_seconds(int(str(payload[_arg])))

func _unsubscribe() -> void:
	if not _event.is_empty() and not Engine.is_editor_hint():
		MPF.server.remove_event_handler(_event, _on_tick)
	_event = ""

func _token(settings: Dictionary, kwargs: Dictionary, name: String, default: String) -> String:
	if kwargs.has(name):
		return str(kwargs[name])
	var tokens: Dictionary = settings.get("tokens", {})
	if tokens.has(name):
		return str(tokens[name])
	return str(settings.get(name, default))

static func _thousands(value: int) -> String:
	var digits := str(absi(value))
	var out := ""
	while digits.length() > 3:
		out = "," + digits.substr(digits.length() - 3) + out
		digits = digits.substr(0, digits.length() - 3)
	return ("-" if value < 0 else "") + digits + out
