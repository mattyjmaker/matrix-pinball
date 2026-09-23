# This Machine: Matrix Pinball Setup Notes

This is the production cabinet PC, and it is also used for development. Set up on 2026-09-19.

## Hardware and OS
- Ubuntu 26.04.1 LTS, x86_64, 8 cores, 30 GB RAM, 915 GB NVMe.
- GPU: NVIDIA RTX 2060 Mobile (driver 595.91) plus Intel Iris Xe. Godot uses **Vulkan on the NVIDIA GPU** (Mobile renderer).
- Pinball controller: FAST Neuron, appearing as `/dev/ttyACM0`, `/dev/ttyACM1` and `/dev/ttyACM2` (owned by group `dialout`).

### Boards installed (user, 2026-09-20)
- **Backbox:** the FAST Smart Power Filter Board (FP-PWR-0007, the "big capacitor board") + the Neuron.
- **Playfield:** I/O 1616 at the back, the FAST Playfield Interchange Board (FP-PWR-0030, passive — no MPF config needed), the I/O 3208 (flippers and the lower third are primarily wired to it), and the second I/O 1616 in the middle.
- **Cabinet:** the Cabinet I/O (FP-CAB-0001) **is installed, but not yet wired** (user, 2026-09-20).

See 09-parts-inventory.md for the capacity analysis. The 3208 is confirmed real, which resolves an earlier open question.

### Physical build status (user, 2026-09-20)

Still to build:
- **Upper playfield** — still needs CNC cutting, then building. This is the "Real World" mini-playfield (standups ×3 + a mini left flipper; see 09-parts-inventory.md). Note that `Drawings/Playfield/` in Dropbox has `Playfield v79.dxf`, the backwall and the lower third, plus an upper-right-flipper lane guide, but **no upper-playfield DXF is listed** in 10-dropbox-design-files.md — that file may still need drawing.
- **Wiring** — not finished.
- **Ramps and wireforms** (ball paths) — not installed.

What this means for the MPF side:
- Ball paths aren't final, so `ball_devices:`, opto placement and eject targets can't be locked down yet. Coil tuning in particular should wait: ramp shots need re-tuning once the ramps are physically in (see 06-tutorials-cookbook-finalization.md, "Revisit it once ramps are installed").
- The upper playfield's switches and its flipper driver aren't wired, so the ~6-input shortfall in the capacity estimate isn't yet real — but it will be once the upper playfield lands. Count it in before deciding whether another 1616 is needed.
- Unfinished wiring is why the placeholder switch numbers below can't all be replaced yet. Note the split: the flipper **coils** and the lower third are on the 3208 and wired, so those can be numbered now — while `s_left_flipper`, `s_right_flipper` and `s_start` are `cab-…` **switches** on the Cabinet I/O. Those three now carry FAST's recommended numbers (`cab-8`, `cab-16`, `cab-10`) rather than placeholders, but they stay unconfirmed until the cabinet is wired and switch-tested.

### Wiring colour convention (user, 2026-09-22)

This machine's own convention. Recorded as user-provided; it has not been
cross-checked against FAST's published wiring guides, which are at
fastpinball.com/wiring/neuron.

| Circuit | Leg | Colour |
| --- | --- | --- |
| Switches (cabinet buttons, playfield switches) | Feed out of the board input | Orange |
| Switches | Return back to the board | Purple |
| Solenoids, coils and similar drivers | Negative | Black |
| Solenoids, coils and similar drivers | Positive run | Blue |

So a cabinet flipper button is orange out to the button and purple back, and a
flipper coil is blue on the positive run and black on the negative.

Not yet recorded, and worth adding here as they are decided: LED and lamp
wiring, opto power and signal, ground and earth bonding, and whether any
sub-loom uses a different scheme.

### Audio wiring (planned, 2026-09-23)

Current chain (user): NUC headphone out -> Fosi MC101 RCA line input -> the
donated car speakers. To add: the Kenwood KFC-WPS1200F 12" sub, driven by the
Blaupunkt AMP1501.

Neither the audio signal nor the sub amp's power goes through the FAST boards.
The Cabinet I/O (FP-CAB-0001) only carries switch inputs and low-side drivers.
The Smart Power Filter Board's 12 V headers are 0.156" parts rated 7 A per pin
(FAST, "Smart Power Filter Board Wiring"), while the AMP1501 carries
2 x 20 A fuses. FAST's own audio option is the FAST Audio Interface board
(12 V, 4 ohm main and sub amps, software volume); it is not owned.

Published specs (retailer and manufacturer listings, not measured here):

| Item | Spec |
| --- | --- |
| Kenwood KFC-WPS1200F | Single 4 ohm voice coil, 350 W RMS, 1400 W peak, 91 dB, shallow mount |
| Fosi MC101 | Stereo only, 2 x TPA3116, 2 x 100 W at 4 ohm. RCA line in and Bluetooth. 3.5 mm sub pre-out: full range (no low-pass filter), follows the master volume. No sub amplifier channel |
| Blaupunkt AMP1501 | Class D, 563 W RMS at 4 ohm, 11 to 16 V DC, 2 x 20 A fuses, RCA (low-level) input, 10 to 300 Hz |

Because the MC101 has no sub amplifier, the sub needs the AMP1501:

- Signal: MC101 3.5 mm sub pre-out -> 3.5 mm to 2 x RCA lead -> AMP1501 RCA
  inputs. The pre-out is unfiltered, so the AMP1501's low-pass filter is the
  crossover (start at about 80 Hz).
- Power: its own mains-to-12 V supply, not the filter board. Size it for
  sustained output, because the sub is used for effect build-ups that hold
  near full power for seconds, not only for music peaks: 350 W to the sub is
  roughly 440 W in (assuming about 80% efficiency), about 32 A at 13.8 V. Use a
  500 to 600 W (40 to 50 A) supply trimmed to 13.8 V, 8 AWG, and a 40 to 50 A
  fuse near the supply. Link the amp's `REM` terminal to its `+12V` terminal
  so it powers up with the supply. Earth the supply to mains earth.
- Gain: the amp can exceed the sub's 350 W RMS, so the amp's gain setting is
  what protects the sub.

Effects use (user, 2026-09-23): the sub is also for tension build-ups that
shake the cabinet, not only background bass. Consequences:

- The AMP1501 is the right amp for this. A BT30D Pro on its 48 V 5 A brick
  (240 W across all three channels) cannot sustain a long build-up.
- Bolt the sub rigidly to the cabinet floor, firing down through a grilled
  cutout, so the cabinet structure is driven.
- Author build-ups as rumble in roughly the 30 to 60 Hz range, high-passed
  at about 25 Hz in the audio file. The Kenwood is rated to 30 Hz, and
  whether the AMP1501 has a subsonic filter is unknown.
- Set the AMP1501 gain with the loudest build-up, not with music.
- The MC101 feeds the car speakers full range with no high-pass, so turn its
  bass control down and check the speakers do not bottom out on build-ups.
- No bus changes are needed: the build-ups are ordinary sounds on the
  `effects` bus, and the AMP1501 low-pass sends their low end to the sub.
- Pair build-ups with the JJP shaker motor (PBL-100-0092-00, owned) on a
  Cabinet I/O driver, run as a coil with a low `default_hold_power` from a
  show (see 04-game-logic-and-mechs.md, "Shakers"). `shakers:` needs the
  FAST EXP-1313, which is not owned. The shaker's voltage, current and
  diode are not yet checked.

Open items:
- [ ] 09-parts-inventory.md lists a Fosi BT30D Pro, which has a built-in 4 ohm
      sub channel. Confirm whether it is actually owned. It would suit music
      bass, but not sustained effect build-ups, so the AMP1501 stays.
- [ ] Check the JJP shaker's rated voltage, current and flyback diode before
      assigning it a Cabinet I/O driver.
- [ ] Decide the sub's mounting position and enclosure in the cabinet.

## Installed software

| What | Version | Location |
|---|---|---|
| Python | 3.14.4 (system) | `/usr/bin/python3` |
| MPF | 0.80.0 (pinned) | venv `~/.mpfenv/matrix` |
| MPF Monitor | 1.0.0.dev1 (+ PyQt6 6.11) | same venv |
| Godot editor | 4.6.3-stable installed; **project now targets 4.7.2** | `~/.local/opt/godot/`, symlinked as `~/.local/bin/godot` |
| Godot export templates | 4.6.3 (Linux x86_64 only) | `~/.local/share/godot/export_templates/4.6.3.stable/` |
| GMC addon | 1.0.0 | `~/matrix-pinball/gmc/addons/mpf-gmc/` (inside the project) |
| Game project | `mattyjmaker/matrix-pinball` | `~/matrix-pinball` |

> Don't run `pip install mpf --pre`, because that now installs 0.81 dev builds. To upgrade, use
> `pip install "mpf==0.80.*"` with the venv active. MPF and GMC versions must match (MPF 0.80.0 requires GMC 1.0.0).

## Commands

| Command | Does |
|---|---|
| `pinball` | MPF + Godot window, **virtual hardware** (smart_virtual). Switches come from the keyboard (see `gmc/gmc.cfg`). |
| `pinball hw` | MPF + Godot on the **real FAST hardware**. |
| `pinball -X -v` | Any `mpf` flags, passed through. |
| `pinball-editor` | Open the GMC project in the Godot editor. |
| `pinball-monitor` | MPF Monitor, which connects to a running MPF on port 5051. |
| `mpfenv` | Shell alias: activate the venv and `cd ~/matrix-pinball`. After that, `mpf ...` commands work directly. |

There are also desktop launchers: "Matrix Pinball (virtual)" and "Matrix Pinball – Godot Editor".

Keyboard (virtual mode, from `gmc/gmc.cfg`):
- `1` start
- `a`/`d` flippers
- `z x c v b n m k` toggle trough switches 1–8
- `p` toggle the plunger lane
- `0`/`9` outlanes
- `8`/`7` inlanes

Logs go to `~/matrix-pinball/logs/`.

## Changes made to the repo (uncommitted, for review)
1. `config/config.yaml`: **removed the `keyboard:` section**. MPF 0.80 rejects it with `CFE-ConfigProcessor-3`. The trough and plunger toggle keys were moved to `gmc/gmc.cfg`.
2. `gmc/addons/mpf-gmc`: **upgraded GMC 0.1.1 → 1.0.0**, because MPF 0.80.0 refuses to connect to older GMC versions.
3. Godot 4.6 rewrote some `.import` files and added `.uid` files. This is normal when upgrading Godot from 4.3.
4. LFS assets (fonts, PNG, videos) were fetched directly from GitHub, because git-lfs wasn't installed yet.

## Verified
- MPF 0.80.0 and GMC 1.0.0 connect over BCP on port 5050, and the welcome and attract slides play with no errors.
- A simulated game works: start → base mode → trough ejects to the plunger → an inlane scores 100.

## Still to do
- [ ] Install system packages. This needs sudo, so the user runs it:
  `sudo apt update && sudo apt install -y git git-lfs python3.14-venv && sudo usermod -aG dialout,tty pinball`, then log out and back in.
- [ ] Turn `~/matrix-pinball` into a real git clone (with git-lfs) and commit the changes above.
- [ ] Replace placeholder switch numbers for `s_trough1`, `s_trough_jam` and `s_plunger`.
      These are still commented out in `config/config.yaml`.
- [ ] Confirm the cabinet button numbers. `s_left_flipper` (`cab-8`), `s_start`
      (`cab-10`) and `s_right_flipper` (`cab-16`) are now in the config with the
      `flippers:` section enabled, but the numbers are FAST's recommended
      defaults, not measured on this machine. MPF range-checks them against the
      24 inputs the board reports and nothing more, so a wrong-but-in-range
      number reads the wrong input silently. Verify in the service-mode switch
      test once the board is wired.
- [ ] **Add the second 1616 to `io_loop:` in `config/config.yaml`.** The config declares only three boards (`cab`, `top16`, `bottom32`) but two 1616s are installed. Until the fourth entry exists — with `order:` values matching the real daisy-chain order out of the Neuron — switch and driver numbers will land on the wrong boards.
- [ ] Run `mpf hardware scan` to confirm the board models and loop order match the config (`FP-CAB-0001`, `FP-I/O-1616` ×2, `FP-I/O-3208`, `FP-EXP-2000` + `FP-PWR-0007`). This is the fastest way to get the true `order:` values.
- [ ] Wire the Cabinet I/O (FP-CAB-0001). It's mounted but unwired. The config
      now assumes the side flipper buttons and start button land on the
      left-side (`cab-8` to `cab-15`) and right-side (`cab-16` to `cab-23`)
      headers; the coin door header J4 is `cab-0` to `cab-7`. The board's 8
      drivers (`cab-0` to `cab-7`) are still unconfigured, so no knocker or
      button lamps yet.
- [ ] Check whether the Cabinet I/O's **NET cable** is plugged into the I/O loop. If it isn't, it won't appear in `mpf hardware scan` and the config's `order: 1` for `cab` is wrong — every other board's order shifts.
- [ ] **Install Godot 4.7.2 on this machine.** `project.godot` is now tagged
      `4.7`, but the editor here is still 4.6.3, which will warn that the
      project was made with a newer version. Download 4.7.2 from
      godotengine.org, replace `~/.local/opt/godot/`, keep the
      `~/.local/bin/godot` symlink pointing at it, and fetch the matching
      4.7.2 export templates before building a production export.
      Godot 4.7.2 was verified against this project in a container: the import
      is clean, GMC 1.0.0 loads, and all four slides render unchanged.
- [ ] No LED expansion boards are wired or configured yet (FP-EXP-0081 and FP-EXP-0071 are owned). Needed before any playfield RGB inserts or servos work.
- [ ] Decide the plunger behaviour. `bd_plunger` has `eject_coil: c_auto_plunge` plus `mechanical_eject: true` but no `player_controlled_eject_event`, so a ball in the lane waits for a manual plunge. `eject_timeouts: 15s` is long; the docs suggest 3–5 s.
- [ ] Modes `welcome`, `plunge_ready` and `skillshot` exist but aren't listed under `modes:` and have no start events. `skillshot.yaml` is empty.
- [ ] `slide_player` for attract is defined in both `config.yaml` and `modes/attract`, so it is duplicated.
- [ ] Later, for production: export the Godot project to a binary, build the MPF production bundle, and set up auto-start on boot.
