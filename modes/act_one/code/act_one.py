"""Act I controller: the story order, the Mission scoop and the FREED roster.

The individual chapters, multiballs and The One are ordinary YAML modes. This
mode decides which of them may start, and records what each one achieved:

- Chapters play in film order from the Mission scoop. After chapter 4, the
  scoop replays the first chapter not yet completed.
- One multiball at a time. A multiball requested while another runs waits in
  the player's `mb_pending` queue and starts when the running one ends.
- Each completed chapter or multiball frees one crew member. Enough names
  (the `the_one_threshold` setting) light The One, which the scoop then
  starts in preference to a chapter replay.
- The One survives ball end: `the_one_stage` stays set, and it restarts on the
  player's next ball until the EMP moves the player to Act II.

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

# How long a ball sits in the Mission scoop while a mode intro starts.
MISSION_RELEASE_MS = 2000
MISSION_AWARD_RELEASE_MS = 750


class ActOne(Mode):

    """Sequencing and bookkeeping for Act I."""

    __slots__ = ["_chapter_running"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chapter_running = None

    def mode_start(self, **kwargs):
        self._chapter_running = None
        self.player["mission_ready"] = 0

        for event in ROSTER:
            self.add_mode_event_handler(event, self._roster_award, event_name=event)
        for number in CHAPTERS:
            self.add_mode_event_handler("ch{}_ended".format(number), self._chapter_ended, number=number)
        for name, mode in MULTIBALLS.items():
            self.add_mode_event_handler("request_{}_mb".format(name), self._request_multiball, name=name)
            self.add_mode_event_handler("mode_{}_stopped".format(mode), self._multiball_stopped, name=name)
        self.add_mode_event_handler("drop_target_mission_drop_down", self._mission_drop_down)
        self.add_mode_event_handler("ball_hold_mission_hold_held_ball", self._mission_scoop)
        self.add_mode_event_handler("mode_ch4_rescue_lock_stopped", self._rescue_lock_stopped)
        self.add_mode_event_handler("the_one_emp", self._act_complete)

        if self.player["the_one_stage"]:
            # The One carries on from the stage the player reached.
            self._start_multiball("the_one")
        else:
            self.machine.events.post("act_one_features_start")
            self._start_pending_multiball()
            self._update_idle_objective()

    def mode_stop(self, **kwargs):
        # At ball end this mode can stop before the chapter modes post their
        # chN_ended, so record a chapter cut short by the drain here.
        if self._chapter_running and self.player["chapter_next"] == self._chapter_running:
            self.player["chapter_next"] = self._chapter_running + 1
        self._chapter_running = None
        # A rescue multiball still queued dies with its chapter.
        pending = self._pending()
        if "rescue" in pending:
            pending.remove("rescue")
            self._set_pending(pending)
        self.player["rescue_mb_starting"] = 0

    # --- chapters ----------------------------------------------------------

    def _next_chapter(self):
        """Return the chapter the scoop starts next, or None."""
        if self.player["chapter_next"] <= 4:
            return self.player["chapter_next"]
        for number, (_, freed_var, _) in CHAPTERS.items():
            if not self.player[freed_var]:
                return number
        return None

    def _chapter_active(self):
        return any(self.machine.modes[mode].active
                   for modes in CHAPTER_MODES.values() for mode in modes) or self._chapter_running

    def _chapter_ended(self, number, **kwargs):
        del kwargs
        if self._chapter_running == number:
            self._chapter_running = None
        if self.player["chapter_next"] == number:
            self.player["chapter_next"] = number + 1
        self.machine.events.post("chapter_played", chapter=number)
        self._update_idle_objective()

    def _rescue_lock_stopped(self, **kwargs):
        """Chapter 4 ends here if its lock phase ended without the multiball."""
        del kwargs
        pending = self._pending()
        if "rescue" in pending:
            # The ball ended with the rescue queued behind another multiball.
            pending.remove("rescue")
            self._set_pending(pending)
        if not self.machine.modes["ch4_rescue_mb"].active and self._chapter_running == 4 and \
                not self._rescue_starting():
            self.machine.events.post("ch4_ended")

    def _rescue_starting(self):
        return self.player["rescue_mb_starting"] == 1

    # --- Mission Drop and scoop -------------------------------------------------

    def _mission_drop_down(self, **kwargs):
        del kwargs
        self.player["mission_ready"] = 1
        self._update_idle_objective()

    def _mission_scoop(self, **kwargs):
        """A ball is held in the Mission scoop: start what is lit, if anything."""
        del kwargs
        startable = self.player["mission_ready"] and not self._multiball_running() and \
            not self._chapter_active()

        if startable and self.player["the_one_lit"] and not self.player["the_one_stage"]:
            self._consume_mission()
            self.machine.events.post("act_one_features_stop")
            self._start_multiball("the_one")
            self._release_mission(MISSION_RELEASE_MS)
            return

        chapter = self._next_chapter() if startable else None
        if chapter is None:
            self.machine.events.post("mission_scoop_award")
            self._release_mission(MISSION_AWARD_RELEASE_MS)
            return

        self._consume_mission()
        self._chapter_running = chapter
        self.machine.events.post("start_ch{}".format(chapter))
        # Chapter 2 holds the ball through the pill choice and releases it itself.
        if chapter != 2:
            self._release_mission(MISSION_RELEASE_MS)

    def _consume_mission(self):
        self.player["mission_ready"] = 0
        self.machine.events.post("mission_drop_reset")

    def _release_mission(self, ms):
        self.delay.add(ms=ms, callback=self.machine.events.post, event="mission_release")

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
            self.machine.events.post("multiball_queued", name=name)
            return
        self._start_multiball(name)

    def _start_multiball(self, name):
        if name == "rescue":
            self.player["rescue_mb_starting"] = 1
        self.machine.events.post("start_{}_mb".format(name))

    def _multiball_stopped(self, name, **kwargs):
        del kwargs
        if name == "rescue":
            self.player["rescue_mb_starting"] = 0
        # Let the stopping mode finish before starting the next one.
        self.delay.add(ms=100, callback=self._after_multiball)

    def _after_multiball(self):
        if not self._start_pending_multiball():
            self._update_idle_objective()

    def _start_pending_multiball(self):
        if self._multiball_running() or self.player["the_one_stage"]:
            return False
        pending = self._pending()
        if not pending:
            return False
        name = pending.pop(0)
        self._set_pending(pending)
        self._start_multiball(name)
        return True

    # --- roster and The One ------------------------------------------------

    def _roster_award(self, event_name, **kwargs):
        del kwargs
        freed_var = ROSTER[event_name]
        if self.player[freed_var]:
            return
        self.player[freed_var] = 1
        self.player["freed_count"] += 1
        self.machine.events.post("crew_freed", name=freed_var[len("freed_"):])

        threshold = int(self.machine.settings.get_setting_value("the_one_threshold"))
        if not self.player["the_one_lit"] and self.player["freed_count"] >= threshold:
            self.player["the_one_lit"] = 1
            self.machine.events.post("the_one_lit")
        self._update_idle_objective()

    def _act_complete(self, **kwargs):
        del kwargs
        self.player["act"] = "II"
        self.player["the_one_stage"] = 0
        self.player["objective"] = ""
        self.machine.events.post("act_one_complete")
        self.stop()

    # --- HUD ---------------------------------------------------------------

    def _update_idle_objective(self):
        """Point the player at the next thing to do when nothing else owns the HUD line."""
        if self._multiball_running() or self._chapter_active() or self.player["the_one_stage"]:
            return
        if self.player["the_one_lit"]:
            target = "THE ONE"
        else:
            chapter = self._next_chapter()
            target = CHAPTERS[chapter][2] if chapter else None
        if target is None:
            self.player["objective"] = "FREE THE CREW"
        elif self.player["mission_ready"]:
            self.player["objective"] = "SHOOT THE MISSION SCOOP: " + target
        else:
            self.player["objective"] = "KNOCK DOWN THE MISSION DROP: " + target
