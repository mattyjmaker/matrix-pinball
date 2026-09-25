"""Terminator 2 controller: the story order, the Command scoop and the SAVED roster.

The individual chapters, multiballs and Judgment Day are ordinary YAML modes.
This mode decides which of them may start, and records what each achieved:

- Chapters play in film order from the Command scoop (the mode scoop). After
  chapter 4, the scoop replays the first chapter not yet completed.
- One multiball at a time. A multiball requested while another runs waits in
  the player's `mb_pending` queue and starts when the running one ends.
- Each completed chapter or multiball saves one name. Enough names (the
  `judgment_day_threshold` setting) light Judgment Day, which the scoop then
  starts in preference to a chapter replay.
- Judgment Day survives ball end: `judgment_day_stage` stays set, and it
  restarts on the player's next ball until it is averted.

The shape is act_one.py's. See docs/12-rules-terminator-2.md.
"""
from mpf.core.mode import Mode

# chapter number: (mode that starts it, roster variable it lights, title)
CHAPTERS = {
    1: ("t2_ch1_arrival", "saved_john", "ARRIVAL"),
    2: ("t2_ch2_pescadero", "saved_sarah", "PESCADERO BREAK-OUT"),
    3: ("t2_ch3_dyson", "saved_dyson", "THE CHOICE"),
    4: ("t2_ch4_raid_lock", "saved_chip", "CYBERDYNE RAID"),
}

# Every mode belonging to a chapter, for "is a chapter running".
CHAPTER_MODES = {
    1: ("t2_ch1_arrival",),
    2: ("t2_ch2_pescadero", "t2_ch2_breakout_mb"),
    3: ("t2_ch3_dyson",),
    4: ("t2_ch4_raid_lock", "t2_ch4_raid_mb"),
}

# The chapter that keeps the scoop's ball for its own choice screen.
CHAPTER_KEEPS_BALL = 3

# Multiball name: the mode that runs it. Only one may run at a time.
MULTIBALLS = {
    "future_war": "future_war_mb",
    "t1000": "t1000_mb",
    "breakout": "t2_ch2_breakout_mb",
    "raid": "t2_ch4_raid_mb",
    "judgment_day": "judgment_day",
}

# What each completion event saves.
ROSTER = {
    "t2_ch1_completed": "saved_john",
    "t2_ch2_completed": "saved_sarah",
    "t2_ch3_completed": "saved_dyson",
    "t2_ch4_completed": "saved_chip",
    "future_war_mb_completed": "saved_resistance",
    "t1000_mb_completed": "saved_skynet",
}

# How long a ball sits in the Command scoop while a mode intro starts.
SCOOP_RELEASE_MS = 2000
SCOOP_AWARD_RELEASE_MS = 750


class T2Main(Mode):

    """Sequencing and bookkeeping for Terminator 2."""

    __slots__ = ["_chapter_running"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chapter_running = None

    def mode_start(self, **kwargs):
        self._chapter_running = None
        self.player["mode_ready"] = 0

        for event in ROSTER:
            self.add_mode_event_handler(event, self._roster_award, event_name=event)
        for number in CHAPTERS:
            self.add_mode_event_handler("t2_ch{}_ended".format(number), self._chapter_ended, number=number)
        for name, mode in MULTIBALLS.items():
            self.add_mode_event_handler("request_{}_mb".format(name), self._request_multiball, name=name)
            self.add_mode_event_handler("mode_{}_stopped".format(mode), self._multiball_stopped, name=name)
        self.add_mode_event_handler("drop_target_mode_drop_down", self._mode_drop_down)
        self.add_mode_event_handler("ball_hold_t2_scoop_hold_held_ball", self._scoop)
        self.add_mode_event_handler("mode_t2_ch2_pescadero_stopped", self._lock_phase_stopped,
                                    number=2, multiball="breakout")
        self.add_mode_event_handler("mode_t2_ch4_raid_lock_stopped", self._lock_phase_stopped,
                                    number=4, multiball="raid")
        self.add_mode_event_handler("judgment_day_averted", self._t2_complete)

        if self.player["judgment_day_stage"]:
            # Judgment Day carries on from the stage the player reached.
            self._start_multiball("judgment_day")
        else:
            self.machine.events.post("t2_features_start")
            self._start_pending_multiball()
            self._update_idle_objective()

    def mode_stop(self, **kwargs):
        # At ball end this mode can stop before the chapter modes post their
        # t2_chN_ended, so record a chapter cut short by the drain here.
        if self._chapter_running and self.player["t2_chapter_next"] == self._chapter_running:
            self.player["t2_chapter_next"] = self._chapter_running + 1
        self._chapter_running = None
        # A chapter multiball still queued dies with its chapter.
        pending = self._pending()
        for name in ("breakout", "raid"):
            if name in pending:
                pending.remove(name)
        self._set_pending(pending)
        self.player["raid_mb_starting"] = 0

    # --- chapters ----------------------------------------------------------

    def _next_chapter(self):
        """Return the chapter the scoop starts next, or None."""
        if self.player["t2_chapter_next"] <= 4:
            return self.player["t2_chapter_next"]
        for number, (_, saved_var, _) in CHAPTERS.items():
            if not self.player[saved_var]:
                return number
        return None

    def _chapter_active(self):
        return any(self.machine.modes[mode].active
                   for modes in CHAPTER_MODES.values() for mode in modes) or self._chapter_running

    def _chapter_ended(self, number, **kwargs):
        del kwargs
        if self._chapter_running == number:
            self._chapter_running = None
        if self.player["t2_chapter_next"] == number:
            self.player["t2_chapter_next"] = number + 1
        self.machine.events.post("t2_chapter_played", chapter=number)
        self._update_idle_objective()

    def _lock_phase_stopped(self, number, multiball, **kwargs):
        """A chapter's first phase stopped: the chapter ends here unless its multiball took over."""
        del kwargs
        pending = self._pending()
        if multiball in pending:
            # The ball ended with the multiball queued behind another one.
            pending.remove(multiball)
            self._set_pending(pending)
        starting = multiball == "raid" and self.player["raid_mb_starting"] == 1
        if not self.machine.modes[MULTIBALLS[multiball]].active and self._chapter_running == number \
                and not starting and not self._multiball_starting(multiball):
            self.machine.events.post("t2_ch{}_ended".format(number))

    def _multiball_starting(self, name):
        # The breakout multiball starts on request with no lock to wait for,
        # so its start event may already be in flight when the lock phase stops.
        return name == "breakout" and self.player["breakout_mb_starting"] == 1

    # --- Command scoop -----------------------------------------------------

    def _mode_drop_down(self, **kwargs):
        del kwargs
        self.player["mode_ready"] = 1
        self._update_idle_objective()

    def _scoop(self, **kwargs):
        """A ball is held in the Command scoop: start what is lit, if anything."""
        del kwargs
        startable = self.player["mode_ready"] and not self._multiball_running() and \
            not self._chapter_active()

        if startable and self.player["judgment_day_lit"] and not self.player["judgment_day_stage"]:
            self._consume_mode_drop()
            self.machine.events.post("t2_features_stop")
            self._start_multiball("judgment_day")
            self._release_scoop(SCOOP_RELEASE_MS)
            return

        chapter = self._next_chapter() if startable else None
        if chapter is None:
            self.machine.events.post("t2_scoop_award")
            self._release_scoop(SCOOP_AWARD_RELEASE_MS)
            return

        self._consume_mode_drop()
        self._chapter_running = chapter
        self.player["chapter"] = "CHAPTER {}".format(chapter)
        self.machine.events.post("start_t2_ch{}".format(chapter))
        if chapter != CHAPTER_KEEPS_BALL:
            self._release_scoop(SCOOP_RELEASE_MS)

    def _consume_mode_drop(self):
        self.player["mode_ready"] = 0
        self.machine.events.post("mode_drop_reset")

    def _release_scoop(self, ms):
        self.delay.add(ms=ms, callback=self.machine.events.post, event="t2_scoop_release")

    # --- multiballs --------------------------------------------------------

    def _multiball_running(self):
        return any(self.machine.modes[mode].active for mode in MULTIBALLS.values())

    def _pending(self):
        return [name for name in str(self.player["mb_pending"]).split(",") if name]

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

    def _start_multiball(self, name):
        if name == "raid":
            self.player["raid_mb_starting"] = 1
        if name == "breakout":
            self.player["breakout_mb_starting"] = 1
        self.machine.events.post("start_{}_mb".format(name))

    def _multiball_stopped(self, name, **kwargs):
        del kwargs
        if name == "raid":
            self.player["raid_mb_starting"] = 0
        if name == "breakout":
            self.player["breakout_mb_starting"] = 0
        # Let the stopping mode finish before starting the next one.
        self.delay.add(ms=100, callback=self._after_multiball)

    def _after_multiball(self):
        if not self._start_pending_multiball():
            self._update_idle_objective()

    def _start_pending_multiball(self):
        if self._multiball_running() or self.player["judgment_day_stage"]:
            return False
        pending = self._pending()
        if not pending:
            return False
        name = pending.pop(0)
        self._set_pending(pending)
        self._start_multiball(name)
        return True

    # --- roster and Judgment Day -------------------------------------------

    def _roster_award(self, event_name, **kwargs):
        del kwargs
        saved_var = ROSTER[event_name]
        if self.player[saved_var]:
            return
        self.player[saved_var] = 1
        self.player["saved_count"] += 1
        self.machine.events.post("name_saved", who=saved_var[len("saved_"):])

        threshold = int(self.machine.settings.get_setting_value("judgment_day_threshold"))
        if not self.player["judgment_day_lit"] and self.player["saved_count"] >= threshold:
            self.player["judgment_day_lit"] = 1
            self.machine.events.post("judgment_day_lit")
        self._update_idle_objective()

    def _t2_complete(self, **kwargs):
        del kwargs
        self.player["t2_complete"] = 1
        self.player["judgment_day_stage"] = 0
        self.player["chapter"] = "COMPLETE"
        self.player["objective"] = ""
        self.machine.events.post("t2_complete")
        self.stop()

    # --- HUD ---------------------------------------------------------------

    def _update_idle_objective(self):
        """Point the player at the next thing to do when nothing else owns the HUD line."""
        if self._multiball_running() or self._chapter_active() or self.player["judgment_day_stage"]:
            return
        if self.player["judgment_day_lit"]:
            target = "JUDGMENT DAY"
            self.player["chapter"] = "JUDGMENT DAY"
        else:
            chapter = self._next_chapter()
            target = CHAPTERS[chapter][2] if chapter else None
            if chapter:
                self.player["chapter"] = "CHAPTER {}".format(chapter)
        if target is None:
            self.player["objective"] = "SAVE THE FUTURE"
        elif self.player["mode_ready"]:
            self.player["objective"] = "SHOOT THE COMMAND SCOOP: " + target
        else:
            self.player["objective"] = "KNOCK DOWN THE PERIMETER DROP: " + target
