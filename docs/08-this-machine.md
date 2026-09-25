# This Machine: Matrix Pinball Setup Notes

This is the production cabinet PC, and it is also used for development. Set up on 2026-09-19.

## Hardware and OS
- Ubuntu 26.04.1 LTS, x86_64, 8 cores, 30 GB RAM, 915 GB NVMe.
- GPU: NVIDIA RTX 2060 Mobile (driver 595.91) plus Intel Iris Xe. Godot uses **Vulkan on the NVIDIA GPU** (Mobile renderer).
- Pinball controller: FAST Neuron, appearing as `/dev/ttyACM0`, `/dev/ttyACM1` and `/dev/ttyACM2` (owned by group `dialout`).

### Boards installed (user, 2026-09-20)
- **Backbox:** the FAST Smart Power Filter Board (FP-PWR-0007, the "big capacitor board") + the Neuron.
- **Playfield:** I/O 1616 at the back, the FAST Playfield Interchange Board (FP-PWR-0030, passive — no MPF config needed), the I/O 3208 (flippers and the lower third are primarily wired to it), and the second I/O 1616 in the middle.
- **Cabinet:** the Cabinet I/O **is installed, but not yet wired** (user, 2026-09-20). Its part number has not been read off the board. FAST's public Cabinet I/O is the FP-I/O-0024, and the config now uses that model; the repo previously said FP-CAB-0001. See 12-fast-boards.md, section 2, check 1.

Per-board pinouts, FAST's wiring rules and the checks still to do on the machine are in 12-fast-boards.md.

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

This machine's own convention, recorded as user-provided. It was checked
against FAST's wiring standard on 2026-09-25 (12-fast-boards.md, section 4).

| Circuit | Leg | Colour |
| --- | --- | --- |
| Switches (cabinet buttons, playfield switches) | Feed out of the board input | Orange |
| Switches | Return back to the board | Purple |
| Solenoids, coils and similar drivers | Negative | Black |
| Solenoids, coils and similar drivers | Positive run | Blue |

So a cabinet flipper button is orange out to the button and purple back, and a
flipper coil is blue on the positive run and black on the negative.

Compared with FAST's standard (Official, fastpinball.com/wiring/standards):
- Orange, purple and blue match.
- Black on the coil negative does not match. FAST uses grey or white for the
  wire from the coil to the I/O board driver pin, and keeps black for ground
  returns. That includes the 48 V toxic ground from each I/O board's GND pins
  back to the Playfield Interchange Board.
- Using black for driver lines makes a control line look like a ground
  return. Decide whether to use grey or white for the wiring still to do.
- FAST's other colours: yellow for 12 V, red for 5 V, white for LED data,
  and black for all DC ground returns.

Not yet recorded, and worth adding here as they are decided: LED and lamp
wiring, opto power and signal, ground and earth bonding, and whether any
sub-loom uses a different scheme.

### Cabinet flipper opto boards (user, 2026-09-25; silkscreen read 2026-09-25)

Two FAST **FP-SWI-7083-1** "OPTO FLIPPER SW" boards are installed in the
cabinet, one on each side. The part number comes from a photo of the board's
silkscreen (user-provided, 2026-09-25). It was previously recorded here as
FP-SWI-7003-1, which was a misreading. FAST's part number index lists no
FP-SWI boards at all (Official, checked 2026-09-25), so the board is still
undocumented by FAST. Its full details are in 12-fast-boards.md, section 3.9.

From the silkscreen (user-provided photo):
- **Two optos per board** (OP1, OP2). The button's actuator carries two flags,
  one through each opto, so each board gives two switch outputs, SW1 and SW2.
  Which output trips first on a press is not known yet.
- **J1** is a 7-pin white header. Pin 1 is marked with a triangle.

  | J1 pin | Signal |
  | --- | --- |
  | 1 | SW1 |
  | 2 | SW2 |
  | 3 | GND |
  | 4 | GND |
  | 5 | KEY |
  | 6 | 12V |
  | 7 | 12V |

- There is also an unpopulated 4-pad alternative (SW1, SW2, 12V, GND) and two
  test points (IN1, IN2).
- Blocker: no matching housings. The header's pitch and family are not
  confirmed. Measure the pin pitch and check whether pin 5 is fitted (see
  12-fast-boards.md, section 3.9).

Planned wiring, one board per Cabinet I/O side header (4 wires):

| Opto board J1 | Cabinet I/O left (J1) | Cabinet I/O right (J9) |
| --- | --- | --- |
| 1 SW1 | pin 1, `cab-8` | pin 1, `cab-16` |
| 2 SW2 | pin 2, `cab-9` | pin 2, `cab-17` |
| 3 or 4 GND | pin 9, G | pin 9, G |
| 6 or 7 12V | pin 13, 12 V | pin 13, 12 V |

- This matches FAST's recommended cabinet numbering (flippers on `cab-8/9` and
  `cab-16/17`), and keeps `s_left_flipper` (`cab-8`) and `s_right_flipper`
  (`cab-16`) as configured, provided SW1 is the first stage. If SW2 trips
  first, swap the two wires or change the numbers.
- The board's GND is both its supply return and the reference for its
  switch outputs, so it must share ground with the switch inputs. Taking
  12 V and ground from the same header as the inputs does that with no
  question about separate grounds. FAST's guide suggests J11 for opto power
  instead. FAST publishes no current rating for the side header's 12 V and G
  pins (Unverified), so measure the board's current draw on the bench first.
- The start button (`cab-10`, left header pin 3) also needs pin 9 (G). The
  header has one G pin, so the start button's purple and the opto board's
  GND share it (two wires in one crimp, or a splice).

Bench test before connecting to the Cabinet I/O (output type is Unverified):
1. Power one board from a 12 V bench supply on J1 pins 6 and 3.
2. Measure the current draw.
3. Measure SW1 and SW2 to GND with nothing else connected, button released
   and pressed. An output that switches between open (no voltage) and near
   0 V is an open-collector output, which suits a FAST switch input. An output
   that sits at about 12 V is driven, and must not go to a switch input until
   FAST confirms it is safe.
4. Note which output is active when released and which when pressed. If an
   output is active with the button released (like a plain opto), set
   `type: NC` on that switch in MPF.

- Fallback: the owned Stern 500-6890-01 leaf switches wire straight to the
  Cabinet I/O headers with no board and need no config change.

### Audio wiring (decided 2026-09-23, not yet installed)

Current chain (user): NUC headphone out -> Fosi MC101 RCA line input -> the
donated car speakers. To add: the Kenwood KFC-WPS1200F 12" sub, driven by the
Blaupunkt AMP1501.

Neither the audio signal nor the sub amp's power goes through the FAST boards.
The Cabinet I/O only carries switch inputs and low-side drivers.
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
  roughly 440 W in (assuming about 80% efficiency), about 33 A at 13.2 V.
  Mains stays in the backbox (user's design goal), so the supply goes in the
  backbox and only 12 V DC runs down to the amp in the cabinet. Chosen
  supply (user, 2026-09-23, confirmed to fit the backbox): Mean Well
  RSP-500-12 (12 V, 41.7 A, fan-cooled, active PFC, universal 85 to 264 V AC
  input, 230 x 127 x 40.5 mm, 1.3 kg, output adjustable 10.8 to 13.2 V; same
  family as the backbox RSP-500-48). Set the output to 13.2 V. Chosen over
  the fanless UHP-500-12 (232 x 81 x 31 mm) because the fan holds full output
  in the enclosed backbox. Keep its fan intake and exhaust clear. Feed its
  mains input from the same switched, fused split as the other two supplies,
  and check that the existing mains fuse suits the added load. Fuse the +V
  lead within about 300 mm of the supply (50 A, MIDI, ANL or maxi blade), run
  8 AWG pure copper (not CCA) down, and put a 50 A
  connector (e.g. Anderson SB50) at the backbox/cabinet join so the backbox
  can still be separated. Neither backbox Mean Well suits it: the FAST bundle
  pair is an RSP-500-48 (wrong voltage; the amp takes 11 to 16 V) and an
  LRS-150-12 (12.5 A, and it feeds the controller's 12 V rail). The installed
  models are not yet confirmed from their labels. Link the amp's `REM` terminal to its `+12V` terminal
  so it powers up with the supply. Earth the supply to mains earth.
- Gain: the amp can exceed the sub's 350 W RMS, so the amp's gain setting is
  what protects the sub.

Rejected alternative (user chose a dedicated 12 V supply, 2026-09-23): an amp powered from the existing backbox
RSP-500-48 (10.5 A) instead of a new 12 V supply. The LRS-150-12 is too small
for any useful sub power. The candidate is a Fosi BT30D Pro, which takes
24 to 48 V (only units labelled "DC INPUT 24~48V"; units labelled 19~36V
must not get 48 V), has a sub low-pass and sub level control, and would
replace both the MC101 and the AMP1501. Fosi says it needs active cooling at
48 V. Sustained build-up draw is roughly 6 A at 48 V (estimate), which leaves
about 4.5 A for coils during a build-up. Risks, not yet tested: weaker
flippers during build-ups, coil clicks in the audio, the Smart Power Filter
Board's 48 V over-current cut-out also muting the sub, and a ground loop via
the NUC. Feed it from a fused 48 V output of the filter board, not upstream of
it. Test by playing the loudest build-up while hammering the flippers. If it
fails, the Fosi 48 V brick in the backbox with 48 V DC run down (about 6 A,
16 AWG) is the fallback. The Fosi V3 Mono (48 V, 240 W at 4 ohm) was
rejected because it has no low-pass and the MC101 pre-out is unfiltered.

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
- Conflict: the Cabinet I/O has one high-current driver (driver 7, D1 on J2),
  and the knocker is also planned for it. Its other outputs are
  current-limited LED drivers (L0 to L5) and logic outputs (D5, D6), which
  cannot run a motor by FAST's ratings. FAST's shaker guide says a regular
  driver works "with caveats around the snubber" and recommends the EXP-1313.
  See 12-fast-boards.md, section 5, finding 3.

Open items:
- [x] Order the Mean Well RSP-500-12 and the 50 A fuse (user, 2026-09-23).
- [ ] Buy the rest: 8 mm² twin-core tinned OFC cable (sold per metre; one run
      carries both +V and -V, so buy the route length plus about 0.5 m),
      a genuine Anderson SB50 pair with 8 AWG contacts, 8 AWG ferrules for
      the amp end, short 12 AWG leads with ring terminals and a small -V
      junction block for the supply end, a hex crimp tool, heatshrink, a
      grommet and cable clips, a 3.5 mm to 2 x RCA lead, and a short
      18 to 22 AWG REM jumper (not blue, which this machine uses for coil
      positive runs).
- [ ] Mount the RSP-500-12 in the backbox with its fan clear, and print a
      mount like the existing LRS-150 mounts if needed.
- [ ] Check the existing mains fuse rating (and slow-blow type) against the
      third supply's added load.
- [ ] Read the labels on the two existing backbox Mean Wells to confirm they
      are the RSP-500-48 and LRS-150-12.
- [ ] Decide which device gets the Cabinet I/O's only high-current driver
      (`cab-7`): the knocker or the shaker. The other needs an FP-EXP-1313
      (shaker) or a spare playfield I/O driver run to the cabinet.
- [ ] Check the JJP shaker's rated voltage, current and flyback diode before
      assigning it a driver. It is installed in the cabinet, not
      yet wired (user, 2026-09-25). Retailers list the replacement motor for
      JJP shaker kits (041-5029-04) as 12 V DC, 3100 RPM; its current is not
      published, so read the fitted motor's label or measure its winding
      resistance (stall current is roughly 12 V / R). Planned wiring: motor +
      to Cabinet I/O J11 (SHAKER PWR, 12 V), motor - to driver 7 (J2 D1) if
      the shaker gets it,
      diode across the motor with the band to +12 V. The flipper optos take
      12 V from the side switch headers, not J11 (see "Cabinet flipper opto
      boards"). Still run the shaker hard once while watching the flipper
      buttons in the switch test, since both likely come from the board's J3
      12 V input (unverified).
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
- The Act I playfield keys are listed in the README, section "Keyboard".

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
- [ ] **Load 7 balls.** `balls_installed` is now 7 for the Act I multiballs
      (docs/11-rules-act-1.md, section 2). With fewer balls in the machine,
      attract mode ball-searches constantly.
- [ ] **First boot of the Act I rules on the FAST hardware.** `hardware:
      platform:` is now `fast, virtual`, with the unwired features on the
      virtual platform. This has only been run on smart_virtual (the tests and
      `mpf -X`). Run `pinball hw` and check the log for errors before playing.
- [ ] As each playfield feature is wired, move it out of
      `config/playfield_pending.yaml` (see that file's header) and check the
      `TODO` assumptions there: Trinity lock positions, Ammo Lock capacity,
      Sentinel gate type, and which ramps are left and right.
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
- [ ] **Do the board checks in 12-fast-boards.md, section 2.** The most
      important are the Cabinet I/O part number (MPF 0.80 aborts if the
      `model:` does not match the board), the physical loop order, and the
      Neuron firmware version (v2.13 or newer is needed for the Cabinet I/O).
- [ ] **48 V enable.** The Smart Power Filter Board's software 48 V enable is
      not released (FAST, as fetched 2026-09-25), so 48 V flows only while its
      J8 (ENA IN) pins 1 and 3 are closed. Wire the coin door interlock to J8
      (and optionally J9 ENA OUT to a Cabinet I/O switch input), or jumper J8
      for testing.
- [ ] **Add the second 1616 to `io_loop:` in `config/config.yaml`.** The config declares only three boards (`cab`, `top16`, `bottom32`) but two 1616s are installed. Until the fourth entry exists — with `order:` values matching the real daisy-chain order out of the Neuron — switch and driver numbers will land on the wrong boards.
- [ ] Run `mpf hardware scan` to confirm the board models and loop order match the config (`FP-I/O-0024`, `FP-I/O-1616` ×2, `FP-I/O-3208`, `FP-EXP-2000` + `FP-PWR-0007`). This is the fastest way to get the true `order:` values.
- [ ] Wire the Cabinet I/O (FP-I/O-0024 expected). It's mounted but unwired.
      Pinouts are in 12-fast-boards.md, section 3.6. None of its 13-pin
      headers are keyed. The config
      now assumes the side flipper buttons and start button land on the
      left-side (`cab-8` to `cab-15`) and right-side (`cab-16` to `cab-23`)
      headers; the coin door header J4 is `cab-0` to `cab-7`. The board's 8
      drivers (`cab-0` to `cab-7`) are still unconfigured, so no knocker or
      button lamps yet.
- [ ] Fit the knocker in the cabinet (user wants it there, 2026-09-25): the
      owned WPC assembly B-10686-1 with an AE-23-800 coil. Per FAST's Cabinet
      I/O pages, the board takes 12 V and 48 V on J3 (12 V, G, TG, H2) from
      the Smart Power Filter Board's J10 (4-pin). The knocker goes on J2
      (D1, key, TG, H2): H2 to the coil lug on the diode band side, D1 to the
      other lug. D1 is software driver 7 (`cab-7`). FAST accepts a 1N4001,
      1N4004 or 1N4007 diode; this repo uses a 1N4004 or 1N4007 because a
      1N4001 is rated only 50 V. Check that the assembly's coil
      already has one. MPF 0.80 has no `knockers:` device (not in its
      `config_spec.yaml`), so the knocker is a plain entry under `coils:`
      fired by `coil_player`. Nothing in the Act I rules fires it yet.
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
