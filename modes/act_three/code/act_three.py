"""Act III controller: the story order, the Mission scoop and the DEFENDERS roster.

The same sequencing as Acts I and II (modes/act_one/code/act_one.py), with
Act III's chapters, multiballs, roster and wizard:

- Chapters play in film order from the mode scoop (the Mission scoop). After
  chapter 4, the scoop replays the first chapter not yet completed.
- One multiball at a time, through the player's `mb_pending` queue. Chapter
  3, the Siege of Zion, is itself a multiball, so it counts as one.
- Each completed chapter or multiball adds one name to the DEFENDERS. Enough
  names (the `machine_city_threshold` setting) light the Machine City, which
  the scoop then starts in preference to a chapter replay.
- The Machine City survives ball end: `machine_city_stage` stays set, and it
  restarts on the player's next ball until Smith is beaten. That completes
  the Matrix: `matrix_complete` is set and the player plays on in the base
  mode, as a Terminator 2 player does after Judgment Day.

Act III starts on the ball the Architect's last shot ends Act II, as well as
on every ball while `act` is III and the Matrix is not complete.
See docs/15-rules-act-3.md.
"""
from modes.act_one.code.act_one import ActOne

# chapter number: (mode that starts it, roster variable it lights, title)
CHAPTERS = {
    1: ("a3_ch1_mobil_ave", "defenders_sati", "MOBIL AVENUE"),
    2: ("a3_ch2_club_hel", "defenders_lock", "CLUB HEL"),
    3: ("a3_ch3_siege_mb", "defenders_mifune", "THE SIEGE OF ZION"),
    4: ("a3_ch4_hammer", "defenders_roland", "THE HAMMER"),
}

# Every mode belonging to a chapter, for "is a chapter running".
CHAPTER_MODES = {
    1: ("a3_ch1_mobil_ave",),
    2: ("a3_ch2_club_hel",),
    3: ("a3_ch3_siege_mb",),
    4: ("a3_ch4_hammer",),
}

# Multiball name: the mode that runs it. Only one may run at a time.
MULTIBALLS = {
    "apu": "apu_mb",
    "swarm": "swarm_mb",
    "siege": "a3_ch3_siege_mb",
    "machine_city": "the_machine_city",
}

# What each completion event adds to the DEFENDERS.
ROSTER = {
    "a3_ch1_completed": "defenders_sati",
    "a3_ch2_completed": "defenders_lock",
    "a3_ch3_completed": "defenders_mifune",
    "a3_ch4_completed": "defenders_roland",
    "apu_mb_completed": "defenders_zee",
    "swarm_mb_completed": "defenders_kid",
}

# The Act III intro waits this long when Act III starts on the Architect's
# ball, so it does not play over the Sentinels clip (base.yaml, 8 s).
INTRO_AFTER_FINALE_MS = 8000


class ActThree(ActOne):

    """Sequencing and bookkeeping for Act III."""

    __slots__ = []

    CHAPTERS = CHAPTERS
    CHAPTER_MODES = CHAPTER_MODES
    MULTIBALLS = MULTIBALLS
    ROSTER = ROSTER
    # The Siege is started straight from the scoop as a multiball; no chapter
    # has a first phase that hands over to one.
    CHAPTER_PHASES = {}
    CHAPTER_KEEPS_BALL = None
    CHAPTER_EVENT = "a3_ch{}"
    CHAPTER_NEXT = "a3_chapter_next"
    SCOOP_HOLD = "a3_scoop_hold"
    ROSTER_COUNT = "defenders_count"
    ROSTER_EVENT = "defender_joined"
    ROSTER_ARG = "defender"
    ROSTER_GOAL = "DEFEND ZION"
    WIZARD = "machine_city"
    WIZARD_TITLE = "THE MACHINE CITY"
    WIZARD_THRESHOLD = "machine_city_threshold"
    WIZARD_DONE = "machine_city_peace"
    FEATURES = "act_three_features"
    COMPLETE = "act_three_complete"
    NEXT_ACT = None

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        if not self.player["a3_intro_played"]:
            # Act II's finale is on screen when Act III starts on its last ball.
            delay = INTRO_AFTER_FINALE_MS if self.player["act_finale"] else 1
            self.player["act_finale"] = 0
            self.delay.add(ms=delay, callback=self._intro, name="intro")

    def _intro(self):
        # Marked played only once it plays, so a drain before then does not lose it.
        self.player["a3_intro_played"] = 1
        self.machine.events.post("act_three_intro")

    def _act_complete(self, **kwargs):
        # Act III is the last act: the Matrix is complete for this player.
        self.player["matrix_complete"] = 1
        super()._act_complete(**kwargs)
