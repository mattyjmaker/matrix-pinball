# FAST Boards: Owned Hardware Reference

This file is a reference for every FAST Pinball board this machine owns: what
each one does, its headers and pinouts, how MPF 0.80 sees it, and what still
has to be checked on the machine.

- **Reviewed:** 2026-09-25, from fastpinball.com (fetched that day) and the
  MPF 0.80.0 wheel from PyPI.
- **Source labels:** *Official* means fastpinball.com or the MPF 0.80.0 source.
  *User-provided* means the owner's notes in 08-this-machine.md and
  09-parts-inventory.md. Anything not backed by one of those is marked
  **Unverified**.
- **Pin numbering:** FAST's pinout tables list each header's pins in order.
  For the Cabinet I/O, the wiring guide's pin references ("Pin 9 G",
  "Pin 13 V+") confirm that table order is pin order. For the other boards
  that is assumed. Check pin 1 on the silkscreen before crimping a housing.
- **Diagrams:** FAST's wiring diagrams are images and were not read. Only the
  text and tables were used.

## 1. What is owned

| Board | Part number | Qty | Location | Bus | MPF 0.80 config | Wiring state (user) |
| --- | --- | --- | --- | --- | --- | --- |
| Neuron controller | FP-CPU-2000 (its built-in expansion board is FP-EXP-2000) | 1 | Backbox | USB to host; hosts the NET loop and EXP bus | `controller: neuron`, EXP board `neuron` | Running; enumerates as `/dev/ttyACM0` to `ACM2` |
| Smart Power Filter Board | FP-PWR-0007 | 1 | Backbox | EXP breakout (5-wire cable to a Neuron breakout header) | Breakout `port: 1` of `neuron` | Not recorded |
| Playfield Interchange Board | FP-PWR-0030 | 1 | Rear of playfield | None (passive) | None needed | Not recorded |
| I/O 1616 | FP-I/O-1616 | 2 | Playfield back; playfield middle | NET loop | One declared (`top16`); **the second is missing** | Partly wired |
| I/O 3208 | FP-I/O-3208 | 1 | Playfield | NET loop | `bottom32` | Flippers and lower third wired |
| Cabinet I/O | **FP-I/O-0024-5** (silkscreen, photo 2026-09-25; the repo previously said FP-CAB-0001) | 1 | Cabinet | NET loop | `cab` | Mounted, not wired; NET cables not plugged in |
| Expansion board, 256 LEDs | FP-EXP-0081 | 1 | Not installed | EXP bus | Not configured | Not wired |
| Expansion board, 128 LEDs + 4 servos | FP-EXP-0071 | 1 | Not installed | EXP bus | Not configured | Not wired |
| Opto flipper switch board | FP-SWI-7083-1 (silkscreen, photo 2026-09-25) | 2 | Cabinet, one per side | Switch-level only | None | Blocked: no matching housings |
| Network cables | 7 ft x2, 2 ft x4, 3 ft x2 | 8 | | NET and EXP | | |

FAST's part number index lists no FP-SWI boards, current or retired
(Official, checked 2026-09-25), so the FP-SWI-7083-1 is undocumented by FAST.
It was previously misrecorded as FP-SWI-7003-1. See section 3.9.

## 2. Checks to do on the machine

Record each result in 08-this-machine.md with the date. Items 1 to 3 block the
first boot on FAST hardware.

1. **Cabinet I/O part number. Done 2026-09-25: FP-I/O-0024-5** (user photo).
   The config's `FP-I/O-0024` is correct. Revision -5 is newer than FAST's
   documentation; see section 3.6 for what differs. The same photo shows no
   cables in either NET jack, so the board is not in the loop yet, and
   `order: 1` in the config is wrong until it is. The background:
   - MPF 0.80 compares the model each board reports over the loop with the
     `model:` in `io_loop:` and stops with an `AssertionError` if they differ
     (`mpf/platforms/fast/communicators/net_neuron.py`, `_process_nn`).
     `FP-CAB-0001` and `FP-I/O-0024` are both valid names, but MPF does not
     treat them as aliases. (Official, MPF 0.80.0 source)
   - FAST's docs say the public board is the FP-I/O-0024, that FP-CAB boards
     were built for commercial partners with different pinouts, and that
     revision -4 is the only one sold publicly. FAST's own MPF log example
     shows a cabinet board reporting `FP-I/O-0024-3`. (Official)
2. **Loop order.** Trace the cables from the Neuron's NODE OUT through each
   board's IN and OUT and back to the Neuron's IN. Record which physical board
   is 1, 2, 3 and 4. Also record the full part number and revision of both
   1616s and the 3208.
3. **Neuron firmware.** The Cabinet I/O needs Neuron firmware v2.13 or newer
   (Official). With `fast: net: debug: true`, the MPF log shows it on the
   `ID:NET FP-CPU-2000 <version>` line.
4. **Smart Power Filter Board breakout.** Note which Neuron breakout header
   (J23, J24 or J25) the filter board's J7 cable is plugged into. The config
   says `port: 1`. FAST's pages do not say how J23 to J25 map to MPF ports
   1 to 3 (Unknown), so confirm it from the EXP debug log.
5. **Smart Power Filter Board fuses and 48 V enable.** Record the fuse fitted
   in each of F1 to F6. Check whether J8 (ENA IN) is jumpered or wired to the
   coin door switch, and whether the 48V ENA LED is lit.
6. **Expansion boards.** Record the revision of the FP-EXP-0081 and
   FP-EXP-0071, and confirm their ID solder jumpers are open (default
   addresses 84 and B4).
7. **FP-SWI-7083-1.** Measure J1's pin pitch and check whether pin 5 (KEY)
   has a pin fitted, so matching housings can be ordered. Then do the bench
   test in 08-this-machine.md ("Cabinet flipper opto boards") before
   connecting it to the Cabinet I/O.

## 3. Board reference

### 3.1 Neuron controller (FP-CPU-2000)

Official: [product page](https://fastpinball.com/products/controllers/neuron/),
[wiring guide](https://fastpinball.com/wiring/neuron/neuron/).

- Supports up to 120 switches and 120 drivers, over at most 9 I/O boards.
- The built-in expansion board (FP-EXP-2000) has 4 LED ports (10 W sustained
  in total) and 3 breakout headers.
- There are 2 EXP bus ports and 1 display bus port.
- It runs on 12 V only. Boards that need 5 V make it locally.
- Soft power on and off is "not yet complete" and will come in a future
  firmware update (Official, as fetched).

| Header | Function | Details in FAST guide |
| --- | --- | --- |
| J1 | 12 V power in (3-pin 0.156") | Smart Power Filter Board wiring |
| J3, J4 | SSR relay and soft power switch (3-pin 0.100") | SSR wiring |
| J5 | Host PC control (5-pin 0.100") | Host PC wiring (guide not yet written) |
| J10 | Raspberry Pi | Raspberry Pi wiring |
| J13 | USB to host | Host PC wiring |
| J26 | 12 V power out (2-pin 0.156") | Fuses and current |
| J23, J24, J25 | Breakout headers (5-pin 0.100") | Expansion board wiring |
| J19 to J22 | LED chain headers (4-pin 0.100") | LED wiring |
| J15, J11 | I/O loop RJ45 | Playfield I/O wiring |
| J6 | Display bus RJ45 | DMD and segment wiring |
| J7, J8 | Expansion bus RJ45 | Expansion board wiring |
| BAT1 | CR2032 battery | SSR wiring |

- **BLANKING LED (D5):** when it is on, the watchdog has expired and all
  drivers are disabled. The MPF default watchdog is 1 s. (Official, FAST MPF
  NET page)
- **MPF:** `fast: net: controller: neuron`, plus `FP-EXP-2000` under
  `fast: exp: boards:`. MPF gives it a local breakout (FP-BRK-0001) with
  4 LED ports, so backbox LEDs are numbered `neuron-<port>-<led>`.
  (Official, MPF 0.80.0 `fast_defines.py`)

### 3.2 Smart Power Filter Board (FP-PWR-0007)

Official: [product page](https://fastpinball.com/products/power/smart-power-filter-board/),
[wiring guide](https://fastpinball.com/wiring/neuron/smart-power-filter-board/),
[fuses guide](https://fastpinball.com/wiring/neuron/fuses/).

This board sits between the power supplies and the machine. It is the fuse
centre, holds 30,000 uF of 48 V reserve capacitance, and is the only place
where the 48 V toxic ground and the 12 V logic ground are joined.

| Header | Label | Type | Purpose | Fuse |
| --- | --- | --- | --- | --- |
| J6 | 48V INPUT | 7-pin 0.156" | Pins 1 to 3 toxic ground (black), pin 4 key, pins 5 to 7 48 V (blue). All six wires are required. | none |
| J5 | 12V/CPU INPUT | 7-pin 0.156" | Pins 1 and 2 are G and CPU (host PC supply, any DC voltage); the rest are 2x 12 V and 2x ground. All three pairs are required, even when the host PC is 12 V. | none |
| J1 | CONTROLLER | 3-pin 0.156" | 12 V to the Neuron | F2 BKBOX |
| J2 | BACKBOX | 3-pin 0.156" | 12 V for backbox devices (DMD, LCD) | F2 BKBOX |
| J3 | TOPPER | 3-pin 0.156" | 12 V for a topper | F2 BKBOX |
| J4 | CPU POWER | 3-pin 0.156" | Host PC power, at whatever voltage is on J5 pins 1 and 2 | F3 CPU |
| J12 | PLAYFIELD | 9-pin 0.156" | 12 V on pins 1 and 2, 48 V H1, 48 V H2 and 3x toxic ground, to the Playfield Interchange Board J19. All 8 wires are required. | F6 PLAY12 (12 V), F4 48V_1 (H1), F1 48V_2 (H2) |
| J10 | CABINET | 4-pin 0.156" | 12 V, ground, toxic ground and 48 V H2, to the Cabinet I/O J3 | F5 CAB12 (12 V), F1 48V_2 (H2, shared with the playfield) |
| J7 | BREAKOUT | 5-pin 0.100" | Link to a Neuron breakout header, wired straight through pin to pin (G, T, R, G, V; T and R are swapped on the boards by design), 22 AWG | none |
| J8 | ENA IN | 3-pin 0.100" | 48 V output is enabled only while pins 1 and 3 are connected | none |
| J9 | ENA OUT | 3-pin 0.100" | Switch output that mirrors 48 V enable: + to a switch input (orange), - to switch ground (purple) | none |
| J11 | GND TIE | spade | Tie point for the DC grounds to chassis or earth. FAST says this is a deliberate decision, covered in its ground guide. | none |

Specifications (Official):
- Every 0.156" header pin is rated 7 A. On 12 V branches, use a fuse no larger
  than 6 A.
- The 48 V circuit accepts 20 to 60 V DC.
- The CPU circuit range is inconsistent between FAST pages: the product page
  says 9 to 60 V DC, the wiring guide says 9 to 30 V DC. Use 30 V as the
  limit.
- The capacitors discharge slowly, over several hours. Treat them as charged.

Fuse sizing (Official, fuses guide):
- FAST gives no fixed values. Start low and step up until the fuse survives
  normal play. Deliberately short each circuit once to prove its fuse blows.
- The fuse must be the weakest part of every circuit.
- If the 12 V supply can deliver more than 7 A, FAST suggests an inline 6 A
  5x20 mm fuse on each supply lead, so a loose parallel wire cannot overload
  one pin.
- For the AC line fuse, FAST suggests 5 A for 240 V countries. This is
  relevant to the open item in 08-this-machine.md on the mains fuse and the
  third (RSP-500-12) supply.

**48 V enable.** Both the product page and FAST's MPF power page say the smart
functions (current monitoring, fuse status, remote 48 V enable) are **not
released yet** (Official, as fetched). Until they are, the board outputs 48 V
only while J8 pins 1 and 3 are closed. The Cabinet I/O guide calls the
software-controlled coin door interlock "preferred", but that option depends
on the unreleased feature. For now:
- wire the coin door interlock switch to J8, or jumper J8 for bench testing;
- optionally, wire J9 to a Cabinet I/O switch input so MPF can see that 48 V
  has been cut.

**MPF 0.80:** `FP-PWR-0007` is accepted as a breakout model. The source marks
it `# TODO temp module until this code is written`, so declaring it does
nothing useful yet beyond detecting the board. (Official, MPF 0.80.0
`fast_defines.py`)

### 3.3 Playfield Interchange Board (FP-PWR-0030)

Official: [product page](https://fastpinball.com/products/power/playfield-interchange-board/),
[wiring guide](https://fastpinball.com/wiring/neuron/playfield-interchange/).

This board is passive and has no MPF config. Unplugging 1 power connector and
the network cables here frees the playfield.

| Header | Type | Purpose |
| --- | --- | --- |
| J19 | 9-pin 0.156" | Power trunk in from the filter board's J12 |
| J5, J6, J11 | 4-pin 0.156" | 48 V H1 plus 3x toxic ground. For most coils, including the flippers. |
| J10 | 4-pin 0.156" | 48 V H2 plus 2x toxic ground and a key, so it cannot be swapped with H1. For magnets or anything to isolate. |
| J2, J3, J4 | 3-pin 0.156" | 12 V high current, 7 A each. Use one for the playfield expansion board. |
| 4x low current | 3-pin 0.100" | 12 V for opto emitter boards. 2.5 A combined, protected by a soldered self-resetting fuse (Bourns MF-MSMF250/16X). Use 22 AWG minimum. |
| I/O loop | 4x RJ45 | Straight pass-through couplers. Each jack connects to the one behind it, not the one beside it, and direction does not matter. |
| EXP bus | 3x RJ45 | All three are bussed together and interchangeable |

- **Cable length:** allow enough slack in every cable for the backbox to fold
  down and for the playfield to be lifted up.

### 3.4 I/O 1616 (FP-I/O-1616), qty 2

Official: [product page](https://fastpinball.com/products/ioboards/1616/),
[I/O board wiring](https://fastpinball.com/wiring/neuron/ioboards/).

- 16 switch inputs and 16 drivers.
- Powered by 12 V over the loop cables.
- Housings needed: 2x 12-pin 0.156" (drivers) and 2x 11-pin 0.100"
  (switches).
- The 11-pin DBI header near the RJ45 jacks is no longer used.

| Header | Pins in FAST table order |
| --- | --- |
| J1 | NODE OUT (RJ45) |
| J2 | NODE IN (RJ45) |
| J3 drivers 0-7 (12-pin 0.156") | D0, D1, D2, D3, key, D4, D5, D6, D7, GND, GND, GND |
| J4 drivers 8-15 (12-pin 0.156") | D8, D9, D10, D11, D12, key, D13, D14, D15, GND, GND, GND |
| J7 switches 0-7 (11-pin 0.100") | S0, S1, S2, S3, key, S4, S5, S6, S7, G, G |
| J8 switches 8-15 (11-pin 0.100") | S8, S9, S10, key, S11, S12, S13, S14, S15, G, G |
| J6 | Programming (2x5 0.100") |

- **GND on the driver headers** is the toxic ground return. It goes back to a
  toxic ground pin on the Playfield Interchange Board. It is not a 48 V
  supply: 48 V reaches each coil directly from the interchange board.
- **Keys:** the key sits in a different position on each header, so a keyed
  housing only fits its own header.
- **Driver MOSFET:** IRL540NSTRLPBF, one per driver output.
- **Firmware:** Neuron systems use 2.x firmware, Nano systems 1.x. MPF 0.80
  refuses to start below I/O firmware 1.09 (`IO_MIN_FW`). (Official)

### 3.5 I/O 3208 (FP-I/O-3208)

Official: [product page](https://fastpinball.com/products/ioboards/3208/).

- 32 switch inputs and 8 drivers.
- Housings needed: 1x 12-pin 0.156" (drivers) and 4x 11-pin 0.100"
  (switches).

| Header | Pins in FAST table order |
| --- | --- |
| J1 | NODE OUT (RJ45) |
| J2 | NODE IN (RJ45) |
| J4 drivers 0-7 (12-pin 0.156") | D0, D1, D2, D3, D4, key, D5, D6, D7, GND, GND, GND |
| J8 switches 0-7 | S0, S1, S2, S3, key, S4, S5, S6, S7, G, G |
| J3 switches 8-15 | S8, S9, S10, key, S11, S12, S13, S14, S15, G, G |
| J6 switches 16-23 | S16, S17, key, S18, S19, S20, S21, S22, S23, G, G |
| J9 switches 24-31 | S24, key, S25, S26, S27, S28, S29, S30, S31, G, G |
| J7 | Programming (2x5 0.100") |

- **Key positions differ** from the 1616 as well as between headers. A driver
  housing keyed for a 1616 J3 (key at position 5) will not fit a 3208 J4 (key
  at position 6).
- Status LEDs, MOSFET and firmware are the same as the 1616.

### 3.6 Cabinet I/O (FP-I/O-0024)

Official: [product page](https://fastpinball.com/products/ioboards/cabinet/),
[wiring guide](https://fastpinball.com/wiring/neuron/cabinet-ioboard/).

This machine's board is **FP-I/O-0024-5** (silkscreen, user photo
2026-09-25). FAST's pages document revisions up to -4, so section 3.6.1 lists
what the -5 board shows and where it differs.

- 24 switch inputs and 8 drivers.
- Needs Neuron firmware v2.13 or newer. Not compatible with the Nano.
- FAST designed it for the front-left corner of the cabinet, on the coin door
  hinge side.
- **None of the 13-pin headers are keyed.** FAST suggests cutting a different
  unused pin on each header and fitting a key plug in the matching housing.

**Drivers.** The software numbers do not match the silkscreen for the
knocker driver.

| Software number | Silkscreen | Type | Rating (Official) |
| --- | --- | --- | --- |
| 0 to 5 | L0 to L5 | Low current, current-limited open drain, for 12 V or 5 V LEDs | Not stated beyond "low current" |
| 6 | D6 | Digital open drain, plus TTL outputs D6 and D6-inverted on J10 | 200 mA open drain; TTL 20 mA, 0 to 5 V |
| 5 (shared) | D5 | TTL output on J10, shares its control line with L5 | 20 mA |
| **7** | **D1** on J2 | Standard high-current driver, the only one on the board. MOSFET Q4, IRL540NSTRLPBF. | Same as a playfield I/O driver |

**Pinouts** (pin 1 first), as FAST documents them for revision -4. On this
machine's -5 board, J9 is printed CABINET B, J10 is J11, and J11 (SHAKER PWR)
is J12; J1 is printed CABINET A. See section 3.6.1.

| Pin | J1 CABINET LEFT | J9 CABINET RIGHT | J4 COIN DOOR | J10 BILL/CARD/TICKET (rev -4) |
| --- | --- | --- | --- | --- |
| 1 | S8 | S16 | S0 | S21 (same input as J9 pin 6) |
| 2 | S9 | S17 | S1 | S22 (same input as J9 pin 7) |
| 3 | S10 | S18 | S2 | S23 (same input as J9 pin 8) |
| 4 | S11 | S19 | S3 | D6 digital (enable output) |
| 5 | S12 | S20 | S4 | D5 TTL (shares L5) |
| 6 | S13 | S21 | S5 | D6-inverted TTL |
| 7 | S14 | S22 | S6 | G |
| 8 | S15 | S23 | S7 | G |
| 9 | G (switch return) | G | G | G |
| 10 | 5 V always on | 5 V | 5 V | 5 V |
| 11 | L2 | L4 | L0 | L3 (same driver as J1 pin 12) |
| 12 | L3 | L5 | L1 | L5 (same driver as J9 pin 12) |
| 13 | 12 V always on | 12 V | 12 V | 12 V (sized for a 4 A bill acceptor) |

| Header | Type | Pins |
| --- | --- | --- |
| J2 KNOCKER | 4-pin 0.156" | D1 (driver 7), key, TG (toxic ground), H2 (48 V) |
| J3 TO FILTER BOARD | 4-pin 0.156" | 12 V, G, TG, H2, from the filter board's J10 |
| J11 SHAKER PWR | 3-pin 0.156" | key, + (12 V), - (ground) |
| J6 | RJ45 | NODE IN |
| J7 | RJ45 | NODE OUT |

**Shared resources.** Switches 21 to 23 are one set of inputs, reachable on
both J9 and J10. Likewise L3 is on J1 and J10, and L5 is on J9 and J10 (and
shares its line with D5). Use each input or driver in one place only.

**Silkscreen misprint.** Some boards label the J4 coin door inputs
0-7-6-5-4-2-1-0 instead of 7-6-5-4-3-2-1-0. The pins and electronics are
correct, so ignore the labels.

**Inconsistencies in FAST's own pages** (Official, noted 2026-09-25). Treat
the pinout table and the board's silkscreen as authoritative, and confirm with
a meter:
- The wiring guide puts the coin door switches on "Pins 6-13" in one
  paragraph and on "Pin 1-8" in the next two. The pinout table puts them on
  pins 1 to 8.
- The product page says J10's D5 is "shared with pin 13", but by position D5
  shares with L5 on pin 12. Pin 13 is 12 V.

**Wiring (Official, wiring guide):**
- **Switches:** purple from pin 9 (G), daisy-chained to one lug of every
  switch; orange from each switch's other lug to its input.
- **Button and coin reject lamps:** a common wire from pin 13 (12 V, yellow)
  or pin 10 (5 V, red) to one leg of each lamp, and the other leg to L-driver
  pin 11 or 12 (white or grey). The lamps stay off until MPF enables them.
- **Knocker:** J2 H2 to the coil lug on the diode band side, and J2 D1 to the
  other lug. The coil needs a flyback diode.
- **Bill acceptor:** FAST says to use a 12 V pulse-type unit on J10: 12 V from
  pin 13, ground from pin 9, credit pulse to S21 to S23 (pins 1 to 3), and
  inhibit driven from pin 4 (D6) or pin 6 (D6-inverted). None is owned.
- **Opto flipper buttons:** FAST says to take their 12 V from J11. J11 has
  its own ground pin; the side headers only offer the switch return G.
- **Cabinet expansion board:** FAST says it can take power from J11.

#### 3.6.1 Revision -5 as fitted (User-provided photo, 2026-09-25)

The photo shows the component side from the front. Pin labels on the lower
headers are printed under the header bodies and are only partly legible, so
anything below marked Unverified needs a closer photo or a meter.

| FAST -4 docs | This -5 board | Status |
| --- | --- | --- |
| J1 CABINET LEFT | J1 **CABINET A**, 13 pins labelled 8, 9, 10, 11, 12, 13, 14, 15, G, 5V, L2, L3, V+ | Same pinout, new name |
| J9 CABINET RIGHT | **CABINET B**, 13 pins; legible labels run 16 up to 23, then G, from the right-hand end | Designator not legible. Pin order matches -4 as far as readable; L4, L5, 5V and V+ labels not legible (Unverified) |
| J4 COIN DOOR | J4, 13 pins, inside a bracket marked COIN DOOR | Pin labels not visible (Unverified) |
| (none) | **J8**, 5 pins, also inside the COIN DOOR bracket, below J4 | **Not in FAST's docs.** Function and pinout Unknown |
| J10 BILL/CARD/TICKET | **J11** BILL/CARD/TICKET, 13 pins; labels end 23, 22, 21 at the right-hand end | Designator changed. Pins 1 to 3 (S21 to S23) match -4 as far as readable |
| J11 SHAKER PWR | **J12** SHAKER PWR, 3-pin with K printed at the right-hand end | Designator changed. The polarity of the other two pins is not legible; confirm with a meter before wiring |
| J2 KNOCKER | J2, labelled H2, TG, K, D1 from left to right | Same pins. D1 (driver 7) is at the right-hand end |
| J3 TO FILTER BOARD | J3, labelled H2, TG, G, 12 from left to right | Same pins |
| J6, J7 NODE IN / OUT | J7 (upper) and J6 (lower) RJ45 | IN and OUT labels not visible; FAST -4 has J6 IN and J7 OUT (Unverified for -5) |

Other features visible on the -5 board and not described by FAST:
- **Fuses F1 to F3 and F5 to F7:** six small fuses, each beside one of the
  driver transistors (Q1 to Q8 area). Six fuses match the six low-current
  drivers L0 to L5, but that mapping and their rating are Unverified.
- **F4 and F8:** larger parts marked `050` / `30`. F4 is near J3 and the
  knocker MOSFET Q4; F8 is near pads marked `5V` and `12V`. Their rating and
  function are Unverified.
- **LEDs:** D1 labelled EXT PWR, plus D3 STATUS, D4 LINK and D5 ACTIVE.
- **Test points:** NET, 12V, VCC, 3V3 and GND.
- **Unpopulated positions:** a row of pads marked GND, CK, LD, DO, DI; a
  single-row header position J5; and a 2x5 header J9 (programming on other
  FAST I/O boards). Their functions are Unknown.

Worth asking FAST for the -5 pinout sheet, covering J4, J8 and J12 polarity
in particular, before wiring the coin door and the shaker.

**MPF numbering for this machine** (`io_loop` name `cab`). These are FAST's
recommended defaults (see 02-hardware.md, "FAST 0024 cabinet I/O board
recipe") and are not yet switch-tested:

| Device | Number | Header and pin |
| --- | --- | --- |
| `s_left_flipper` | `cab-8` | J1 CABINET A, pin 1 |
| `s_start` | `cab-10` | J1 CABINET A, pin 3 |
| `s_right_flipper` | `cab-16` | CABINET B, pin 1 |
| Knocker (planned) | `cab-7` | J2, D1 |

### 3.7 Expansion board, 256 LEDs (FP-EXP-0081)

Official: [product page](https://fastpinball.com/products/expansion/81/),
[expansion board wiring](https://fastpinball.com/wiring/neuron/expansion-boards/),
[LED wiring](https://fastpinball.com/wiring/neuron/leds/).

- 8 LED ports, each driving up to 32 WS2812 LEDs, for 256 in total.
- 20 W sustained: 10 W for each bank of 4 ports.
- 2 EXP bus ports.
- 12 V in on a 3-pin 0.156" header. On the playfield, take it from a Playfield
  Interchange 12 V high-current header (J2 to J4).
- Default EXP address 84. The ID solder jumpers set 85 to 87; only needed for
  a second 0081.
- **MPF:** `model: FP-EXP-0081`. MPF 0.80 requires EXP firmware 0.12 or newer
  for this board. LEDs are numbered `<board>-<port>-<led>`. (Official, MPF
  0.80.0 source)

### 3.8 Expansion board, 128 LEDs + 4 servos (FP-EXP-0071)

Official: [product page](https://fastpinball.com/products/expansion/71/).

- 4 LED ports, each driving up to 32 WS2812 LEDs, for 128 in total; 10 W
  sustained.
- 4 servo ports. The board makes the servo supply from its 12 V input
  (6 V, per FAST's expansion board guide).
- 2 EXP bus ports and 12 V in (3-pin 0.156").
- Default EXP address B4 (B5 to B7 by jumper).
- MPF 0.80 requires EXP firmware 0.11 or newer.
- FAST's Neuron servo wiring guide is still "coming soon" (Official, as
  fetched).

**LED rules** (Official, LED wiring guide), for both expansion boards and the
Neuron:
- 32 LEDs per port at most.
- WS2812-type 3-wire RGB only for now. APA102 and RGBW support are promised
  in future firmware.
- With 3-wire LEDs, the header's C (clock) pin is not connected.
- Follow the data direction arrows on each LED.
- No mid-chain power injection is needed, because the 5 V is made on the
  board.

### 3.9 Opto flipper switch board (FP-SWI-7083-1), qty 2

Not on FAST's part number index, and there is no product page. Everything
below comes from the silkscreen in a photo supplied by the owner on
2026-09-25 (User-provided). Anything not printed on the board is marked.

- **Function:** "OPTO FLIPPER SW". Two optos (OP1, OP2) sit in the path of
  two flags on the flipper button's actuator, so each board gives two switch
  outputs, SW1 and SW2. That suits a two-stage button (first and second
  stage, or lower and upper flipper). Which output trips first is Unknown.
- **J1:** 7-pin header, white and shrouded in the photo. Pin 1 is marked with
  a triangle. Pins: 1 SW1, 2 SW2, 3 GND, 4 GND, 5 KEY, 6 12V, 7 12V.
- **Alternative pads:** 4 unpopulated through-hole pads, SW1, SW2, 12V and
  GND.
- **Test points:** IN1 and IN2, next to U1.
- **Other parts visible:** R1, R2 and D1, D2 beside the optos. Q1, Q2 are
  3-pin SMD transistors. U1 is an 8-pin SOIC with an ST logo; its part
  marking is not legible in the photo. Circuit function: Unverified.
- **Other marking:** a line reading `...0A_Y226_240330` sits beside J1. Its
  meaning is Unknown.
- **Supply:** 12 V, which matches the Cabinet I/O side headers' pin 13 and
  J11.
- **Output type:** Unknown. Open-collector outputs to GND would suit a FAST
  switch input. Confirm with the bench test in 08-this-machine.md first.

**Housing family (Unverified).** The pin count (7) and the KEY position are
known. The pitch is not. Measure from the centre of pin 1 to the centre of
pin 7:
- 15.24 mm means 0.100" (2.54 mm) pitch. FAST's other boards use 0.100"
  headers for this kind of signal.
- 15.0 mm means 2.5 mm pitch, for example JST XH.

The 0.24 mm difference needs calipers. The shroud shape also helps: a JST XH
header is a closed box, while a 0.100" friction-lock header has an open front
with a ramp on the back wall. If pin 5 has no pin, fit a key plug in position
5 of the housing.

**Wiring plan:** see 08-this-machine.md, "Cabinet flipper opto boards". In
short: SW1 and SW2 go to the first two inputs of a Cabinet I/O side header
(`cab-8`/`cab-9` left, `cab-16`/`cab-17` right), GND to that header's pin 9
and 12 V to its pin 13.

### 3.10 Buses and cables

- **I/O loop (NET):** a ring of Cat 5 cables (5e and 6 also fine). It is not
  Ethernet.
  - Connect each board's OUT to the next board's IN, and the last board's OUT
    back to the Neuron's IN. The loop must be closed.
  - FAST says 99% of problems are two INs or two OUTs connected together.
  - Board order does not matter electrically, but it sets MPF's `order:`
    values and switch numbering.
- **EXP bus:** a tree, not a loop. Any port can go to any port, and not every
  port needs to be used.

## 4. Wiring standard: FAST compared with this machine

FAST's standard (Official, [wiring standards](https://fastpinball.com/wiring/standards/)):

| Colour | Gauge | Purpose |
| --- | --- | --- |
| Red | 18 AWG | 5 V power, high current |
| Yellow | 18 AWG | 12 V power, high current |
| Blue | 18 AWG | 48 V power |
| Black | 18 AWG | DC ground returns, high current, all voltages (including 48 V toxic ground) |
| Grey or white | 18 AWG | Driver control lines, from coil to I/O board driver pin |
| Orange | 22 AWG | Switch inputs |
| Purple | 22 AWG | Switch returns |
| White | 22 AWG | LED data |
| Red | 22 AWG | 5 V or less, low current |
| Yellow | 22 AWG | 12 V, low current |
| Black | 22 AWG | 5 V and 12 V ground returns, low current |

- **Wire gauge:** 0.156" headers take 18 AWG (up to 7 A). 0.100" headers take
  22 AWG (up to 3 A).

Compared with this machine's convention (User-provided, 08-this-machine.md):

| Circuit | This machine | FAST | Result |
| --- | --- | --- | --- |
| Switch input | Orange | Orange | Same |
| Switch return | Purple | Purple | Same |
| Coil positive (48 V) | Blue | Blue | Same |
| Coil "negative" (the lug wired to the driver pin) | Black | Grey or white | **Different.** FAST keeps black for ground returns, including the toxic ground from each I/O board's GND pins back to the interchange board. With black driver lines, a control line and a ground return look the same when servicing. |

Other FAST rules that apply here (Official):
- **Toxic ground:** keep the 48 V toxic ground separate from the 12 V logic
  ground everywhere. They join only inside the Smart Power Filter Board.
- **Coil diodes:** every coil and magnet needs a flyback diode, band to the
  48 V lug. FAST accepts 1N4001, 1N4004 or 1N4007. This repo specifies
  1N4004 or 1N4007: a 1N4001 is rated 50 V, only 2 V above the 48 V supply.
  That extra margin is this repo's choice, not a FAST requirement.
- **Switch diodes:** switches need no diodes. There is no matrix.
- **Opto receivers:** collector to the switch input (orange), emitter to
  switch return (purple). An opto reads active when unblocked, so it is
  inverted in software.
- **Flippers:** FAST recommends dual-wound flipper coils. Each one uses two
  drivers (power and hold).

## 5. Findings

Ordered by impact.

1. **The Cabinet I/O model in the config was wrong, and is now fixed.** It
   said `FP-CAB-0001`; the board reads FP-I/O-0024-5, and MPF 0.80 aborts on
   a mismatch. The config now says `FP-I/O-0024`. Separately, the board is
   not yet cabled into the loop, so its `order: 1` is wrong until it is.
   Revision -5 also has a header (J8) and designator changes that FAST does
   not document (section 3.6.1).
2. **The second 1616 is missing from `io_loop:`.** This was already known.
   It still needs the real loop order (check 2).
3. **The knocker and the shaker are both planned on the Cabinet I/O, but it
   has only one high-current driver** (driver 7, D1 on J2).
   - L0 to L5 are current-limited LED drivers, and D5 and D6 are logic
     outputs (200 mA and 20 mA). By FAST's ratings, none of them can run a
     12 V motor.
   - FAST's shaker guide says a regular driver can work "with caveats around
     the snubber" and recommends its shaker expansion board, the FP-EXP-1313,
     which is not owned. MPF's `shakers:` device also needs the EXP-1313.
   - Decision for the owner: give driver 7 to the knocker or to the shaker.
     The alternatives are an FP-EXP-1313 for the shaker, or a spare playfield
     I/O driver run down to the cabinet.
4. **48 V enable must be hardware for now.** Software 48 V control is
   unreleased (Official, as fetched), so the filter board needs J8 closed by
   the coin door switch or a jumper. The "smart switch preferred" advice in
   FAST's Cabinet I/O guide cannot be followed yet.
5. **The driver line colour differs from FAST's standard** (black here, grey
   or white in FAST's standard). See section 4. The owner decides whether to
   switch for the remaining wiring.
6. **Opto board power from the side headers is not FAST's recommendation.**
   FAST points opto flipper buttons at J11, which has its own ground. The
   FP-SWI-7083-1's GND is both its supply return and its switch output
   reference, so taking 12 V and G from the same side header keeps the
   grounds common. FAST publishes no current rating for those pins
   (Unverified), so measure the board's current draw first. The board's
   output type is also Unverified (section 3.9).
7. **The Neuron firmware has not been confirmed as v2.13 or newer.** The
   Cabinet I/O needs it (check 3).
8. **The filter board's breakout `port: 1` has not been confirmed** (check 4).
   MPF 0.80's support for this board is a placeholder in any case.
9. **FAST's own pages disagree** on several details: the Cabinet I/O coin
   door pins, J10 D5, and the filter board's CPU voltage range. In each case
   the pinout table and the silkscreen take precedence.

## Sources

Official, fastpinball.com (fetched 2026-09-25):
- Part number index: https://fastpinball.com/products/part-numbers/
- Neuron: https://fastpinball.com/products/controllers/neuron/ and https://fastpinball.com/wiring/neuron/neuron/
- Smart Power Filter Board: https://fastpinball.com/products/power/smart-power-filter-board/ and https://fastpinball.com/wiring/neuron/smart-power-filter-board/
- Playfield Interchange Board: https://fastpinball.com/products/power/playfield-interchange-board/ and https://fastpinball.com/wiring/neuron/playfield-interchange/
- I/O 1616: https://fastpinball.com/products/ioboards/1616/
- I/O 3208: https://fastpinball.com/products/ioboards/3208/
- I/O board wiring: https://fastpinball.com/wiring/neuron/ioboards/
- Cabinet I/O: https://fastpinball.com/products/ioboards/cabinet/ and https://fastpinball.com/wiring/neuron/cabinet-ioboard/
- FP-EXP-0071: https://fastpinball.com/products/expansion/71/
- FP-EXP-0081: https://fastpinball.com/products/expansion/81/
- Expansion board wiring: https://fastpinball.com/wiring/neuron/expansion-boards/
- LED wiring: https://fastpinball.com/wiring/neuron/leds/
- Driver wiring: https://fastpinball.com/wiring/neuron/drivers/
- Flipper wiring: https://fastpinball.com/wiring/neuron/flippers/
- Opto wiring: https://fastpinball.com/wiring/neuron/optos/
- Fuses and current: https://fastpinball.com/wiring/neuron/fuses/
- Wiring standards: https://fastpinball.com/wiring/standards/
- Shaker, servo and host PC guides (all "coming soon"): https://fastpinball.com/wiring/neuron/shaker-motor/, /servos/, /host-pc/
- MPF config for FAST: https://fastpinball.com/mpf/config/net/, /exp/, /power/

Official, MPF 0.80.0 (PyPI wheel `mpf-0.80.0-py3-none-any.whl`):
- `mpf/platforms/fast/fast_defines.py`: valid I/O models, EXP addresses and firmware minimums, FP-PWR-0007 placeholder
- `mpf/platforms/fast/communicators/net_neuron.py`: model assertion, `IO_MIN_FW = 1.09`

User-provided: 08-this-machine.md, 09-parts-inventory.md.
