"""Act II controller: the story order, the Mission scoop and the ALLIES roster.

The same sequencing as Act I (modes/act_one/code/act_one.py), with Act II's
chapters, multiballs, roster and wizard:

- Chapters play in film order from the mode scoop (the Mission scoop). After
  chapter 4, the scoop replays the first chapter not yet completed.
- One multiball at a time, through the player's `mb_pending` queue.
- Each completed chapter or multiball allies one name. Enough names (the
  `architect_threshold` setting) light the Architect, which the scoop then
  starts in preference to a chapter replay.
- The Architect survives ball end: `architect_stage` stays set, and it
  restarts on the player's next ball until the Sentinels are stopped, which
  moves the player to Act III.

Act II starts on the ball the EMP ends Act I, as well as on every ball while
`act` is II. See docs/14-rules-act-2.md.
"""
from modes.act_one.code.act_one import ActOne

# chapter number: (mode that starts it, roster variable it lights, title)
CHAPTERS = {
    1: ("a2_ch1_zion", "allies_link", "ZION"),
    2: ("a2_ch2_seraph", "allies_seraph", "THE ORACLE"),
    3: ("a2_ch3_merovingian", "allies_persephone", "THE MEROVINGIAN"),
    4: ("a2_ch4_garage", "allies_keymaker", "THE FREEWAY"),
}

# Every mode belonging to a chapter, for "is a chapter running".
CHAPTER_MODES = {
    1: ("a2_ch1_zion",),
    2: ("a2_ch2_seraph", "a2_ch2_brawl_mb"),
    3: ("a2_ch3_merovingian",),
    4: ("a2_ch4_garage", "a2_ch4_freeway_mb"),
}

# Multiball name: the mode that runs it. Only one may run at a time.
MULTIBALLS = {
    "logos": "logos_mb",
    "hunt": "hunt_mb",
    "brawl": "a2_ch2_brawl_mb",
    "freeway": "a2_ch4_freeway_mb",
    "architect": "the_architect",
}

# What each completion event allies.
ROSTER = {
    "a2_ch1_completed": "allies_link",
    "a2_ch2_completed": "allies_seraph",
    "a2_ch3_completed": "allies_persephone",
    "a2_ch4_completed": "allies_keymaker",
    "logos_mb_completed": "allies_niobe",
    "hunt_mb_completed": "allies_ghost",
}

# Chapter number: (the mode for its first phase, the multiball that follows).
CHAPTER_PHASES = {
    2: ("a2_ch2_seraph", "brawl"),
    4: ("a2_ch4_garage", "freeway"),
}

# The Act II intro waits this long when Act II starts on the EMP's ball, so
# it does not play over the EMP clip (base.yaml, 8 s).
INTRO_AFTER_FINALE_MS = 8000


class ActTwo(ActOne):

    """Sequencing and bookkeeping for Act II."""

    __slots__ = []

    CHAPTERS = CHAPTERS
    CHAPTER_MODES = CHAPTER_MODES
    MULTIBALLS = MULTIBALLS
    ROSTER = ROSTER
    CHAPTER_PHASES = CHAPTER_PHASES
    CHAPTER_KEEPS_BALL = None
    CHAPTER_EVENT = "a2_ch{}"
    CHAPTER_NEXT = "a2_chapter_next"
    SCOOP_HOLD = "a2_scoop_hold"
    ROSTER_COUNT = "allies_count"
    ROSTER_EVENT = "ally_joined"
    ROSTER_ARG = "ally"
    ROSTER_GOAL = "FIND YOUR ALLIES"
    WIZARD = "architect"
    WIZARD_TITLE = "THE ARCHITECT"
    WIZARD_THRESHOLD = "architect_threshold"
    WIZARD_DONE = "architect_sentinels_stopped"
    FEATURES = "act_two_features"
    COMPLETE = "act_two_complete"
    NEXT_ACT = "III"

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        if not self.player["a2_intro_played"]:
            # Act I's finale is on screen when Act II starts on the EMP's ball.
            delay = INTRO_AFTER_FINALE_MS if self.player["act_finale"] else 1
            self.player["act_finale"] = 0
            self.delay.add(ms=delay, callback=self._intro, name="intro")

    def _intro(self):
        # Marked played only once it plays, so a drain before then does not lose it.
        self.player["a2_intro_played"] = 1
        self.machine.events.post("act_two_intro")
