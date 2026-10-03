# This Machine: Matrix Pinball Setup Notes

This is the production cabinet PC, and it is also used for development. Set up on 2026-09-19.

## Hardware and OS
- Ubuntu 26.04.1 LTS, x86_64, 8 cores, 30 GB RAM, 915 GB NVMe.
- GPU: NVIDIA RTX 2060 Mobile (driver 595.91) plus Intel Iris Xe. Godot uses **Vulkan on the NVIDIA GPU** (Mobile renderer).
- Pinball controller: FAST Neuron, appearing as `/dev/ttyACM0`, `/dev/ttyACM1` and `/dev/ttyACM2` (owned by group `dialout`).

### Boards installed (user, 2026-09-20)
- **Backbox:** the FAST Smart Power Filter Board (FP-PWR-0007, the "big capacitor board") + the Neuron.
- **Playfield:** I/O 1616 at the back, the FAST Playfield Interchange Board (FP-PWR-0030, passive — no MPF config needed), the I/O 3208 (flippers and the lower third are primarily wired to it), and the second I/O 1616 in the middle.
- **Cabinet:** the Cabinet I/O **is installed, but not yet wired** (user, 2026-09-20). Its silkscreen reads **FP-I/O-0024-5** (user photo, 2026-09-25), which confirms the config's `FP-I/O-0024`; the repo previously said FP-CAB-0001. In the same photo neither RJ45 jack has a cable, so the board is not yet in the I/O loop. Revision -5 is newer than FAST's documentation (-4); see 13-fast-boards.md, section 3.6.

Per-board pinouts, FAST's wiring rules and the checks still to do on the machine are in 13-fast-boards.md.

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
against FAST's wiring standard on 2026-09-25 (13-fast-boards.md, section 4).

| Circuit | Leg | Colour |
| --- | --- | --- |
| Switches (cabinet buttons, playfield switches) | Feed out of the board input | Orange |
| Switches | Return back to the board | Purple |
| Solenoids, coils and similar drivers | Negative (to the driver pin) | Black |
| Solenoids, coils and similar drivers | Positive run | Blue (48 V only) |

So a cabinet flipper button is orange out to the button and purple back, and a
flipper coil is blue on the positive run and black on the negative.

Decision (user, 2026-09-26): keep this machine's own convention for driver
lines (black), to match the existing wiring, rather than FAST's grey/white.
- The positive colour follows the voltage, not the device: blue means 48 V
  only. A 12 V load on a driver (the shaker) has a yellow positive and a
  black driver wire.
- Exception already installed: the start lamp's return to CABINET A L2 is
  white 22 AWG (wired 2026-09-26 when white was advised). It works as is;
  change it to black only if you want the harness uniform.
- Since black also means ground returns in FAST's scheme, label driver wires
  where they could be confused with a ground (for example on 0.156" driver
  headers next to the GND pins).

Compared with FAST's standard (Official, fastpinball.com/wiring/standards):
- Orange, purple and blue match.
- Black on the coil negative does not match. FAST uses grey or white for the
  wire from the coil to the I/O board driver pin, and keeps black for ground
  returns. That includes the 48 V toxic ground from each I/O board's GND pins
  back to the Playfield Interchange Board.
- Using black for driver lines makes a control line look like a ground
  return. The user chose to keep black for consistency (2026-09-26); label
  where it matters.
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
undocumented by FAST. Its full details are in 13-fast-boards.md, section 3.9.

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
  13-fast-boards.md, section 3.9).
- Plan (user, 2026-09-28): use the two 8-way female housings on hand as
  7-way, housing position 1 on J1 pin 1 and position 8 left empty and
  overhanging past pin 7. Before crimping: check the 8-way housing fits
  inside J1's shroud (the header looked shrouded in the photo) and matches
  its pitch. If J1 has no pin at position 5, fit a key plug in housing
  position 5 so the housing cannot mate one position off. Result not yet
  reported.

Planned wiring, one board per Cabinet I/O side header (4 wires):

| Opto board J1 | Cabinet I/O CABINET A (J1, left) | Cabinet I/O CABINET B (right) | Wire (22 AWG) |
| --- | --- | --- | --- |
| 1 SW1 | pin 1, `cab-8` | pin 1, `cab-16` | Orange |
| 2 SW2 | pin 2, `cab-9` | pin 2, `cab-17` | Orange |
| 3 or 4 GND | pin 9, G | pin 9, G | Purple |
| 6 or 7 12V | pin 13, 12 V | pin 13, 12 V | Yellow |

Colours: orange and purple follow this machine's switch convention, which
matches FAST's. GND is purple rather than black because it lands on the
switch return pin (G) and is the return for SW1 and SW2; it also carries the
board's supply current. Yellow is FAST's colour for low-current 12 V.

- This matches FAST's recommended cabinet numbering (flippers on `cab-8/9` and
  `cab-16/17`), and keeps `s_left_flipper` (`cab-8`) and `s_right_flipper`
  (`cab-16`) as configured, provided SW1 is the first stage. If SW2 trips
  first, swap the two wires or change the numbers.
- The board's GND is both its supply return and the reference for its
  switch outputs, so it must share ground with the switch inputs. Taking
  12 V and ground from the same header as the inputs does that with no
  question about separate grounds. FAST's guide suggests SHAKER PWR (J11 in FAST's docs, J12 on this -5 board) for opto power
  instead. FAST publishes no current rating for the side header's 12 V and G
  pins (Unverified), so measure the board's current draw on the bench first.
- The start button (`cab-10`, left header pin 3) also needs pin 9 (G), and
  its lamp (if fitted) needs 12 V. CABINET A has one G pin and one V+ pin,
  so the left opto board's spare GND (pin 4) and spare 12V (pin 7) are used
  as feeds for the start button. That keeps one wire per Cabinet I/O pin.

Left side harness, start button fed from the opto board (decided 2026-09-26):

| From | To | Wire (22 AWG) |
| --- | --- | --- |
| CABINET A pin 1 (`cab-8`) | Left opto J1 pin 1 (SW1) | Orange |
| CABINET A pin 2 (`cab-9`) | Left opto J1 pin 2 (SW2) | Orange |
| CABINET A pin 9 (G) | Left opto J1 pin 3 (GND) | Purple |
| CABINET A pin 13 (V+) | Left opto J1 pin 6 (12V) | Yellow |
| Left opto J1 pin 4 (GND) | Start button switch, common lug | Purple |
| Start button switch, other lug | CABINET A pin 3 (`cab-10`) | Orange |
| Left opto J1 pin 7 (12V) | Start lamp, one terminal | Yellow |
| Start lamp, other terminal | CABINET A pin 11 (L2, driver `cab-2`) | Grey or white |

- Opto J1 pins 6 and 7 (12V) have continuity (user, 2026-09-26).
- Opto J1 pins 3 and 4 (GND): continuity not yet checked. Check before using
  pin 4 as the start button's return.
- Start lamp type in the 500-6388-44 is unknown. An LED lamp is fine through
  the opto board. For an incandescent bulb, use a 12 V LED replacement or feed
  it straight from CABINET A pin 13, since the opto board's current rating
  between pins 6 and 7 is not published.
- Unplugging the left opto board also disconnects the start button's return
  and the start lamp's 12 V.
- The start lamp is not in the config yet (FAST's recipe drives it as a
  `platform: drivers` light on `cab-2`).

Wiring status (user, 2026-09-26):
- Left side harness installed as in the table above: flipper opto board,
  start button switch and start lamp. The lamp is in the config as `l_start`
  (`platform: drivers` on `c_start_lamp`, `cab-2`); nothing drives it yet.
- Right side installed: flipper button and opto board, to CABINET B pins 1, 2,
  9 and 13.
- All cabinet button and lamp wiring finished (user, 2026-09-26). The start
  lamp return was first landed on the pin labelled "11" (pin 4, switch input
  11) and has been moved to pin 11 (label L2). Remaining: buy the two 7-pin
  housings for the opto boards (J1 pitch still to measure).
- Still to confirm: opto J1 pins 3 and 4 continuity (the start button's
  return uses pin 4), the start lamp type and current, and the opto bench
  test result. None of it is powered or switch-tested yet.

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

### Tilt bob (planned 2026-09-27)

The owned Williams/Bally plumb bob tilt mechanism (A-15361) is a plain
switch: the pendulum touching the ring closes it. No polarity, 22 AWG.

| From | To | Colour |
| --- | --- | --- |
| Tilt bob, either contact | Wired 2026-09-27 to the pin labelled "18" on CABINET B (pin 3, `cab-18`); planned was CABINET A label "11" | Orange |
| Tilt bob, other contact | Purple daisy-chained via a lead or terminal of the cabinet power button (which lead: not yet recorded), then to the right opto board J1 pin 4 (GND) | Purple |

- Right opto board J1 pins 3 and 4 (GND) have continuity (user, 2026-09-27).
  The left board is the same part, so its pins 3 and 4 are very likely
  joined too (inference; not measured).
- The purple passes through one of the power button's switch leads (blue or
  yellow; which one not recorded) (user, 2026-09-27).
- Decision (user, 2026-09-27): use the power button as an ordinary switch
  until FAST releases soft power. Its other switch lead goes to the pin
  labelled "19" on CABINET B (pin 4, `cab-19`, orange 22 AWG), so the
  purple on its first lead is now its switch return as well as the tilt's.
  Wired as planned (user, 2026-10-01): switch lead on the pin labelled "19"
  (`cab-19`); the tilt bob stays on the pin labelled "18" (`cab-18`).
  In the config as `s_cabinet_button`. When soft power arrives: take both
  switch leads off (join the two purples directly for the tilt), and move
  blue and yellow to the Neuron's J4 pins 2 and 3.

- The purple daisy-chain is FAST's standard switch-return practice. It relies
  on the same return as the start button (left opto J1 pin 4, which depends
  on opto pins 3 and 4 being joined). If the start button works in the
  switch test, the tilt return does too.
- In the config as `s_plumb_bob` (`cab-18`, tag `tilt_warning`). MPF's
  built-in `tilt` mode is not in the `modes:` list yet; enabling it also
  needs a GMC slide named `tilt`, which does not exist yet.
- User decision (2026-09-27): skip the opto board bench test and the left
  opto pins 3 and 4 continuity check. Accepted risk: the opto outputs are
  assumed to suit FAST switch inputs (it is a FAST board named OPTO FLIPPER
  SW), and a missing 3-to-4 link would show up as a dead start button and
  tilt in the switch test.

### Cabinet power button (user photos, 2026-09-26)

A round stainless push button with an LED ring is fitted under the cabinet,
front right (the usual machine power switch position). It has a 5-wire blue
plug with red, yellow, blue, green and black leads. This is the common
"anti-vandal" LED push button style; its part number, whether it is momentary
or latching, the LED's rated voltage and the lead colour mapping are all
Unknown. Identify them with a meter before wiring (see below).

How FAST intends this button to be used (Official, FAST "SSR & soft power
switch" wiring guide):
- It is the soft power button: a low-voltage momentary push button wired to
  the Neuron's J4 (PWR SW), pins 2 and 3. The Neuron then switches the AC
  supply through a solid state relay (SSR) on J3, pins 1 and 3, with a
  thermal fuse and a CR2032 battery on the Neuron for power-on.
- FAST's soft power firmware is "coming soon" (as fetched 2026-09-25), so the
  button cannot switch the machine on yet. FAST says to build the hardware
  now and use a normal AC switch in the meantime.
- The button must be momentary. A latching button will not work with J4.

Identifying the leads (meter, button out of circuit):
1. Continuity between pairs with the button released, then pressed. The pair
   that closes only when pressed is common + normally open (NO); the pair
   that opens when pressed is common + normally closed (NC). The common lead
   is in both pairs. If it stays pressed after release, it is latching.
2. The remaining two leads are the LED. Find its rated voltage (printed on
   the body or the listing; these are sold as 3 to 6 V, 12 V, 24 V or
   110/220 V). For a 12 V LED, test on a 12 V supply both ways round with a
   low current limit; it lights one way only, which gives LED + and -.
3. A common vendor mapping is red = LED +, black = LED -, and the other three
   are the switch (C, NO, NC). That mapping is not verified for this button.

Lead mapping (user, 2026-09-26, not yet metered): blue and yellow are the
momentary switch pair; red and black are the LED (red taken as +). Green is
not accounted for; on these buttons it is usually the normally closed
contact, so leave it unconnected and insulated. Confirm with a meter that
blue to yellow closes only while pressed, and that the LED lights with red
on + and black on -. The LED's rated voltage is still Unknown.

Planned LED wiring (22 AWG):

| Button lead | To | Wire |
| --- | --- | --- |
| Red (LED +) | Right opto board J1 pin 7 (12V) | Yellow |
| Black (LED -) | CABINET B pin 11 (L4, `cab-4`) | Grey or white |
| Blue, yellow (switch) | Unconnected for now; later the Neuron J4 pins 2 and 3 | 2-core, if pre-run |
| Green | Unconnected, insulated | |

The button's own black lead is the LED's switched return, not a ground; it
lands on a driver pin, so label it. The light is in the config as
`l_power_button` (`platform: drivers` on `c_power_button_led`, `cab-4`).

How the machine is switched today (user, 2026-09-26): a mains rocker
switch on the back of the backbox (head). Switching it on powers everything
at once; the cabinet button plays no part. Switching it off also cuts the
host PC without a shutdown, which risks the Ubuntu install; FAST's soft power
plus the Neuron's J5 (PC control) header are meant to solve that once the
firmware ships.

Plan (2026-09-26):
- LED: wire now as an MPF-controlled light on CABINET B pin 11 (L4, `cab-4`),
  12 V from the right opto board's spare 12V (J1 pin 7), once the lead
  mapping and LED voltage are confirmed.
- Switch contacts: leave unconnected and labelled. If the cabinet is open
  anyway, pre-run a 2-core 22 AWG cable from the button to the backbox for
  the Neuron's J4 (PWR SW, pins 2 and 3), with slack for the head to fold.
- Soft power itself (SSR, thermal fuse, CR2032, a 3-position ON/OFF/SOFT
  mains switch per FAST's guide) waits for FAST's firmware. The existing
  rocker stays the power switch until then.

Open items are in the to-do list below ("Cabinet power button").

### Trough optos, position 1 and jam (user photos, 2026-10-03)

The 8-ball PBL-100-0016-00 trough uses mechanical switches for positions 2
to 8 (`s_trough2` to `s_trough8`, inputs 1 to 7) and an opto pair at the
eject end for position 1 and the jam (stacked ball) position (Official,
Pinball Life listing). One board sits on each side wall, both made by
Anarchy PCB, each with a 4-pin header labelled `B1 GND`, `B1 +`,
`JAM GND`, `JAM +`:

| Board | Silkscreen | Role |
| --- | --- | --- |
| Blue | "BALL TROUGH RECEIVER BOARD", 600-0208-00, REV A | Receiver: one dark-domed phototransistor each for BALL 1 and JAM, two leads each, traces straight to the header. No resistors or other parts on either side (both sides photographed 2026-10-03) |
| Green | "BALL TROUGH TRANSMITTER BOARD", 600-0209-00, REV A, "100MA MAX EACH" | Transmitter: two clear-bodied IR LEDs, at most 100 mA each, traces straight to the header. No resistors on either side (both sides photographed 2026-10-03), so the current limit must be external |

Wiring plan (decided 2026-10-03, not yet installed), all 22 AWG:

Receiver (blue), 4-pin 0.100" housing at the board:

| Receiver pin | To | Wire |
| --- | --- | --- |
| `B1 +` | 3208 J6 pin 8 (S22, `s_trough1`) | Orange |
| `JAM +` | 3208 J6 pin 9 (S23, `s_trough_jam`) | Orange |
| `B1 GND` | 3208 J6 pin 10 (G) | Purple |
| `JAM GND` | 3208 J6 pin 11 (G) | Purple |

J6 pin order (FAST table order): S16, S17, key, S18, S19, S20, S21, S22,
S23, G, G. Pins 1 to 7 already carry `bottom32-16` to `-21`. If pins 10
and 11 are already taken by other returns, join the two receiver purples
into the existing purple return instead.

Transmitter (green), 4-pin 0.100" housing at the board; interchange end,
3-pin 0.100" housing on one low-current header:

| From | Via | To | Wire |
| --- | --- | --- | --- |
| Interchange 12 V pin | One run, spliced near the trough into two tails | | Yellow |
| Tail 1 | 1k 1/4 W inline | Transmitter `B1 +` | Yellow |
| Tail 2 | 1k 1/4 W inline | Transmitter `JAM +` | Yellow |
| Interchange ground pin | One run, spliced near the trough into two tails | Transmitter `B1 GND` and `JAM GND` | Black |

- Which pin of the interchange low-current header is 12 V and which is
  ground is not published (FAST interchange and opto wiring guides, fetched
  2026-10-03). Meter it with the machine on before crimping.
- Emitter power distribution (for more optos later): one 12 V run and one
  ground run from the interchange header to a pair of lever connectors
  (e.g. WAGO 221 series) under the playfield, then a tail per LED, each
  with its own 1k. Adding an LED adds a tail; existing resistors do not
  change. Check each new emitter board for its own resistor first.
- Resistors and splices are soldered and heatshrunk, clear of the ball
  path and the trough's metal. The resistors are owned Yageo
  CFR-25JT-52-1K.

- The receiver needs no power: `+` is read as the collector and `GND` as the
  emitter, which is FAST's opto wiring (collector to the switch input,
  emitter to the return). Inference from the labels; confirm with the
  switch test.
- 1k from 12 V gives about 10.5 mA per LED: (12 V - about 1.5 V) / 1k,
  dissipating about 0.11 W (44% of a 1/4 W part). Chosen from parts on
  hand (2026-10-03); the owned 220 and 120 ohm parts are 1/8 W and would
  overheat at 12 V. If the switch test shows an unreliable beam, add a
  second 1k in parallel with each (500 ohm, about 21 mA, each resistor
  still about 0.11 W). The transmitter has no resistors of its own
  (confirmed 2026-10-03), so never put 12 V straight across an LED pair.
- Fit the resistors inline in the 12 V wires near the interchange end,
  soldered and heatshrunk, not on the board's header pins.
- Alternative: FAST's FP-AUX-040, a 4-channel 12 V constant-current opto
  emitter driver. It takes 12 V on a 3-pin 0.100" header and drives each IR
  LED at a regulated current, so no resistors are needed (Official, FAST
  product page, fetched 2026-10-03). Not in the parts inventory or the BOM,
  so not known to be owned (asked 2026-10-03). FAST quotes 43 mA at 12 V
  with 3 LEDs attached. If its channels are linear current regulators,
  that is about 14 mA per LED (inference, not published), close to the
  1k resistor plan's 10.5 mA. Output pinout not yet checked. Both boards take a crimped 4-pin housing (pitch to
  measure, 0.100" expected) so they can come off for trough service.
- Both switches are `type: NC` (beam clear means no ball). Do not add them
  to the config until they are wired: an unconnected NC input reads as a
  ball, so MPF would count a phantom ball and a jam.
- After they are in, raise `balls_installed` to 8 and add `s_trough1` to
  `virtual_platform_start_active_switches` (see the config comments).

### Playfield power distribution (planned 2026-09-27)

**The playfield I/O boards take no power cable.** Each board's logic runs on
12 V delivered over the I/O loop (RJ45) cables: "This loop is used to power
the I/O boards themselves (via 12V which is delivered via the loop)"
(Official, FAST I/O board wiring guide). The loop was closed on 2026-09-26,
so the back 1616, middle 1616 and front 3208 should all have logic power
already. `mpf hardware scan` reporting all four NET boards confirms it.

What each board needs before its coils can fire is the coil circuit, which
has three runs. None of them lands on a 48 V pin on the I/O board, because
the boards have none (13-fast-boards.md, sections 3.4 and 3.5):

| Run | From | To | Wire |
| --- | --- | --- | --- |
| 48 V feed | Playfield Interchange H1 pin (J5, J6 or J11), or H2 (J10) | Coil lug on the diode band side, daisy-chained coil to coil | Blue, 18 AWG |
| Driver line | Other coil lug | Driver pin on the I/O board's driver header | Black, 18 AWG (this machine's convention) |
| Toxic ground | I/O board driver header GND pins | Playfield Interchange TG pins | Black, 18 AWG, tagged "TG" |

- FAST: "All playfield power comes from the playfield interchange board,
  including the always-on 48V and toxic ground returns", and from each I/O
  board run "one toxic ground per high current solenoid from that I/O board.
  One toxic ground to cover 'everything else' from that I/O board"
  (Official, FAST driver wiring guide). For a heavily loaded 48 V daisy
  chain, FAST suggests a parallel wire rather than a thicker one.
- A board with no toxic ground wired has no return path for its drivers, so
  none of its coils will fire even though the board is on the loop and
  reports normally (engineering inference from FAST keeping toxic ground
  separate from logic ground).
- Tag every TG wire. Under this machine's convention a black TG wire and a
  black driver wire look the same, and both land on the same 12-pin header.

**Proposed header allocation** (one H1 header per board, so each board's
48 V chain and its toxic grounds unplug together):

| Interchange header | Circuit | Pins | Serves |
| --- | --- | --- | --- |
| J5, J6 or J11 (whichever is in use now) | H1 | 1x 48 V, 3x TG | Front 3208: flippers, slings, trough eject, auto plunge (already wired; header not yet recorded) |
| Next free H1 header | H1 | 1x 48 V, 3x TG | Middle 1616 |
| Last H1 header | H1 | 1x 48 V, 3x TG | Back 1616 |
| J10 | H2 | 1x 48 V, 2x TG, key | Platform magnet and knocker (both isolated on H2, per FAST's advice for magnets); returns from the board(s) driving them |

- Toxic ground pin budget: 11 on the interchange in total (3 each on J5, J6
  and J11, 2 on J10). FAST's one-per-high-current-solenoid rule will not fit
  every board once the playfield is complete, so give the extra TG pins to
  the boards driving flippers, VUKs and scoops.
- Whether all the interchange's TG pins are joined on the board is not
  stated by FAST (Unverified). Meter continuity between a TG pin on each of
  J5, J6, J11 and J10, with the machine off, before relying on a return
  landing on another header's TG pin.

**Driver capacity.** The 3208's 8 drivers are all assigned (`bottom32-0` to
`bottom32-7`), so every remaining playfield coil goes on the two 1616s (32
drivers):

| Coils | Drivers |
| --- | --- |
| `config/playfield_pending.yaml`, including a power and a hold driver per Hobbit pop-up | 18 |
| Knocker (backbox, back 1616) | 1 |
| Upper playfield mini flipper: same type as the main flippers (user, 2026-09-28), so dual-wound, power and hold | 2 |
| Upper right flipper: coil not recorded; 2 if dual-wound | 2 |
| Kickback (left outlane) | 1 |
| **Total** | **24 of 32** |

Pop bumpers (3 owned, not placed) would add 3. Each 1616 needs two 12-pin
0.156" driver housings (J3 and J4, keys at different positions).

**Hobbit pop-up wiring** (Official, JJP The Hobbit operation manual rev.
3.4, pop-up assembly parts list and Pop-Up Mechanisms Test; confirmed as
the Hobbit assemblies by the user, 2026-09-27). Each assembly has:

| Part | JJP part | Wires at the assembly | FAST connection |
| --- | --- | --- | --- |
| Coil: FL-11753 flipper coil, driven as "Pop-up Power" and "Pop-up Hold" | 23-2004-01 | 3: common, power winding, hold winding | Common to 48 V (blue); power and hold windings to 2 driver pins (black) |
| Up switch: microswitch with internal roller actuator | 18-3005-01 | 2 | 1 switch input (orange), return (purple) |
| Hit switch: leaf switch behind the head | 18-0006-00 (in 18-7019-0X) | 2 | 1 switch input (orange), return (purple) |

- 7 wires per assembly. Per assembly on FAST: 2 drivers and 2 switch
  inputs. For the three: 6 drivers and 6 switch inputs, all on a 1616.
  The 48 V and the purple return can be daisy-chained between assemblies.
- The Hobbit ran these coils at 70 V (manual coil table). FAST runs them at
  48 V, so the lift will be weaker. Whether it still raises the head
  reliably is Unverified: bench-test one assembly on 48 V before wiring all
  three.
- Check the diodes on each coil before wiring. FAST requires a flyback
  diode on every coil (13-fast-boards.md, section 4).
- Config (`config/playfield_pending.yaml`, 2026-09-28): each pop-up is a
  drop target on its up switch (`s_popup_N_up`, `type: NC`, so active means
  down). The power winding (`c_popup_N_power`) is the reset coil and lifts
  the head; the hold winding (`c_popup_N_hold`) is enabled on the same
  events that raise it, and released by the hit switch (`s_popup_N_hit`) or
  at game end, so the pop-up falls. Nothing is held in attract. Confirm the
  up switch's sense in the switch test before trusting `type: NC`.

**12 V on the playfield** is for devices, not I/O boards: the LED expansion
boards take 12 V from interchange J2 to J4 (7 A each), and opto emitter
boards from the four low-current headers (2.5 A combined).

Still to record: which interchange header feeds the 3208's coils now, and
how many TG wires return from its J4 GND pins. See the to-do list below
("Playfield power").

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
  See 13-fast-boards.md, section 5, finding 3.

Open items:
- [x] Order the Mean Well RSP-500-12 and the 50 A fuse (user, 2026-09-23).
- [ ] Buy the rest: 8 mm² twin-core tinned OFC cable (sold per metre; one run
      carries both +V and -V, so buy the route length plus about 0.5 m),
      a genuine Anderson SB50 pair with 8 AWG contacts, 8 AWG ferrules for
      the amp end, short 12 AWG leads with ring terminals and a small -V
      junction block for the supply end, a hex crimp tool, heatshrink, a
      grommet and cable clips, a short 18 to 22 AWG REM jumper (not blue,
      which this machine uses for coil positive runs), and 14 AWG
      (2 to 2.5 mm²) pure copper speaker cable for the amp to the sub
      (about 9.4 A RMS at the sub's 350 W into 4 ohms; 12 AWG if the run
      is over about 3 m).
- [x] 3 m 3.5 mm to 2 x RCA lead for the MC101 sub pre-out to the AMP1501
      (ordered, Amazon, $14, user, 2026-09-26). If only one RCA carries
      signal (mono pre-out), that is expected. If it hums, try a
      ground-loop isolator.
- [ ] Mount the RSP-500-12 in the backbox with its fan clear, and print a
      mount like the existing LRS-150 mounts if needed.
- [ ] Check the existing mains fuse rating (and slow-blow type) against the
      third supply's added load.
- [ ] Read the labels on the two existing backbox Mean Wells to confirm they
      are the RSP-500-48 and LRS-150-12.
- [x] **Cabinet I/O power cable** (planned 2026-09-26, installed by the user 2026-09-27; pre-power checks not yet reported): Smart Power Filter
      Board J10 CABINET to Cabinet I/O J3 TO FILTER BOARD, 4 x 18 AWG,
      straight through by label: 12 to 12 (yellow), G to G (black), TG to TG
      (black, tagged "TG"), H2 to H2 (blue). Both ends are 4-pin 0.156"
      housings with no key position; match pins by the printed labels (on
      the -5 Cabinet I/O, 12 is at the right-hand end). Fuses: F5 CAB12
      (12 V: opto boards, lamps, SHAKER PWR) and F1 48V_2 (H2, shared with
      the playfield H2). Record the fitted F5 value. The cable unplugs at
      both ends, so no inline connector is needed; leave slack for the head
      to fold.
- [ ] **Knocker in the backbox, on the back 1616** (decided 2026-09-26,
      option C). The owned Williams B-10686-1, mounted vertically (gravity
      return) with the strike plate (01-7525) above the plunger.
      Wiring, 18 AWG: Playfield Interchange J10 H2 (48 V, fuse F1) to the
      coil lug on the diode band side (blue); other coil lug to a spare
      driver pin on the back 1616's J3 or J4 (black, this machine's
      convention). The back 1616's driver GND pins must return to the
      interchange TG pins; nothing is plugged into that board yet
      (2026-09-27), see "Playfield power distribution". 1N4007 across the
      coil, band to the H2 lug.
      A 2-pin 0.156" inline connector where the pair crosses from
      playfield to backbox, with slack for the head to fold and the
      playfield to lift; it adds one plug to playfield removal.
      Config: add as a coil once the loop order gives the back 1616's
      `io_loop` name and the driver pin is chosen.
- [ ] **Shaker on the Cabinet I/O, driver 7** (follows from the knocker
      decision, 2026-09-26). Solid yellow (+) to SHAKER PWR + (J12 on the
      -5 board; meter its polarity first), striped yellow (-) to J2 D1
      (`cab-7`), 18 AWG, 1N4007 across the motor with the band on the solid
      yellow. SHAKER PWR - and J2 H2 and TG stay unconnected; never connect
      the motor straight across SHAKER PWR + and -. This follows FAST's
      "driver output (with proper protection)" route, so no FP-EXP-1313 is
      needed; the motor is driven as a coil (PWM hold power), not MPF's
      `shakers:` device. In the config as `c_shaker` (`cab-7`) with
      placeholder limits (2026-09-26): 50 ms full-power start, then 50%
      PWM hold, capped at 50% and 3 s per enable. Revise once the winding
      resistance, running current and fuse F5 (CAB12) value are known.
      Knocker deferred to a later date (user, 2026-09-26).
      Progress (user, 2026-09-26): harness wires crimped into the J12 and J2
      housings. Diode fitted (user, 2026-10-02). Still to do: connect the
      harness to SHAKER PWR (J12) on the Cabinet I/O, and the connector that
      mates with the shaker's own plug if that is still unbought.
- [ ] Check the JJP shaker's rated voltage, current and flyback diode before
      assigning it a driver. It is installed in the cabinet, not
      yet wired (user, 2026-09-25). Retailers list the replacement motor for
      JJP shaker kits (041-5029-04) as 12 V DC, 3100 RPM. Its two leads are
      yellow and yellow with a black stripe (user, 2026-09-26). Solid
      yellow = +, black-striped = - (user's online sources, Community
      practice, unverified for this motor; confirm against the terminal
      component's polarity marking if it is a polarised capacitor). A black cylindrical part sits at the motor terminals
      (photo, 2026-09-26), marked "CKHM", "2M45" and "R105 deg C T", with
      a scored end like an electrolytic capacitor's vent. It connects from
      the motor's + terminal to the motor frame (user, 2026-09-26), the
      usual layout for a noise-suppression capacitor. Value and polarity
      marking: Unknown. With the low side switched (driver or EXP-1313),
      the + terminal sits at a steady 12 V, so PWM does not charge and
      discharge this capacitor on every pulse (engineering inference). If
      it is a polarised electrolytic, its minus stripe must face the frame
      lead. It does not replace a flyback diode across the motor.
      No diode is visible across the two motor solder tabs (photo,
      2026-09-26): fit a 1N4004 or 1N4007 across them, band to the solid
      yellow (+) tab. Its current is not
      published, so read the fitted motor's label or measure its winding
      resistance (stall current is roughly 12 V / R). Planned wiring: motor +
      to Cabinet I/O SHAKER PWR (J12 on this -5 board, 12 V; confirm polarity with a meter), motor - to driver 7 (J2 D1) if
      the shaker gets it,
      diode across the motor with the band to +12 V. The flipper optos take
      12 V from the side switch headers, not SHAKER PWR (see "Cabinet flipper opto
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
- `x c v b n m k` toggle trough switches 2 to 8
- `.` (full stop) toggles the plunger lane
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
- [ ] Fit the playfield opto sets (owned, none fitted yet; only the trough
      optos are on the machine, user 2026-10-03): left lock ramp and
      backboard ramp, plus the set listed with the right outlane lock
      parts, which the lock itself may not use. Power them from the
      emitter lever connectors (see "Trough optos").
- [ ] Wire the trough position 1 and jam optos and add `s_trough1` and
      `s_trough_jam` (see "Trough optos" above). They are still commented
      out in `config/config.yaml`.
- [x] Shooter lane switch wired to input 0 on the front 3208 (user,
      2026-10-02). In the config as `s_plunger` (`bottom32-0`), with
      `bd_plunger` restored as the playfield's source device. The trough
      switches were renumbered at the same time: the user corrected them to
      inputs 1 to 7, starting with the one closest to the trough eject
      (`s_trough2` = `bottom32-1` to `s_trough8` = `bottom32-7`). The old
      config had `s_trough2` on 0 and inputs 2 and 3 swapped. All eight are
      still to be confirmed in the switch test.
- [ ] Confirm the cabinet button numbers. `s_left_flipper` (`cab-8`), `s_start`
      (`cab-10`) and `s_right_flipper` (`cab-16`) are now in the config with the
      `flippers:` section enabled, but the numbers are FAST's recommended
      defaults, not measured on this machine. MPF range-checks them against the
      24 inputs the board reports and nothing more, so a wrong-but-in-range
      number reads the wrong input silently. Verify in the service-mode switch
      test once the board is wired.
- [ ] **Do the board checks in 13-fast-boards.md, section 2.** The most
      important are the physical loop order and the Neuron firmware version
      (v2.13 or newer is needed for the Cabinet I/O). The Cabinet I/O part
      number is done: FP-I/O-0024-5 (2026-09-25).
- [x] **Cabinet I/O cabled into the I/O loop** at order 1 (user,
      2026-09-26), matching the config.
- [x] **48 V enable** (user, 2026-09-27): J8 (ENA IN) on the Smart Power
      Filter Board is jumpered across pins 1 and 3, and the 48V ENA LED is lit.
      48 V is now live whenever the machine is powered (no coin door
      interlock). Later: replace the jumper with a coin door interlock switch
      (closed when the door is shut), optionally wire J9 (ENA OUT) to a spare
      Cabinet I/O switch input, or move to FAST's software enable once it is
      released.
- [ ] **Cabinet power button.** Identify its leads and whether it is
      momentary (see "Cabinet power button"). Optionally pre-run a 2-core
      cable to the backbox for the Neuron's J4. For the LED, the plan is MPF
      control: LED + from
      the right opto board's spare 12V (J1 pin 7, if pins 6 and 7 are joined
      as on the left), LED - to CABINET B pin 11 (L4), as a second
      `platform: drivers` light on `cab-4`. Needs a 12 V LED, or a series
      resistor sized for its rated voltage.
- [x] **Second 1616 added to `io_loop:`** (2026-09-26), order traced by the user: Neuron, Cabinet I/O, Interchange, back 1616 (`top16`, 2), middle 1616 (`mid16`, 3), front 3208 (`bottom32`, 4), Interchange, Neuron. Neither 1616 has anything plugged in yet.
- [ ] **Playfield power** (planned 2026-09-27; see "Playfield power
      distribution"). The I/O boards need no power cable (12 V comes over
      the loop). Record which interchange H1 header feeds the 3208's coils
      and how many TG wires leave its J4 GND pins. Meter the interchange TG
      pins for continuity across headers. Then, per 1616, as its first coils
      are wired: an H1 header's 48 V (blue) daisy-chained to its coils, and
      TG (black, tagged) from its J3 and J4 GND pins to that header's TG
      pins.
- [ ] Run `mpf hardware scan` to confirm the board models and loop order match the config (`FP-I/O-0024`, `FP-I/O-1616` ×2, `FP-I/O-3208`, `FP-EXP-2000` + `FP-PWR-0007`). This is the fastest way to get the true `order:` values.
- [ ] Wire the Cabinet I/O (FP-I/O-0024-5). It's mounted but unwired.
      Pinouts are in 13-fast-boards.md, section 3.6. None of its 13-pin
      headers are keyed. The config
      now assumes the side flipper buttons and start button land on the
      left-side (`cab-8` to `cab-15`) and right-side (`cab-16` to `cab-23`)
      headers; the coin door header J4 is `cab-0` to `cab-7`. The board's 8
      drivers (`cab-0` to `cab-7`) are still unconfigured, so no knocker or
      button lamps yet.
- [ ] Knocker background (superseded 2026-09-26 by "Knocker in the
      backbox, on the back 1616" above): the owned WPC assembly B-10686-1
      with an AE-23-800 coil, no diode fitted (use a 1N4007; the black part
      on the shaker motor is a capacitor, not a diode). It has no return
      spring and must be mounted vertically, plunger firing up into the
      strike plate (Community practice, Pinscape build guide). MPF 0.80 has
      no `knockers:` device, so it is a plain entry under `coils:` fired by
      `coil_player`. Nothing in the Act I rules fires it yet.
- [x] The Cabinet I/O's NET cables are in the I/O loop, at order 1 (user, 2026-09-26).
- [ ] **Install Godot 4.7.2 on this machine.** `project.godot` is now tagged
      `4.7`, but the editor here is still 4.6.3, which will warn that the
      project was made with a newer version. Download 4.7.2 from
      godotengine.org, replace `~/.local/opt/godot/`, keep the
      `~/.local/bin/godot` symlink pointing at it, and fetch the matching
      4.7.2 export templates before building a production export.
      Godot 4.7.2 was verified against this project in a container: the import
      is clean, GMC 1.0.0 loads, and all four slides render unchanged.
- [ ] No LED expansion boards are wired or configured yet (FP-EXP-0081 and FP-EXP-0071 are owned). Needed before any playfield RGB inserts or servos work.
- [ ] Decide the plunger behaviour. `bd_plunger` has `eject_coil: c_auto_plunge` plus `mechanical_eject: true` but no `player_controlled_eject_event`, so a ball in the lane waits for a manual plunge at ball start, and multiball balls fire the auto-plunge coil. `eject_timeouts` cut from 15 s to 5 s (2026-10-02); it only applies to coil ejects.
- [ ] Modes `welcome`, `plunge_ready` and `skillshot` exist but aren't listed under `modes:` and have no start events. `skillshot.yaml` is empty.
- [ ] `slide_player` for attract is defined in both `config.yaml` and `modes/attract`, so it is duplicated.
- [ ] Later, for production: export the Godot project to a binary, build the MPF production bundle, and set up auto-start on boot.
