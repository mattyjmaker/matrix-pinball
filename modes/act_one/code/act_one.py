"""Act I controller: the story order, the Mission scoop and the FREED roster.

The individual chapters, multiballs and The One are ordinary YAML modes. This
mode decides which of them may start, and records what each one achieved:

- Chapters play in film order from the mode scoop (the Mission scoop). After
  chapter 4, the scoop replays the first chapter not yet completed.
- One multiball at a time. A multiball requested while another runs waits in
  the player's `mb_pending` queue and starts when the running one ends.
- Each completed chapter or multiball frees one crew member. Enough names
  (the `the_one_threshold` setting) light The One, which the scoop then
  starts in preference to a chapter replay.
- The One survives ball end: `the_one_stage` stays set, and it restarts on the
  player's next ball until the EMP moves the player to Act II.

Act II's and Act III's controllers (modes/act_two, modes/act_three) are this
class with their own tables: every act-specific name is a class attribute
below.

See docs/11-rules-act-1.md.
"""
from mpf.core.mode import Mode

# chapter number: (mode that starts it, roster variable it lights, title)
CHAPTERS = {
    1: ("ch1_trinity_escape", "freed_trinity", "TRINITY'S ESCAPE"),
    2: ("ch2_red_pill", "freed_apoc", "RED PILL"),
    3: ("ch3_construct", "freed_mouse", "THE CONSTRUCT"),
    4: ("ch4_rescue_lock", "freed_tank", "RESCUE MORPHEUS"),
}

# Every mode belonging to a chapter, for "is a chapter running".
CHAPTER_MODES = {
    1: ("ch1_trinity_escape",),
    2: ("ch2_red_pill", "ch2_unplugged"),
    3: ("ch3_construct",),
    4: ("ch4_rescue_lock", "ch4_rescue_mb"),
}

# Multiball name: the mode that runs it. Only one may run at a time.
MULTIBALLS = {
    "trinity": "trinity_mb",
    "sentinel": "sentinel_mb",
    "unplugged": "ch2_unplugged",
    "rescue": "ch4_rescue_mb",
    "the_one": "the_one",
}

# What each completion event frees.
ROSTER = {
    "ch1_completed": "freed_trinity",
    "ch2_completed": "freed_apoc",
    "ch3_completed": "freed_mouse",
    "ch4_completed": "freed_tank",
    "trinity_mb_completed": "freed_switch",
    "sentinel_mb_completed": "freed_dozer",
}

# Chapter number: (the mode for its first phase, the multiball that follows).
# If the first phase stops without its multiball running or starting, the
# chapter ends there, and a queued chapter multiball dies with its chapter.
CHAPTER_PHASES = {
    4: ("ch4_rescue_lock", "rescue"),
}

# How long a ball sits in the mode scoop (the Mission scoop) while a mode intro starts.
MODE_SCOOP_RELEASE_MS = 2000
MODE_SCOOP_AWARD_RELEASE_MS = 750


class ActOne(Mode):

    """Sequencing and bookkeeping for Act I."""

    __slots__ = ["_chapter_running"]

    CHAPTERS = CHAPTERS
    CHAPTER_MODES = CHAPTER_MODES
    MULTIBALLS = MULTIBALLS
    ROSTER = ROSTER
    CHAPTER_PHASES = CHAPTER_PHASES
    # The chapter that keeps the scoop's ball for its own choice screen.
    CHAPTER_KEEPS_BALL = 2
    # Chapter events: start_ch1, ch1_ended.
    CHAPTER_EVENT = "ch{}"
    CHAPTER_NEXT = "chapter_next"
    SCOOP_HOLD = "mode_scoop_hold"
    ROSTER_COUNT = "freed_count"
    # Posted with the name as ROSTER_ARG ("trinity"), never as `name`.
    ROSTER_EVENT = "crew_freed"
    ROSTER_ARG = "crew"
    ROSTER_GOAL = "FREE THE CREW"
    # The wizard: its multiball name, which also prefixes its player
    # variables and events (the_one_lit, the_one_stage).
    WIZARD = "the_one"
    WIZARD_TITLE = "THE ONE"
    WIZARD_THRESHOLD = "the_one_threshold"
    WIZARD_DONE = "the_one_emp"
    FEATURES = "act_one_features"
    COMPLETE = "act_one_complete"
    NEXT_ACT = "II"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chapter_running = None

    def mode_start(self, **kwargs):
        self._chapter_running = None
        self.player["mode_ready"] = 0

        for event in self.ROSTER:
            self.add_mode_event_handler(event, self._roster_award, event_name=event)
        for number in self.CHAPTERS:
            self.add_mode_event_handler(self._chapter_event(number) + "_ended", self._chapter_ended,
                                        number=number)
        for name, mode in self.MULTIBALLS.items():
            self.add_mode_event_handler("request_{}_mb".format(name), self._request_multiball, name=name)
            self.add_mode_event_handler("mode_{}_stopped".format(mode), self._multiball_stopped, name=name)
        for number, (mode, multiball) in self.CHAPTER_PHASES.items():
            self.add_mode_event_handler("mode_{}_stopped".format(mode), self._phase_stopped,
                                        number=number, multiball=multiball)
        self.add_mode_event_handler("drop_target_mode_drop_down", self._mode_drop_down)
        self.add_mode_event_handler("ball_hold_{}_held_ball".format(self.SCOOP_HOLD), self._mode_scoop)
        self.add_mode_event_handler(self.WIZARD_DONE, self._act_complete)

        if self._wizard_stage():
            # The wizard carries on from the stage the player reached.
            self._start_multiball(self.WIZARD)
        else:
            self.machine.events.post(self.FEATURES + "_start")
            self._start_pending_multiball()
            self._update_idle_objective()

    def mode_stop(self, **kwargs):
        # At ball end this mode can stop before the chapter modes post their
        # chN_ended, so record a chapter cut short by the drain here.
        if self._chapter_running and self.player[self.CHAPTER_NEXT] == self._chapter_running:
            self.player[self.CHAPTER_NEXT] = self._chapter_running + 1
        self._chapter_running = None
        # A chapter multiball still queued dies with its chapter.
        pending = self._pending()
        for _, multiball in self.CHAPTER_PHASES.values():
            if multiball in pending:
                pending.remove(multiball)
            self.player[multiball + "_mb_starting"] = 0
        self._set_pending(pending)

    def _chapter_event(self, number):
        return self.CHAPTER_EVENT.format(number)

    def _wizard_stage(self):
        return self.player[self.WIZARD + "_stage"]

    # --- chapters ----------------------------------------------------------

    def _next_chapter(self):
        """Return the chapter the scoop starts next, or None."""
        if self.player[self.CHAPTER_NEXT] <= len(self.CHAPTERS):
            return self.player[self.CHAPTER_NEXT]
        for number, (_, roster_var, _) in self.CHAPTERS.items():
            if not self.player[roster_var]:
                return number
        return None

    def _chapter_active(self):
        return any(self.machine.modes[mode].active
                   for modes in self.CHAPTER_MODES.values() for mode in modes) or self._chapter_running

    def _chapter_ended(self, number, **kwargs):
        del kwargs
        if self._chapter_running == number:
            self._chapter_running = None
        if self.player[self.CHAPTER_NEXT] == number:
            self.player[self.CHAPTER_NEXT] = number + 1
        self.machine.events.post("chapter_played", chapter=number)
        self._update_idle_objective()

    def _phase_stopped(self, number, multiball, **kwargs):
        """A chapter's first phase stopped: the chapter ends here unless its multiball took over."""
        del kwargs
        pending = self._pending()
        if multiball in pending:
            # The ball ended with the multiball queued behind another one.
            pending.remove(multiball)
            self._set_pending(pending)
        if not self.machine.modes[self.MULTIBALLS[multiball]].active and self._chapter_running == number and \
                not self.player[multiball + "_mb_starting"]:
            self.machine.events.post(self._chapter_event(number) + "_ended")

    # --- Mode drop and scoop (the Mission Drop and scoop) ----------------------

    def _mode_drop_down(self, **kwargs):
        del kwargs
        self.player["mode_ready"] = 1
        self._update_idle_objective()

    def _mode_scoop(self, **kwargs):
        """A ball is held in the mode scoop: start what is lit, if anything."""
        del kwargs
        startable = self.player["mode_ready"] and not self._multiball_running() and \
            not self._chapter_active()

        if startable and self.player[self.WIZARD + "_lit"] and not self._wizard_stage():
            self._consume_mode_drop()
            self.machine.events.post(self.FEATURES + "_stop")
            self._start_multiball(self.WIZARD)
            self._release_mode_scoop(MODE_SCOOP_RELEASE_MS)
            return

        chapter = self._next_chapter() if startable else None
        if chapter is None:
            self.machine.events.post("mode_scoop_award")
            self._release_mode_scoop(MODE_SCOOP_AWARD_RELEASE_MS)
            return

        self._consume_mode_drop()
        self._chapter_running = chapter
        self.machine.events.post("start_" + self._chapter_event(chapter))
        # A chapter with a choice screen holds the ball and releases it itself.
        if chapter != self.CHAPTER_KEEPS_BALL:
            self._release_mode_scoop(MODE_SCOOP_RELEASE_MS)

    def _consume_mode_drop(self):
        self.player["mode_ready"] = 0
        self.machine.events.post("mode_drop_reset")

    def _release_mode_scoop(self, ms):
        self.delay.add(ms=ms, callback=self.machine.events.post, event="mode_scoop_release")

    # --- multiballs --------------------------------------------------------

    def _multiball_running(self):
        return any(self.machine.modes[mode].active for mode in self.MULTIBALLS.values())

    def _pending(self):
        # Only this act's multiballs: the queue is per player, not per act.
        return [name for name in str(self.player["mb_pending"]).split(",") if name in self.MULTIBALLS]

    def _set_pending(self, names):
        self.player["mb_pending"] = ",".join(names)

    def _request_multiball(self, name, **kwargs):
        del kwargs
        if self._multiball_running():
            pending = self._pending()
            if name not in pending:
                pending.append(name)
                self._set_pending(pending)
            self.machine.events.post("multiball_queued", multiball=name)
            return
        self._start_multiball(name)

    def _is_chapter_multiball(self, name):
        return any(name == multiball for _, multiball in self.CHAPTER_PHASES.values())

    def _start_multiball(self, name):
        # A chapter multiball's start event may still be in flight when its
        # first phase stops; this flag tells _phase_stopped it is coming.
        if self._is_chapter_multiball(name):
            self.player[name + "_mb_starting"] = 1
        self.machine.events.post("start_{}_mb".format(name))

    def _multiball_stopped(self, name, **kwargs):
        del kwargs
        if self._is_chapter_multiball(name):
            self.player[name + "_mb_starting"] = 0
        # Let the stopping mode finish before starting the next one.
        self.delay.add(ms=100, callback=self._after_multiball)

    def _after_multiball(self):
        if not self._start_pending_multiball():
            self._update_idle_objective()

    def _start_pending_multiball(self):
        if self._multiball_running() or self._wizard_stage():
            return False
        pending = self._pending()
        if not pending:
            return False
        name = pending.pop(0)
        self._set_pending(pending)
        self._start_multiball(name)
        return True

    # --- roster and the wizard ---------------------------------------------

    def _roster_award(self, event_name, **kwargs):
        del kwargs
        roster_var = self.ROSTER[event_name]
        if self.player[roster_var]:
            return
        self.player[roster_var] = 1
        self.player[self.ROSTER_COUNT] += 1
        self.machine.events.post(self.ROSTER_EVENT, **{self.ROSTER_ARG: roster_var.split("_", 1)[1]})

        threshold = int(self.machine.settings.get_setting_value(self.WIZARD_THRESHOLD))
        if not self.player[self.WIZARD + "_lit"] and self.player[self.ROSTER_COUNT] >= threshold:
            self.player[self.WIZARD + "_lit"] = 1
            self.machine.events.post(self.WIZARD + "_lit")
        self._update_idle_objective()

    def _act_complete(self, **kwargs):
        del kwargs
        # The last act has no next act: `act` stays, and the subclass records
        # that the story is over.
        if self.NEXT_ACT:
            self.player["act"] = self.NEXT_ACT
        self.player[self.WIZARD + "_stage"] = 0
        self.player["objective"] = ""
        # The finale is on screen: the next act holds its intro back.
        self.player["act_finale"] = 1
        # Anything this act still had queued is forfeited with the act.
        self._set_pending([])
        self.machine.events.post(self.COMPLETE)
        self.stop()

    # --- HUD ---------------------------------------------------------------

    def _update_idle_objective(self):
        """Point the player at the next thing to do when nothing else owns the HUD line."""
        if self._multiball_running() or self._chapter_active() or self._wizard_stage():
            return
        if self.player[self.WIZARD + "_lit"]:
            target = self.WIZARD_TITLE
        else:
            chapter = self._next_chapter()
            target = self.CHAPTERS[chapter][2] if chapter else None
        if target is None:
            self.player["objective"] = self.ROSTER_GOAL
        elif self.player["mode_ready"]:
            self.player["objective"] = "SHOOT THE MISSION SCOOP: " + target
        else:
            self.player["objective"] = "KNOCK DOWN THE MISSION DROP: " + target
