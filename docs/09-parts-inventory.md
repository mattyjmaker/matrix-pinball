# Parts Inventory (from The Matrix BOM)

**Source:** `claude-workspace/The-Matrix-BOM.xlsx`, downloaded 2026-09-19 from the user's Dropbox
(private Dropbox link — not published; see the local copy in `claude-workspace/mpf-documentation/`).
That spreadsheet is the source of truth. If this file disagrees with it, re-download it and update this file.

The workbook has these sheets:
- **Parts:** the master list. Prices are in USD, but some rows are really AUD.
- **First Order**, **Second Order (Mar 2024)** and **Third Order (Oct 2024)**: Pinball Life and FAST carts.
- **Measurements:** hole sizes and clearances.

Status key:
- **HAVE:** marked "purchased!" or has an amount in Total Purchased on the Parts sheet, proven by the running machine, or seen in the **Feb 2023 order**.
- **ORDER:** no longer used. On 2026-09-19 the user confirmed that **all orders arrived** (First, Second Mar 2024, Third Oct 2024), so those items are now HAVE, marked (2nd) or (3rd).
- **PLANNED:** on the BOM but not bought.

The **Feb 2023 order** was placed through Pinside/Trident Pinball and paid 2023-02-04 (US$2,846: Pinball Life US$1,460 + FAST US$1,086 + shipping and handling). The cart screenshots are in Dropbox under `Invoices Purchases/Trident Pinball/Order 1 - Feb 2023/`. The Pinball Life cart had 122 items, so the screenshots may not show every line. This order covers most of the BOM's "First Order" plus the trough, shooter and cabinet mechs, even though the Parts sheet never marked them purchased.

## Control electronics (FAST)

| Part | Qty | Status | Notes |
|---|---|---|---|
| FAST Neuron starter bundle + power supplies + connector/pin pack | 1 | HAVE | Feb 2023 order. Running on this PC as `/dev/ttyACM*` (see 08-this-machine.md). |
| FAST Expansion Board, 256 LEDs | 1 | HAVE | Neuron bundle option |
| FAST Expansion Board, 128 LEDs + 4 servos (FP-EXP-0071) + connectors | 1 | HAVE | Feb 2023 |
| FAST network cables: 7 ft ×2, 2 ft ×4 | 6 | HAVE | Feb 2023. The BOM says 3 ft ×4, but the cart shows 2 ft. |
| FAST vertical mount bracket set | 3 | HAVE | Feb 2023 |
| FAST I/O 1616, v2 firmware for Neuron, + connectors | 1 | HAVE | Feb 2023 |
| FAST I/O 1616 (Neuron version) + connectors | 1 | HAVE (2nd) | This is a **second** 1616, so there are 2 in total. |
| FAST 3 ft network cable | 2 | HAVE | Second Order |
| FAST vertical mount bracket set | 3 | HAVE | Second Order |
| FAST Cabinet I/O board + connectors | 1 | HAVE | Third Order |
| FAST RGB/LED inserts | 50-pack | HAVE | Feb 2023 |
| Wire, 1,400 ft in 11 colours (wirebot.xyz) | 1 lot | HAVE | |

### Boards actually installed (user, 2026-09-20)

| Where | Board | Part no. | On a bus? |
|---|---|---|---|
| Backbox | FAST **Smart Power Filter Board** (the "big capacitor board") | FP-PWR-0007 | EXP bus, via a 5-wire cable from its J7 BREAKOUT header to a Neuron breakout header |
| Backbox | FAST **Neuron** controller | — | host USB; hosts the NET and EXP buses |
| Playfield, back | FAST **I/O 1616** | FP-I/O-1616 | NET loop |
| Playfield, rear | FAST **Playfield Interchange Board** | FP-PWR-0030 | **No** — passive |
| Playfield | FAST **I/O 3208** — flippers and the lower third are primarily wired to this one | FP-I/O-3208 | NET loop |
| Playfield, middle | FAST **I/O 1616** (the 2nd one) | FP-I/O-1616 | NET loop |

So the NET loop carries **2× 1616 + 1× 3208 + the Cabinet I/O** (the latter mounted but unwired — see below).

Both the Smart Power Filter Board and the Playfield Interchange Board ship in the **Neuron starter bundle**, which is why neither appears as its own BOM line.

**Playfield Interchange Board (FP-PWR-0030)** — mounts to the rear of the playfield and is a passive distribution point: main power in from the backbox, out as 4× 48 V driver, 3× 12 V high-current and 4× 12 V low-current fused outputs (2.5 A combined, protected by a soldered-on self-resetting fuse — Bourns MF-MSMF250/16X). It also passes the I/O Loop and Expansion Bus cables through. Because it's passive it has no NET or EXP address, so **MPF needs no config for it**. Its point is that four connectors unplug and the whole playfield lifts out, and you can build the playfield outside the cabinet with no separate power distribution blocks.

**Smart Power Filter Board (FP-PWR-0007)** — the primary power distribution and fuse centre (48 V, 12 V, plus host-PC power). "Smart" because it reports current and fuse status to the Neuron over the EXP bus and can cut 48 V on a short or over-current. ✅ Already correctly declared in `config/config.yaml` as a breakout on port 1 of the Neuron's `FP-EXP-2000`.

✅ The **FP-I/O-3208 does exist** and is installed, even though it never appeared in the BOM or the Feb 2023 FAST cart. The config's `bottom32: FP-I/O-3208` is correct. (The Dropbox `FAST_3208_HEAT_PRESS_M3_v15.stl` mount is presumably for it.)

⚠ **The config is missing a board.** `config/config.yaml`'s `io_loop:` declares only three — `cab` (FP-CAB-0001), `top16` (FP-I/O-1616) and `bottom32` (FP-I/O-3208) — but there are two 1616s installed. The middle 1616 needs its own entry, and the `order:` values must match the real daisy-chain order out of the Neuron, or every switch and driver number shifts to the wrong board.

**Cabinet I/O (FP-CAB-0001): installed but not yet wired** (user, 2026-09-20). The config expects it at `order: 1`. Two consequences: the `cab-…` switch numbers (flipper buttons, start) and the cabinet drivers (knocker, button lamps) can't be finalised yet; and if its **NET cable isn't in the I/O loop**, `order: 1` is wrong and every other board's order shifts.

⚠ **No LED expansion boards are installed or configured.** The user owns two (FP-EXP-0081 256-LED and FP-EXP-0071 128-LED + 4-servo), and `config/config.yaml`'s `exp:` section lists only the Neuron's own `FP-EXP-2000` plus the power filter breakout. So there are no playfield RGB LEDs or servos wired yet — consistent with wiring being unfinished.

Reference: [Playfield Interchange Board](https://fastpinball.com/products/power/playfield-interchange-board/) · [wiring it](https://fastpinball.com/wiring/neuron/playfield-interchange/) · [Smart Power Filter Board](https://fastpinball.com/products/power/smart-power-filter-board/) · [part number lookup](https://fastpinball.com/products/part-numbers/)

## Cabinet, backbox and audio/video

| Part | Qty | Status |
|---|---|---|
| Stern slide & pivot support brackets, L + R | 1 each | HAVE |
| Playfield edge slide brackets | 2 | HAVE |
| Playfield pivot brackets (500-5329-03) | 2 | HAVE |
| Playfield hanger brackets (Stern) | 2 | HAVE |
| Williams/Bally playfield hanger brackets, short | 2 | HAVE (3rd) |
| Stern SPIKE support slide bracket kit | 1 | HAVE |
| Williams/Bally black legs (set of 4), new-style leg brackets ×4, #8×5/8" bracket screws ×30 | — | HAVE |
| Leg levelers with nylon glide ×4, leg felt protectors | — | HAVE |
| Leg bolts, black 2-3/4" (pack of 8); soft-socket leg bolt tool | — | HAVE |
| Happy Sliders, carpet set + hard-floor set | 1 each | HAVE (3rd) |
| Widebody lockdown bar with action button (Black River) | 1 | HAVE |
| Lockdown bar receiver (Facebook Marketplace) | 1 | HAVE |
| JJP/Spooky lockdown bar receiver with action button slot | 1 | HAVE (2nd). This may duplicate the one above. |
| WPC-95 black backbox hinge set, 1/4-20 carriage bolts ×12, whiz locknuts ×12 | — | HAVE |
| Widebody glass 1090 × 604 × 5 mm | 1 | HAVE |
| Widebody glass rear channel, glass side channels ×2 | — | HAVE |
| Glass corner protectors (set of 2) | 2 sets | HAVE (3rd) |
| Mirror blades (Stern) | 1 set | HAVE |
| Backbox translite channels | 1 | HAVE |
| Backbox H-channel | 1 | HAVE (Feb 2023) |
| Coin door with 2 coin acceptors + switches (Alibaba), plus 2 spare acceptors | 1 | HAVE |
| Alienware AW2723DF 27" monitor (backbox display) | 1 | HAVE |
| VESA 100 tilt/swivel monitor mount | 1 | HAVE |
| Fosi Audio BT30D Pro (TPA3255) stereo amp | 1 | HAVE (unconfirmed; the user reports the amp in the chain is an MC101) |
| Fosi Audio MC101 (2 x TPA3116) stereo amp, 3.5 mm full-range sub pre-out | 1 | HAVE (user, 2026-09-23). Currently drives the car speakers |
| Kenwood KFC-WPS1200F 12" subwoofer | 1 | HAVE |
| Stereo car speakers (donated) | 1 pair | HAVE |
| Blaupunkt AMP1501 monoblock sub amp (12 V car amp, 1500 W "max") | 1 | HAVE (user, 2026-09-23). Optional; see 08-this-machine.md, "Audio wiring". |
| Triangular button guard side rails (Stern) + mounting tape | — | HAVE (Feb 2023) |
| Red start button (500-6388-44) | 1 | HAVE (Feb 2023) |
| Cabinet flipper buttons, transparent green, with spring | 2 | HAVE (Feb 2023) |
| Double flip switch assembly 500-6890-01 (EOS/double-stack cabinet switches) | 2 | HAVE |
| Nylon pal nuts (button nuts) | 2 | HAVE |
| Williams/Bally complete tilt mechanism (A-15361) | 1 | HAVE (Feb 2023) |
| Knocker assembly WPC/WPC-95 (B-10686-1, coil AE-23-800) + strike plate | 1 | HAVE (Feb 2023) |
| Shaker motor assembly (JJP, PBL-100-0092-00) | 1 | HAVE (Feb 2023) |

## Flippers, slings and posts

| Part | Qty | Status |
|---|---|---|
| Full flipper assembly, WPC 1992–98, left + right (coil FL-11629, stop A-12390, normally-open EOS SW-1A-194) | 2 | HAVE (Feb 2023) |
| Right flipper mech (upper right flipper) + black bat + green rubber | 1 | HAVE (2nd) |
| Left flipper mech (Real World mini flipper) + small yellow TSPP bat + blue mini rubber | 1 | HAVE (2nd) |
| Flipper bat & shaft, black (no logo), + 1-1/2" green Super-Band rubbers | 2 | HAVE (Feb 2023) |
| Upper playfield flipper links (Marco 515-7265-06, 04-10038, No Fear bushing) | — | Reference only |
| Slingshot assembly (PBL-5849-01) | 2 | HAVE (Feb 2023) |
| Narrow plastic posts, green ×4; 2-1/2" black rubber rings ×2 | — | HAVE (Feb 2023) |
| Star posts ×2 | 2 | PLANNED (not seen in the Feb 2023 screenshots) |
| **DE/Sega pop bumper assembly (500-5227-00, coil AE-26-1200, black base, clear cap, black skirt)** | **3** | **HAVE (Feb 2023). Not listed in the BOM at all.** |
| DE/Sega/Stern return lane guide (550-5037), green | 2 | HAVE (Feb 2023). Not in the BOM. |
| Narrow plastic posts: orange ×5, blue ×4, purple ×5 | 14 | HAVE (3rd) |
| 2" black rubber ring | 1 | HAVE (3rd) |
| Machine post/stud 530-5012-02 | 30 | HAVE (3rd). 10 more planned from Pinballhaus. |
| Machine post/stud 530-5008-00 | 10 | HAVE (2nd) |
| 2-1/4" metal post (10-32 base / 6-32 female top) | 3 | HAVE (2nd) |
| 2-1/2" metal post (10-32 base / 8-32 male top) | 8 | HAVE (2nd) |
| Purple 1-1/16" post sleeves | 3 | HAVE (2nd) |
| Metal round spacer 1-11/16" (6-32 M/F) | 6 | HAVE (2nd) |
| Mini post 10-32 base (530-5005-00, Pinballhaus) | 3 | PLANNED |
| Pan screw with lock washer 10-32 × 1/2" | 4 | HAVE |

## Trough, shooter and ball handling

| Part | Qty | Status |
|---|---|---|
| Ball trough assembly, 8-ball (PBL-100-0016-00) | 1 | HAVE (Feb 2023) |
| Upper ball trough assembly (2-piece) | 1 | HAVE (3rd) |
| Shooter lane auto-kicker assembly (A-21022) | 2 | HAVE: one from Feb 2023 and one from the 3rd order |
| DE/Sega/Stern ball shooter assembly (500-6146-00-04, black, green spring) + housing mounting plate (535-5027-00) | 1 | HAVE (Feb 2023) |
| 10-32 × 5/8" machine screws for the plunger plate | 4 | HAVE |
| Williams/Bally auto-fire assembly (kickback) | 1 | HAVE (2nd) |
| Pinballs, 1-1/16" standard | 10 | HAVE (3rd) |
| Zeitgeist-Ultra pinballs | 3 | HAVE (3rd) |
| Hobbit outer + inner shooter lane flat-rail guides | 1 each | HAVE (2nd) |
| One-way gate assembly (Stranger Things) | 1 | HAVE (2nd) |
| JJP (Wizard of Oz) outhole ball guide flat rail | 1 | HAVE (2nd) |
| Widebody bottom arch (Hobbit), black | 1 | HAVE (2nd) |
| JJP arch retainer brackets | 2 | HAVE (3rd) |
| Wire ball guides 13-3000-26 ×2, 13-3014-26 ×3, 13-3021-00 ×1, 13-3000-05 ×5 | 11 | HAVE (2nd) |
| Rollover switch with mounting bracket (SP-SW-002) | 10 | HAVE (Feb 2023) |

## Feature mechs, by playfield area (mostly the Second Order)

| Area / feature | Parts | Status |
|---|---|---|
| **Agents** (mid-field pop-ups) | Hobbit pop-up beast assemblies ×3: one Orc, one Warg, one Spider. The user confirmed this on 2026-09-19; the spreadsheet is wrong on both sheets. | HAVE |
| **Matrix Team** (5 pop-up targets) | Gottlieb 5-bank drop targets, second-hand (Solar City 1976–77) | HAVE |
| **EMP pop bumper** area | Standup targets ×6, 3-bank drop target assembly (frosted) | HAVE (2nd) |
| **Trinity Ramp** | Stern ball lock assembly, left spinner with switch, IR LED opto set | HAVE (2nd) |
| **Dejavu VUK** | Scoop weldment, closed back | HAVE (2nd) |
| **Agents coming** | Scoop weldment with open back, standup target ×1 | HAVE (2nd) |
| **Ammo Lock** | Stern ball lock assembly, IR LED opto set | HAVE (2nd) |
| **Real World playfield** | Standup targets ×3, plus the mini left flipper above | HAVE (2nd) |
| **Dejavu Ramp** | Left spinner with switch | HAVE (2nd) |
| **Sentinel Boss** | Stern eject VUK 500-1050-00 ×2, 1"×5/8" rectangular standup ×1, square standups ×2, under-playfield magnet assembly ×1 | HAVE (2nd) |
| **Sentinel Ramp** | IR LED opto set | HAVE (2nd) |
| **Real World Ramp** | Left spinner with switch | HAVE (2nd) |
| **Mission Drop** | 1-bank smart drop target (left, frosted), standup ×1, open-back scoop weldment | HAVE (2nd) |
| **Nixie countdown** | 2× IN-12 Nixie tubes + 2 sockets | HAVE |
| Scoop protector | Addams Family electric chair scoop protector | HAVE (3rd) |

The anti-sway 1" frosted square standup targets have diodes. Across all areas there are 13 on order.

## Playfield inserts (HAVE, Second Order)

| Insert | Qty |
|---|---|
| 1" round starburst, clear | 22 |
| 1" square starburst, clear | 10 |
| 1" × 5/16" oval outline, clear | 10 |
| 1-1/16" equilateral triangle starburst, clear | 8 |
| 1-13/16" × 15/16" obtuse triangle starburst | 4 |
| 1" shield ribbed, yellow | 3 |
| 1-1/2" × 5/8" triangle starburst | 3 |
| 2" × 1" triangle starburst | 3 |
| 1-1/2" × 3/4" obtuse triangle starburst | 2 |
| 1-3/4" × 5/8" bullet ribbed | 2 |

## Toys, wood and hardware

| Part | Status |
|---|---|
| McFarlane Matrix Sentinel deluxe boxed set (2003) | HAVE |
| McFarlane Matrix Neo "Real World" figure (2003) | HAVE |
| 18 mm birch plywood, 2 sheets (cabinet) | HAVE |
| 12 mm birch plywood (playfield) | HAVE |
| M5 heat-set inserts (50) and M5 stainless screws (20× 20 mm, 10× 10 mm) | Listed; status unknown |
| Spade bolts 20-9284 ×20 | Listed; status unknown |
| Artwork: cabinet, playfield, plastics, translite acrylic and printing | Not costed ("?") |

## Measurements sheet

- Standup targets need at least 16 mm depth and 30 mm width.
- Scoop: 38 mm wide, 37 mm deep.
- 3-bank drop target: 16 mm deep, 96 mm wide.
- Smart drop: 13 mm deep, 30 mm wide.
- Flipper hole: 13 mm.
- Appearing post hole: 11 mm.
- GI lights: 12 mm, or 15 mm in 3D prints such as the inlanes.
- Head: 52 mm deep, 42 mm wide.
- Trough: 360 × 34 mm.
- Spade bolt thread is 8-32 (4.1 mm); drill a 4.5 mm hole.
- Wireform plug holes: 3.2 mm. The gap for the bottom two wireforms is 20.321 mm.
- Ball guides: stainless steel, 16 gauge (1.6 mm) × 1" (26.5 mm).
- 3D-print heat inserts: a 5 mm hole through the playfield. An extra 10 mm of depth is ideal so the screw reaches the playfield.

## Coil and switch implications (for the MPF config)

This is a rough count of devices that need drivers if everything owned goes in.

**Coils:**
- flippers ×4: 2 main, upper right, and the Real World mini
- slingshots ×2
- trough eject and auto-plunger/auto-kicker
- kickback auto-fire
- ball locks ×2 (Trinity, Ammo)
- scoops ×3 (Dejavu, Agents coming, Mission Drop)
- Sentinel eject VUKs ×2
- magnet ×1
- 3-bank drop reset, 1-bank smart drop, Gottlieb 5-bank reset
- Agents pop-ups ×3
- knocker (a coil) and shaker (a motor)
- pop bumpers ×3 (owned, but not placed in the BOM's layout)

**Switches:** add opto sets (×3) and spinners (×3) to all of the above.

Check driver and switch totals against the FAST boards actually installed on the playfield: **2× I/O 1616 + 1× I/O 3208**. The Neuron itself has no driver outputs; the I/O boards carry them.

Per-board capacity: a **1616** gives 16 switch inputs + 16 drivers; a **3208** gives 32 switch inputs + 8 drivers. So the playfield total is **64 switch inputs and 40 drivers**.

**Rough capacity check (revised 2026-09-20 now that the board list is confirmed; estimate only, redo from the real layout):**

- **Playfield coils: about 27–30.** The list above plus any appearing posts or diverters from the VPX, such as TrinityPost, RightPost, BackDiverter and LeftDrainSavePost. **40 drivers available**, so these now fit with room to spare. The Cabinet I/O's drivers go to the cabinet: knocker, button lamps, always-on outputs.
- **Playfield switches: about 70 or more.**
  - trough ~9, shooter lane 1, rollovers 10
  - standups 13, drop targets 9 (3 + 1 + 5), Agents 3
  - spinners 3, optos 3+, scoops 3, VUKs 2, ball-lock switches ~5
  - slings 2, pops 3, flipper EOS 4 (optional)

  **64 switch inputs available**, so this is short by roughly 6 — much closer than the earlier estimate, and it may well fit once the real layout is counted (flipper EOS is optional, and the pops aren't placed in the BOM layout). If it doesn't, one more 1616 closes the gap.
- **Cabinet switches** (coin door, flipper buttons, start, tilt, launch) go on the Cabinet I/O, so they don't consume playfield inputs.

## Known BOM data issues (not yet fixed in the spreadsheet)

- The Parts sheet's "Total Spent to Date" (US$2,695) excludes the Neuron and the Second and Third Orders.
- The double flip switch and pal nut rows record Total Purchased as 2× the planned amount.
- Row 23's item name is "`". It's the widebody glass rear channel.
- The right slide bracket (row 9) links to the left bracket's page.
- The Pinballhaus rows and the $22 spare coin acceptors are AUD, although the header says everything is USD.
