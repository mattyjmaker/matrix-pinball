extends RichTextLabel

## The trace readout: characters churn until they lock in, one position at a
## time, left to right, the way the trace program locks a number down in the
## films.
##
## Self-driving and purely cosmetic, so it runs on the idle stage with no rules
## behind it. Once the rules exist, call `set_target()` to make a trace spell
## something meaningful; `trace_locked` fires when the last position locks.
##
## Not named `finished`: RichTextLabel already defines a signal by that name.

signal trace_locked

## The string to lock in. Characters that are not in `charset` are treated as
## structure (separators) and lock immediately instead of churning.
@export var target: String = "312-555-0690"
@export var charset: String = "0123456789"
## How often the unlocked positions change, in times per second.
@export var scramble_hz: float = 22.0
## Seconds between one position locking and the next.
@export var lock_seconds: float = 0.28
## Seconds to hold the completed trace before starting over.
@export var hold_seconds: float = 2.5
## Set false to lock once and stay locked, for a mode-driven trace.
@export var loop: bool = true
@export var locked_color: Color = Color(0.85, 1.0, 0.88)
@export var scramble_color: Color = Color(0.2, 0.8, 0.35)

var _locked: int = 0
var _churn: PackedStringArray = PackedStringArray()
var _scramble_accum: float = 0.0
var _lock_accum: float = 0.0
var _hold_accum: float = 0.0
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	_rng.randomize()
	bbcode_enabled = true
	restart()

## Point the readout at a new string and start the lock again.
func set_target(value: String) -> void:
	target = value
	restart()

func restart() -> void:
	_locked = 0
	_lock_accum = 0.0
	_scramble_accum = 0.0
	_hold_accum = 0.0
	_churn.resize(target.length())
	_skip_separators()
	_scramble()
	_render()

func _process(delta: float) -> void:
	if _locked >= target.length():
		if not loop:
			set_process(false)
			return
		_hold_accum += delta
		if _hold_accum >= hold_seconds:
			restart()
		return

	_lock_accum += delta
	if _lock_accum >= lock_seconds:
		_lock_accum = 0.0
		_locked += 1
		_skip_separators()
		if _locked >= target.length():
			trace_locked.emit()
		_render()

	_scramble_accum += delta
	if _scramble_accum >= 1.0 / maxf(scramble_hz, 1.0):
		_scramble_accum = 0.0
		_scramble()
		_render()

## Separators are structure rather than unknowns, so they never churn.
func _skip_separators() -> void:
	while _locked < target.length() and charset.find(target[_locked]) == -1:
		_locked += 1

func _scramble() -> void:
	for i in range(_locked, target.length()):
		if charset.find(target[i]) == -1:
			_churn[i] = target[i]
		else:
			_churn[i] = charset[_rng.randi_range(0, charset.length() - 1)]

func _render() -> void:
	var done := ""
	var pending := ""
	for i in target.length():
		if i < _locked:
			done += target[i]
		else:
			pending += _churn[i]
	text = "[center][color=#%s]%s[/color][color=#%s]%s[/color][/center]" % [
		locked_color.to_html(false), done,
		scramble_color.to_html(false), pending
	]
