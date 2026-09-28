"""What the rules send to the display, checked through a mock BCP client."""
import os
import re
from unittest import TestCase
from unittest.mock import patch

from ruamel.yaml import YAML

from tests.display_test_case import DisplayTestCase
from tests.matrix_test_case import REPO_ROOT


def _widget_player_entries():
    """Yield (mode file, widget name, settings) for every widget_player entry."""
    modes = os.path.join(REPO_ROOT, "modes")
    for mode in sorted(os.listdir(modes)):
        path = os.path.join(modes, mode, "config", mode + ".yaml")
        if not os.path.exists(path):
            continue
        with open(path) as handle:
            config = YAML(typ="safe").load(handle) or {}
        for widgets in (config.get("widget_player") or {}).values():
            for name, settings in widgets.items():
                yield path, name, settings or {}


class TestDisplayAssets(TestCase):

    def test_every_widget_has_a_scene(self):
        for path, name, _ in _widget_player_entries():
            scene = os.path.join(REPO_ROOT, "gmc", "widgets", name + ".tscn")
            self.assertTrue(os.path.exists(scene), "{} plays missing widget {}".format(path, name))

    def test_every_clip_is_in_the_manifest(self):
        with open(os.path.join(REPO_ROOT, "gmc", "video", "manifest.txt")) as handle:
            listed = {line.split("#")[0].strip() for line in handle} - {""}
        for path, name, settings in _widget_player_entries():
            if name == "video_clip":
                clip = settings["tokens"]["clip"]
                self.assertIn(clip, listed, "{} plays unlisted clip {}".format(path, clip))

    def test_every_clip_expires(self):
        for path, name, settings in _widget_player_entries():
            if name == "video_clip":
                self.assertIn("expire", settings, "{}: a missing clip would never leave".format(path))

    def test_countdowns_name_their_event(self):
        for path, name, settings in _widget_player_entries():
            if name in ("countdown", "t2_countdown", "pill_choice", "doors_choice", "dyson_choice", "act_select", "game_select") and settings.get("action", "play") == "play":
                self.assertTrue(settings.get("tokens", {}).get("event"), "{}: {} has no event".format(path, name))

    def test_no_placeholder_tokens(self):
        # MPF does not substitute event arguments into widget tokens.
        for path, name, settings in _widget_player_entries():
            for value in (settings.get("tokens") or {}).values():
                self.assertIsNone(re.search(r"\([a-z_]+\)", str(value)), "{}: {}".format(path, value))


class TestDisplay(DisplayTestCase):

    def played(self, widget, context=None):
        return [(ctx, settings) for name, ctx, settings in self.widgets_played()
                if name == widget and (context is None or ctx == context)]

    def tokens(self, widget, context=None):
        return [settings.get("tokens", {}) for _, settings in self.played(widget, context)]

    def test_chapter_one_card_and_clocks(self):
        self.start()
        self.widgets_played()
        self.start_chapter(1)
        played = self.widgets_played()
        cards = [s["tokens"] for n, c, s in played if n == "chapter_card"]
        self.assertEqual("TRINITY'S ESCAPE", cards[0]["title"])
        clocks = [s for n, c, s in played if n == "countdown"]
        self.assertEqual("timer_ch1_rooftops_tick", clocks[0]["tokens"]["event"])

        for ramp in ("left_lock", "middle_loop", "right_loop"):
            self.ramp(ramp)
        updates = [s for n, c, s in self.widgets_played() if n == "countdown"]
        self.assertEqual("update", updates[-1]["action"])
        self.assertEqual("timer_ch1_phone_tick", updates[-1]["tokens"]["event"])
        self.assertEqual("250000", updates[-1]["tokens"]["value_base"])

    def test_crew_card_survives_the_chapter_stopping(self):
        self.start()
        self.start_chapter(1)
        for ramp in ("left_lock", "middle_loop", "right_loop"):
            self.ramp(ramp)
        self.sent = []
        self.enter_device("s_middle_loop_vuk")
        cards = [(c, s["tokens"]) for n, c, s in self.widgets_played() if n == "chapter_card"]
        self.assertIn(("act_one", "TRINITY"), [(c, t["title"]) for c, t in cards])
        cleared = self.contexts_cleared()
        self.assertIn("ch1_trinity_escape", cleared)
        self.assertNotIn("act_one", cleared)

    def test_blue_pill_callout_survives(self):
        self.start()
        self.start_chapter(2)
        choice = self.tokens("pill_choice")
        self.assertEqual("timer_ch2_choice_tick", choice[0]["event"])
        self.hit_and_release_switch("s_left_flipper")
        self.advance_time_and_run(1)
        banners = [(c, s["tokens"]["title"]) for n, c, s in self.widgets_played() if n == "mode_banner"]
        self.assertIn(("act_one", "THE STORY ENDS"), banners)

    def test_construct_clock_follows_the_rounds(self):
        self.start()
        self.start_chapter(3)
        self.assertEqual("ROUND 1  KUNG FU", self.tokens("countdown")[0]["label"])
        for n in range(1, 6):
            self.hit_switch_and_run("s_five_bank_{}".format(n), .1)
        updates = [s for n, c, s in self.widgets_played() if n == "countdown"]
        self.assertEqual("ROUND 2  SPARRING", updates[-1]["tokens"]["label"])

    def test_the_one_chase_clock_and_ticks(self):
        self.start()
        for event in ("ch1_completed", "ch2_completed", "ch3_completed", "ch4_completed"):
            self.post_event(event, .1)
        self.open_mission()
        self.shoot_mission()
        self.confirm_playfield()
        self.assertEqual("THE SUBWAY", self.tokens("chapter_card", "the_one")[0]["title"])
        self.mock_event("the_one_chase_tick")
        self.player()["the_one_stage"] = 1
        self.player()["the_one_progress"] = 5
        self.knock_down_popup(1, 1)
        played = self.widgets_played()
        clocks = [s["tokens"] for n, c, s in played if n == "countdown"]
        self.assertEqual("the_one_chase_tick", clocks[0]["event"])
        # The chase started on the agent hit; 4 s have passed since.
        self.advance_time_and_run(3)
        self.assertEventCalledWith("the_one_chase_tick", ticks=56)

    def test_the_one_resume_shows_its_stage(self):
        self.start()
        self.player()["the_one_lit"] = 1
        self.player()["the_one_stage"] = 2
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        clocks = self.tokens("countdown", "the_one")
        self.assertEqual("the_one_chase_tick", clocks[-1]["event"])

    def test_emp_finale_survives(self):
        self.start()
        self.player()["the_one_lit"] = 1
        self.open_mission()
        self.shoot_mission()
        self.player()["the_one_stage"] = 3
        self.player()["the_one_progress"] = 2
        self.post_event("the_one_mb_room_303", 6)
        self.ramp("left_lock")
        self.enter_device("s_platform_vuk")
        played = self.widgets_played()
        self.assertIn(("video_clip", "base"), [(n, c) for n, c, s in played if n == "video_clip" and c == "base"])
        self.assertIn("ACT I COMPLETE", [s["tokens"]["kicker"] for n, c, s in played if n == "chapter_card"])

    def test_act_select_screen(self):
        with patch("modes.act_select.code.act_select.AVAILABLE_ACTS", ("I", "II")):
            self.fill_troughs()
            self.hit_and_release_switch("s_start")
            self.advance_time_and_run(1)
            self.hit_and_release_switch("s_start")
            self.advance_time_and_run(1)
            screens = self.tokens("act_select")
            self.assertEqual("act_select_show", screens[0]["event"])
            self.assertEqual("seconds", screens[0]["arg"])


class TestActTwoDisplay(DisplayTestCase):

    def start(self):
        self.start_matrix_game(act="II")

    def played(self, widget, context=None):
        return [(ctx, settings) for name, ctx, settings in self.widgets_played()
                if name == widget and (context is None or ctx == context)]

    def test_intro_card(self):
        self.start()
        self.advance_time_and_run(1)
        cards = [s["tokens"]["title"] for n, c, s in self.widgets_played() if n == "chapter_card"]
        self.assertIn("RELOADED", cards)

    def test_ally_card_survives_the_chapter_stopping(self):
        self.start()
        self.player()["a2_chapter_next"] = 1
        self.open_mission()
        self.shoot_mission()
        self.ramp("right_loop")
        self.hit_and_release_switch("s_upper_target_1")
        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_pop_target_{}".format(n))
        self.advance_time_and_run(.5)
        self.sent = []
        self.enter_device("s_middle_loop_vuk")
        cards = [(c, s["tokens"]["title"]) for n, c, s in self.widgets_played() if n == "chapter_card"]
        self.assertIn(("act_two", "LINK"), cards)
        cleared = self.contexts_cleared()
        self.assertIn("a2_ch1_zion", cleared)
        self.assertNotIn("act_two", cleared)

    def test_architect_doors_and_finale(self):
        self.start()
        self.player()["architect_lit"] = 1
        self.player()["architect_stage"] = 3
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        choices = [s["tokens"] for n, c, s in self.widgets_played() if n == "doors_choice"]
        self.assertEqual("architect_choice_tick", choices[-1]["event"])
        self.hit_and_release_switch("s_right_loop_ramp")
        self.advance_time_and_run(.5)
        played = self.widgets_played()
        clocks = [s["tokens"] for n, c, s in played if n == "countdown"]
        self.assertEqual("architect_trinity_tick", clocks[-1]["event"])
        self.assertEqual("1000000", clocks[-1]["value_base"])
        self.player()["architect_stage"] = 5
        self.post_event("platform_gate_open", .5)
        self.enter_device("s_platform_vuk")
        played = self.widgets_played()
        self.assertIn("base", [c for n, c, s in played if n == "video_clip"])
        self.assertIn("ACT II COMPLETE", [s["tokens"]["kicker"] for n, c, s in played if n == "chapter_card"])
        self.assertPlayerVarEqual("III", "act")


class TestActThreeDisplay(DisplayTestCase):

    def start(self):
        self.start_matrix_game(act="III")

    def test_intro_card(self):
        self.start()
        self.advance_time_and_run(1)
        cards = [s["tokens"]["title"] for n, c, s in self.widgets_played() if n == "chapter_card"]
        self.assertIn("REVOLUTIONS", cards)

    def test_defender_card_survives_the_chapter_stopping(self):
        self.start()
        self.player()["a3_chapter_next"] = 4
        self.open_mission()
        self.shoot_mission()
        for ramp in ("left_lock", "middle_loop", "right_loop", "backboard"):
            self.ramp(ramp)
        self.sent = []
        self.enter_device("s_middle_loop_vuk")
        played = self.widgets_played()
        cards = [(c, s["tokens"]["title"]) for n, c, s in played if n == "chapter_card"]
        self.assertIn(("act_three", "ROLAND"), cards)
        self.assertIn(("video_clip", "act_three"), [(n, c) for n, c, s in played if n == "video_clip"])
        self.assertNotIn("act_three", self.contexts_cleared())

    def test_matrix_finale_survives(self):
        self.start()
        self.player()["machine_city_lit"] = 1
        self.player()["machine_city_stage"] = 4
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.confirm_playfield()
        self.sent = []
        self.enter_device("s_middle_loop_vuk")
        played = self.widgets_played()
        self.assertIn("base", [c for n, c, s in played if n == "video_clip"])
        self.assertIn("THE MATRIX COMPLETE", [s["tokens"]["goal"] for n, c, s in played if n == "chapter_card"])
