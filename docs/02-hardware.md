# 02 — Hardware, Controller Platforms, Existing Machines & Physical Building (MPF 0.80)

A condensed practical reference distilled from the MPF docs source (`dev` branch, current as of MPF 0.80 / GMC, April 2026): `docs/hardware/**`, `docs/machines/**` and `docs/physical_building/**`. Where the docs are outdated, contradict each other or are written for a specific MPF version, this file says so. Items marked **[CHECK]** are known doc inconsistencies you should verify against the config reference (`docs/config/*.md`) or the vendor's own docs before relying on them.

> **Big-picture version warning.** Most of the `docs/hardware` tree was written between MPF 0.33 and 0.57. Very little of it was touched for 0.80. Specifically:
> - **FAST:** everything under `hardware/fast/` is labelled **"Pre-2024 Documentation"** and covers the **FAST Nano with MPF ≤ 0.56**. For the **Neuron / Retro controllers on 0.57+ / 0.80**, the docs send you to **fastpinball.com/mpf**. The only 0.80-era FAST material in the tree is the config reference (`docs/config/fast.md`, `config/fast/fast_net.md`, `fast_exp.md`, `fast_exp_board.md`, headed "2026 Documentation Update… relevant for MPF 0.57.5 and 0.80.0"). Section 4.1 below summarises it.
> - **Displays:** every physical DMD / RGB DMD example (`dmds:`, `rgb_dmds:`, `slides:`, `slide_player:`, `window:`, widget `effects: dmd/color_dmd`) is written for the **legacy Kivy MPF-MC** (0.57 and earlier). The GMC docs in this tree only cover *virtual* DMD look filters (`virtual_dmd`, `dmd_dots`, `pixelate` in `gmc.cfg`). They do not explain how GMC feeds a physical DMD. **[CHECK]** before you plan on a physical DMD with 0.80.
> - **Keyboard:** `hardware/virtual/keyboard.md` documents the MPF-MC `keyboard:` YAML section. In 0.80/GMC, keyboard mapping lives in `gmc.cfg` under `[keyboard]` (see `docs/gmc/keyboard.md`, and the summary in §4.9).
> - Many examples still carry `#config_version=5`. Newer ones (FAST cabinet board, OPP Combo) use `#config_version=6`.

---

## 1. Core hardware concepts

### 1.1 How MPF talks to hardware
- MPF itself is hardware-independent. It runs on a host PC (Windows/Linux/Mac, or an SBC) and talks to a **pinball controller** over USB/serial (or the network for LISY/RPi). The controller drives the driver boards, switches, lights and displays.
- The game code is portable across platforms. The docs show a P-ROC being swapped for a FAST controller in 3 minutes while the same game code keeps running. Only the `hardware:`/platform sections and the `number:` values change.
- **Platform code is owned by the hardware vendors.** For example, FAST maintains `mpf/platforms/fast` and CobraPin/OPP maintain `mpf/platforms/opp`. Take feature, support and documentation requests to the vendor, not to the MPF maintainers. Vendor-maintained sections carry the `hardware_platform.md` banner ("This section is maintained by the hardware maker").

### 1.2 Hardware rules (flippers, pops, slings: "quick response" devices)
**Why:** the full round trip (switch scan → USB → MPF → decide → USB → controller fires coil) takes about 10–20 ms. That is too slow for flippers, pop bumpers, slingshots, kicking targets, kickbacks and diverters.

**Fix:** MPF writes simple **hardware rules** to the controller (for example "when switch X closes, pulse coil Y"). The controller then acts on its own, usually within 1–2 ms.
- Rules are **not stored permanently**. MPF adds, removes and updates them all the time. Flipper rules, for example, are added at ball start and removed at ball end.
- The switch event **still reaches MPF**, so scoring and sounds work. The coil has simply already fired.
- It is **automatic**. You configure `flippers:` and `autofire_coils:`, and MPF writes the rules.

Rule types MPF uses:

| # | Rule | Used for |
|---|------|----------|
| 1 | Pulse + Cancel (pulse on activate, cancel on release) | Main (power) winding of dual-wound flippers |
| 2 | Pulse + Cancel + Hold (pulse, then PWM hold, cancel on release) | Single-wound flippers. Hold winding of dual-wound flippers, often at 100% PWM |
| 3 | Just Pulse (never cancelled) | Pop bumpers (and slings) |
| 4 | Pulse + Cancel + Hold + EOS (switch to PWM hold when the normally-closed EOS opens) | Flippers with EOS switches (dual-wound with hold = 0) |

On most platforms rule 1 is simply rule 2 with hold power 0. When a platform lacks a rule type, MPF falls back to the nearest one.

**Platform constraints on hardware rules (important for wiring layout):**
- **FAST Nano (legacy):** the switch and the coil must be on the **same I/O board**. The exception is the "priority" switches `0-0`…`0-7` (the first 8 switches on the first board in the loop), which can trigger drivers on any board. Put the flipper buttons there. **The FAST Neuron has no such restriction:** any switch can drive any driver.
- **CobraPin/OPP:** the switch and the coil of an autofire device must be on the **same microcontroller**. The first digit of the number must match, e.g. a coil on `0-x-y` needs a switch on `0-a-b`.
- **System 1/80 (LISY), LISY35, System 11 (Snux):** these use a physical **flipper/game-over relay** instead of software rules. You enable it through a `digital_outputs:` entry (§5).
- **Raspberry Pi (pigpio):** hardware rules are **not supported**, so it is not a real pinball controller.

### 1.3 Choosing platforms: `hardware:` and mixing platforms
Three levels of platform selection:

```yaml
# 1. Machine-wide default
hardware:
  platform: p_roc
  driverboards: pdb

# 2. Per device-class default (overrides #1 for that class)
hardware:
  platform: p_roc
  driverboards: pdb
  lights: fadecandy
```
Device-class keys listed in `platform.md`: `coils`, `switches`, `matrix_lights`, `lights`, `dmd`, `rgb_dmd`, `gis`, `flashers`, `servo_controllers`, `accelerometers`, `i2c`. The config reference (`config/hardware.md`) also lists `segment_displays`, `stepper_controllers` and `hardware_sound_system`. **[CHECK]** `matrix_lights`/`gis`/`flashers` look legacy, since lights are unified in `lights:` with `subtype:`.

```yaml
# 3. Per-device override
hardware:
  platform: fast
lights:
  led00:
    number: 0-0          # FAST number
  led01:
    number: 0            # FadeCandy number
    platform: fadecandy
```

- `platform:` can be a **list**, e.g. `platform: your_platform, spi_bit_bang` (from the SPI bit-bang doc).
- `driverboards:` values from `config/hardware.md`: `pdb`, `fast`, `opp`, `wpc`, `wpc95`, `wpcAlphaNumeric`, `sternSAM`, `sternWhitestar`. OPP examples use `gen2`. **[CHECK]** The docs are inconsistent about where `driverboards:` lives. `platform.md` and `hardware.md` put it under `hardware:`, the P-ROC and FAST guides put it under `p_roc:` / `fast:`, and the config reference says the per-platform key is for when you mix platforms. Both forms appear in working examples.
- **Default platform [CHECK]:** `config/hardware.md` says `platform:` defaults to `virtual`, but `virtual/smart_virtual.md` says that with no `platform:` (or no `hardware:` section) MPF uses **smart_virtual**.

### 1.4 `number:` settings: where to look
Every physical device has a `number:` whose format depends on the platform. `hardware/numbers.md` is only a link index. The per-platform formats are collected in the **cheat-sheet in §3** below.

### 1.5 Light numbers vs channels (applies to all LED platforms)
- A light is made of one or more channels. For example, a white GI has 1 white channel, an RGB LED has R/G/B, and a white LED under a red insert should be a single **red** channel.
- `number:` gives the platform's default light layout (usually RGB for serial LEDs).
- For RGBW or mixed chains, use **`start_channel:` + `type:`**, and **`previous:`** to chain lights so MPF calculates the channel numbers:

```yaml
lights:
  led_0:
    start_channel: 0-0
    subtype: led
    type: rgb
  led_1:
    previous: led_0
    subtype: led
    type: rgbw
```
- Explicit per-colour channels are also possible:
```yaml
lights:
  left_lane_arrow_rgb:
    channels:
      red:   {number: 1-10}
      green: {number: 1-11}
      blue:  {number: 1-12}
```
- Use `light_settings: color_correction_profiles:` if LEDs look pinkish or bluish at white. FadeCandy prefers its own hardware correction.

### 1.6 Host computer (from `computer.md`)
- MPF runs anywhere Python 3 runs. The doc still says MPF-MC needs working OpenGL (a legacy MC note) and warns that OpenGL can misbehave in VMs.
- MPF uses 2 processes (game engine plus media controller), so ≥2 cores is recommended and 4 is better. **Dev box:** 4+ cores, 8 GB+ RAM, SSD. **Final game:** 2–4 cores, 2–4 GB RAM, SD/eMMC/SSD. "Do not use such a setup for game development."
- Consider a journaling filesystem or a read-only mount to survive unsafe power-offs. A 64-bit OS is needed for more than 2 GB of assets per process.

---

## 2. Supported controller platforms: comparison

"Primary" means it can be your main switch/coil controller. The hardware index says "pick one of these three" but then lists seven. **[CHECK]** That is a stale sentence.

| Platform | What it is | Connection | Key config | Strengths | Caveats |
|---|---|---|---|---|---|
| **FAST Pinball** (Neuron, Nano, Retro WPC/Sys11) | Commercial controller + I/O boards in a loop. EXP bus for LEDs/servos/motors/steppers. Smart Power Filter. Audio interface | USB (virtual COM ports) | `hardware: platform: fast`, `fast:` (0.80: `fast: net:`, `exp:`, `exp_int:`, `aud:`) | Fast hardware rules (Neuron: any switch → any driver), pulse power, precise debounce/recycle, UL/CE-minded wiring guides | Docs in this tree are Nano/≤0.56. Neuron/0.80 docs are on fastpinball.com. Support via FAST Slack |
| **Multimorphic P-ROC** | Controller for existing machines (WPC, Stern SAM/Whitestar, Sys11 via Snux) or with PDB boards | USB (FTDI D2XX, libpinproc/pypinproc) | `platform: p_roc`, `p_roc: driverboards: pdb/wpc/...` | Drives mono DMD (14-pin), 4 alpha displays, matrix plus direct switches | Needs the FTDI driver stack. P-ROC can't combine hold power and pulse power. Recycle is on/off only (64 ms) |
| **Multimorphic P3-ROC** | Homebrew controller: SW-16 switch boards, PD-16/PD-8x8/PD-LED driver boards on serial buses | USB | `platform: p3_roc`, `p_roc:` section (yes, `p_roc:`) | Up to 256 switches, accelerometer, I2C port, burst optos, servos/steppers on PD-LED | Driver bus is one-way (MPF can't detect PD-16/PD-LED). Address and termination DIPs are easy to get wrong |
| **OPP** (Open Pinball Project, Gen2) | Open-source/open-hardware STM32 boards with wing cards (solenoid, input, incandescent, matrix, LED) | USB-CDC serial (`/dev/ttyACMx`) | `platform: opp`, `driverboards: gen2`, `opp: ports:` | Cheap, flexible | Bare-bones, needs time and skill. Autofire switch and coil must share a microcontroller |
| **CobraPin** (OPP-based) | All-in-one board: 24 solenoids (3 banks), 38 direct or 22 direct + 8x8 matrix inputs, 2 Neopixel chains (512 RGB), built-in power filter and fuses | 2× USB (two STM32 "Blue Pills") | same as OPP | Easiest OPP entry. Silkscreened MPF numbers. Per-coil and per-bank LEDs | Getting the two MCUs' board order wrong makes the silkscreen numbers wrong |
| **OPP EM Combo** (O16I16, O32) | Community OPP fork for digitising EM machines (Blue Pill Plus) | USB, one MCU per board | `platform: opp`, many ports | Cheap EM retrofits (proven on a 1975 Gottlieb Fast Draw) | Configure with `gen2test.py`. Firmware fork 2.4.0.0 |
| **Stern SPIKE / SPIKE 2** | Existing Stern machine (2015+). SD card modified to run the MPF SPIKE bridge | USB-serial to the CPU node (DBGU/CN2, or USB null-modem) | `platform: spike`, `spike: port/baud/runtime_baud/flow_control/nodes` | No controller to buy. Swap SD cards to go back to stock | **Experimental.** Risk to warranty and SD card. No SPIKE sound, servos or WWE LCD |
| **LISY** (LISY1, LISY80, LISY35) | RPi-Zero-based MPU replacement for Gottlieb Sys1/80/80A/80B and Bally/Stern AS-2518-17/-35 | Serial (USB) or network (WiFi/Ethernet). MPF can even run on the LISY itself ("master") | `platform: lisy`, `lisy: connection: serial/network` | Keeps original sounds (hardware sound) and segment displays. PinMAME still available | No hold/pulse power (always 100%). Flippers via game-over relay. Master mode can't run a media controller |
| **APC** (Arduino Pinball Controller) | Replaces CPU and driver board in Williams Sys3–Sys11c. Can also build full custom machines | USB (Arduino serial), **LISY protocol** | `platform: lisy`, `lisy: connection: serial` | One board does everything. Segment displays, sounds | Configured as LISY. See the APC GitHub for the hardware |
| **Penny K PKONE** | Nano controller + Extension boards (switches/coils/servos) + Lightshow boards (WS281x/simple LEDs), CAN-style chain | USB (STM VCP) | `platform: pkone`, `pkone: port:` | Pulse power, recycle_ms, servos, RGBW firmware | Sparse docs (config page still has a TODO) |
| **Virtual / Smart Virtual** | Software-only | — | `platform: virtual` / `smart_virtual`, or `-x` / `-X` | Develop without hardware. Smart virtual simulates ball movement and drop-target resets | — |
| **Virtual Pinball (VPX)** | Visual Pinball table as simulated hardware (Windows) | COM bridge `mpf-vpcom-bridge` | `platform: virtual_pinball` or `--vpx` | Physics-level testing | Windows only. Heavy VBScript work |

**Add-on / peripheral platforms (combine with a primary):**

| Add-on | Purpose | Platform key |
|---|---|---|
| FadeCandy | 512 WS2812 per board (8×64). Up to 4 boards | `lights: fadecandy` |
| SmartMatrix / RGB.DMD / FAST RGB DMD (Teensy-based) | RGB LED DMD | `rgb_dmd: smartmatrix` |
| PIN2DMD | 128x32 or 192x64 RGB DMD over USB (pyusb) | `rgb_dmd: pin2dmd` |
| Raspberry Pi DMD (hzeller rpi-rgb-led-matrix) | RGB matrix on RPi GPIO | `platform: rpi_dmd` (per the doc example) |
| Pololu Maestro | 6/12/18/24 servos over USB | `servo_controllers: pololu_maestro` |
| PCA9685/PCA9635 I2C servo boards | Servos over I2C | `servo_controllers: i2c_servo_controller` |
| Pololu Tic | 1 stepper per USB Tic (needs `ticcmd`) | `stepper_controllers: pololu_tic` |
| Trinamic StepRocker | Steppers over USB | `stepper_controllers: trinamics_steprocker` |
| StepStick/DRV8825 | Stepper driven by two or three `digital_outputs` (slow: ~50–200 steps/s) | `stepper_controllers: step_stick` |
| Native Linux I2C (smbus2_asyncio) | Any I2C bus | `i2c: smbus2` |
| MMA8451 accelerometer | Tilt/leveling over I2C | `accelerometers: mma8451` |
| Raspberry Pi (pigpio, local or remote) | GPIO in/out, servos, I2C (not a real pinball controller) | `platform: rpi` + `raspberry_pi:` |
| MyPinballs / PBL TNA displays | Bally-style or TNA segment displays over serial | `segment_displays: mypinballs` |
| Light segment displays / NeoSeg | Segment displays built from lights on any platform | `segment_displays: light_segment_displays` |
| OSC | Lights out, switches and events in over Open Sound Control (needs `python-osc`) | `platform: osc` |
| SPI bit-bang | Read shift-register switch boards (e.g. Stern SPIKE trough) from any platform | `spi_bit_bang` |
| Snux | System 11 driver board with a P-ROC/FAST WPC (legacy, likely unavailable) | `coils: snux`, `switches: snux` |

Existing-machine support matrix (from `machines/index.md`, simplified; see the contradictions noted in §5):

| Machine | FAST | P-ROC | LISY | Direct | Other |
|---|:-:|:-:|:-:|:-:|---|
| WPC / WPC-S / WPC-95 | ✅ (Retro) | ✅ | | | |
| System 11/11A/B/C | ✅ (Sys11 Retro) | (with Snux) | | | APC |
| Data East | | (with Snux) | | | |
| Stern SAM, Whitestar | | ✅ (not P3-ROC) | | | |
| Pinball 2000 | | libpinproc-compatible board "by Jimmy" | | | |
| Stern SPIKE / SPIKE 2 | | | | ✅ | |
| Gottlieb Sys1 / Sys80 | | | ✅ | | |
| Bally/Stern AS-2518-17/-35 | | | ✅ (LISY35) | | |
| Williams Sys 3–9 | | | | | APC |

---

## 3. Numbering cheat-sheet

| Platform | Switches | Coils/drivers | Lights |
|---|---|---|---|
| FAST Nano (≤0.56) | `board-input`, e.g. `0-0`, `2-24` (board 0 = first after the controller's OUT port) | `board-driver`, e.g. `0-0`, `2-14` | LED `number` 0–255 (chains 0–63, 64–127, 128–191, 192–255) or channel `led-index` |
| FAST Neuron (0.57+/0.80) | `<io_loop board name>-<index>`, e.g. `cabinet-0` | `cabinet-7` | EXP: `<board name>-<port>-<led>`, e.g. `neuron-1-1` |
| FAST Retro / WPC | from the manual (see WPC) | | matrix lights from the manual |
| P-ROC (PDB) | Direct `SD0`–`SD31`. Matrix `col/row`, e.g. `3/4` | `Ax-By-z`. Local PDB drivers 0–31 | Matrix: `C-A2-B0-0:R-A2-B1-0` (defaults to `subtype: matrix`) |
| P3-ROC | `A<sw16>-B<bank>-<in>`, e.g. `A2-B1-5`, or raw `addr*16 (+8 for bank B) + in`. `burst-<sw>-<drv>`. `direct-N` | `Ax-By-z` (PD-16). `direct-N` | PD-LED `board-r-g-b`, e.g. `8-0-1-2`. Channel `8-0`. Serial on PD-LED v2: offset 100/250/400 |
| OPP | `card-switch` (wing 0 → 0–7, wing 1 → 8–15, …). Matrix 32–95 | `card-coil` (wing 0 → 0–3, wing 1 → 4–7, …) | Incandescent `card-bulb` (`subtype: matrix`). LED `chain-card-index` |
| CobraPin | `mcu-0-N` as silkscreened, e.g. `0-0-27`. Matrix `1-0-32`…`1-0-95` | `0-0-8`, `1-0-1` (silkscreened) | `0-0-###` (NEO0), `1-0-###` (NEO1) |
| SPIKE | `node-id` from the manual (drop the `SW`), e.g. `11-4` | `node-id` (drop the `DR`), e.g. `8-0` | `node-id` (drop the `LP` and lowercase node letters), e.g. `8a-LP-47` → `8-47`. Backlight `0-0` |
| PKONE | `addr-input`, e.g. `0-0` (addr 0–7) | `addr-driver` 1–10 | Simple `addr-N` (`subtype: simple`). WS281x `addr-group-index` (`subtype: led`) |
| LISY / APC | Manual numbers (LISY1 special: SLAM 76, outhole 66, reset 56) | Manual numbers. Coils on the lamp bank: +100 | Manual numbers |
| WPC (P-ROC/FAST) | `S11`–`S88` (`S9x` for a 9th column). `SD1`…. `SF1`–`SF8` | `C01`…. Fliptronics `FLRM/FLRH/FLLM/FLLH/FURM/FURH/FULM/FULH` | `L11`…, GI `G01`… |
| System 11 (Snux) | `S<col><row>` | `C01A`/`C01C` (A/C side), `C09` | `L<col><row>` |
| FadeCandy | — | — | `N` (sequential, 64 per connector) or `opc_channel-N` with an fcserver map |
| Pololu Maestro | — | — | servo `number` = channel 0…N |
| Virtual examples | anything, e.g. `s31` | `c01` | — |

---

## 4. Per-platform setup essentials

### 4.1 FAST Pinball

**Version split (from `fast/index.md`):**
- **FAST Neuron with MPF 0.57.0 and newer:** see fastpinball.com/mpf (maintained by FAST).
- **Classic FAST Nano with MPF 0.56.0 and older:** the in-tree docs apply.

#### 4.1a FAST Neuron / 0.80 (from `docs/config/fast*.md`, "2026 Documentation Update")
```yaml
hardware:
  platform: fast

fast:
  net:                       # IO network: switches + drivers
    controller: neuron       # neuron | nano | sys11 | wpc89 | wpc95
    port: auto               # default "auto"
    io_loop:                 # max 9 boards; Playfield Interchange board is pass-through, not listed
      cabinet:
        model: FP-I/O-0024
        order: 1             # starts at 1
      playfield_a:
        model: FP-I/O-3208
        order: 2
  exp:                       # expansion bus: LEDs, servos, motors, steppers
    port: auto
    boards:
      neuron:
        model: FP-EXP-2000   # the Neuron's own LED ports
      playfield_0081:
        model: FP-EXP-0081
  # aud: ...                 # FAST Audio board
```
- Device numbers use the io_loop board **name**, e.g. `number: cabinet-0` for switch 0 on the board named `cabinet`, and `cabinet-7` for driver 7 (from the FAST-recommended 0024 cabinet config). EXP LEDs are `board-port-led`, e.g. `neuron-1-1`.
- EXP models supported as of 0.57.4, with default addresses: `FP-EXP-2000` (48), `-1313` shaker (30), `-0051` DC motors (D0), `-0061` steppers (90), `-0071` servos (B4), `-0081` 2×4 LED headers (84), `-0091` (88). For several boards of the same model, set the solder jumpers (J0 = +1, J1 = +2, so up to 4 of one model) and add `address:`.
- **Raspberry Pi connected directly to a Neuron:** the Neuron's LED headers are not on the normal EXP bus. Move the `FP-EXP-2000` definition under `fast: exp_int: boards:`.
- LED ports default to 32 WS2812 RGB LEDs per port, with at most 128 per group of 4 ports. Custom `led_ports:` (`count`, `type: sk6812|mixed`, `rgbw_numbers`) **requires EXP firmware 0.48 and MPF `0.58.0.dev1`/`0.81.0.dev1`**, so it is *not* in 0.80.0. Upgrade EXP firmware to 0.48 in preparation (mandatory on 0.58/0.81). On FAST, SK6812 RGBW units are configured as `type: rgb`/`grb`, and W is derived as the floor of R, G and B.
- `fast: net:` settings: `watchdog` (**[CHECK]** listed as "Default: 500", the text says 1 s, and a note says the default *until 0.58/0.81* was 1000, which would make it 1000 on 0.80), `default_{quick,normal}_debounce_{open,close}` (mpfconfig defaults: quick 2 ms, normal **10 ms** here versus 4 ms in the old Nano doc), `mute_unconfigured_switches` (new in 0.57.4; unconfigured switches now report unless this is true), `gi_hz`/`lamp_hz` (30, for Retro GI/matrix subtypes). `soft_power_hold_ms` and `soft_power_powerdown_delay` are **new in 0.81** (not 0.80).
- **FAST 0024 cabinet I/O board recipe (FAST-recommended, `config_version=6`):** coin door on J4 (`cabinet-0`…`cabinet-7`, tagged `service_esc/down/up/enter`, `service_door_open`, `slam_tilt`), flippers `cabinet-8/9` and `cabinet-16/17`, start `cabinet-10`, tilt bob `cabinet-11`, launch `cabinet-18`. The low-current drivers L0/L1/L3 are "always-on" open drains (`allow_enable: true` plus `enable_events: enable_always_on_drivers`, posted from `event_player` on `mode_attract_started` and `game_started`). L2/L4 drive button lamps via a `platform: drivers` light:
```yaml
coils:
  c_start_light_driver:
    number: cabinet-2   # L2
    allow_enable: true
lights:
  l_start:
    number: c_start_light_driver
    platform: drivers
    type: w
```
- Power: the Neuron pairs with the **Smart Power Filter Board** (real-time current/voltage monitoring, fuse detection, remote power control). The Nano uses the plain Power Filter Board. FAST's wiring guides (fastpinball.com/wiring/neuron, ~30 guides) aim at UL/FCC/CE-compliant builds, and the MPF docs recommend them even for non-FAST builds.

#### 4.1b FAST Nano / legacy (MPF ≤0.56; still the content of `hardware/fast/*`)
```yaml
hardware:
  platform: fast
fast:
  driverboards: fast          # or wpc for WPC/Snux driver boards
  ports: com4, com5           # Nano: 2nd (NET) and 3rd (RGB) of the 4 ports
  watchdog: 1000              # ms, 0 disables; NET processor only
```
- The Nano shows 4 COM ports: 1st custom/DMD, **2nd NET**, **3rd RGB**, 4th unused. Core/WPC: list the first three. MPF queries each port to find out what is on it. On Linux they appear as `/dev/ttyUSB0-3`, on Mac as `/dev/tty.usbserial-xxxA-D`. Before Windows 10, COM ports above 9 need `\\.\COM10`.
- There are no USB serial numbers, so to pin ports to physical USB sockets use a udev rule on `ID_PATH_TAG` (`udevadm monitor --property`).
- Coils: `default_pulse_power:` (0–1) during the pulse, combinable with `default_hold_power:`. `recycle: true` sets the recycle time to 2× the pulse time. Or set `platform_settings: recycle_ms: 100`.
- Switch debounce: 1 ms scanning. Per switch via `platform_settings: debounce_open: 5ms`, `debounce_close: 20ms` (1–255 ms). Globally via `fast: default_normal_debounce_open:` etc.
- Nano LEDs: 4 chains × 64 RGB. The next chain starts at 64/128/192 even when earlier chains are short. Tuning: `mpf: default_light_hw_update_hz: 50` (try 30) and `fast: rgb_buffer: 3`. `fast: hardware_led_fade_time:` fades LEDs in hardware (default 0).
- Legacy servos on the I/O-board servo daughterboard: 6 slots reserved per board (board 0 → 0–5, board 1 → 6–11…) entered **in hex** unless `fast: config_number_format: int`. *Modern FAST servos use EXP boards instead.*
- RGB DMD: FAST's RGB DMD is a SmartMatrix-type device (`hardware: rgb_dmd: smartmatrix`, `smartmatrix: smartmatrix_1: port: com12, baud: 4000000, old_cookie: false`). **[CHECK]** `fast/rgb_dmd.md` says baud 4000000 but `smartmatrix.md` says "If you are using the FAST DMD board set baud to 3000000".
- Burned FET (a coil stuck on, fuse blows): replace with `IRL540NSTRLPBF`, or contact FAST.
- Matrix lights on FAST are only available on the **Retro** controllers, using the numbers from the manual.

### 4.2 Multimorphic P-ROC / P3-ROC
**Install drivers first:**
- **Windows x64:** FTDI D2XX setup, then copy `ftd2xx64.dll` to `C:\Windows\System32` and rename it `ftd2xx.dll`. Also install the VC++ 2019 x64 redistributable.
- **Windows x86:** the D2XX setup exe plus the VC++ redistributable.
- **Linux:** the MPF Debian installer, choosing "P3 or P-ROC".
- **Mac:** brew `libftdi libusb-compat cmake`, yaml-cpp 0.2.5 from `osx-proc-support`, `libpinproc` (dev branch), MPF's Python 3 `pypinproc`, `D2xxHelper`, then reboot.

```yaml
hardware:
  platform: p3_roc          # or p_roc
p_roc:                      # same section name for both boards
  driverboards: pdb         # wpc / stern... for existing machines
  use_watchdog: true
  watchdog_time: 1s
  # lamp_matrix_strobe_time: 100ms   # tune for LED lamp-matrix bulbs
  # debug: true
  # trace_bus: true                  # logs every libpinproc call (slow)
```
- **Switches (P-ROC):** direct `SD0`–`SD31` plus an 8x8 matrix, *or* `SD8`–`SD31` plus an 8x16 matrix. Using any matrix row > 7 silently takes SD0–SD7, and there is no error check. Optos must go on direct inputs, which are always powered. Direct inputs are not faster than matrix inputs.
- **Switches (P3-ROC):** up to 16 SW-16 boards (256 direct switches, no matrix). `number: A0-B0-0`. Bank A pins: rev 1 = 1, 3–9 / bank B 1, 2, 4–9; rev 2 = pins 2–9 with ground on pin 10 of J2/J6 and a low-current 12 V on pin 1.
- **Debounce:** on by default. `debounce: quick` disables it and `normal` forces it (`auto` also exists).
- **Coils:** `A<addr 0-31>-B<bank 0/1>-<out 0-7>`, where the output number is **logical, not the pin number**. `default_pulse_power` and `default_hold_power` **cannot be used together** on P-ROC/P3-ROC. Hold power becomes PWM on/off ms (0.5 → 1 ms on / 1 ms off). Recycle ("reload") is fixed at 64 ms and can only be switched with `default_recycle: true/false`.
- **P3-ROC burst I/O (firmware ≥ 2.6):** with DIP 1 on, `direct-N` outputs (give PD-16s IDs ≥ 2). With DIP 2 on, `direct-N` inputs (give SW-16s IDs ≥ 4). With DIPs 1 and 2 off, burst optos `burst-<sw>-<drv>` (up to 5 switches per driver; these need 40 kHz IR emitter/receiver PCBs PCBA-0011-0002 / PCBA-0003-0003, and ordinary optos will not work). There is no initial-state read for burst optos, which MPF assumes open. **Burst pins are unprotected 3.3 V logic:** anything above 3.3 V or below 0 V destroys the P3-ROC.
- **Matrix lamps (PD-8x8):** `number: C-A2-B0-0:R-A2-B1-0`. `subtype: matrix` is needed on the P3-ROC, where the default is `led`.
- **PD-LED:** 84 outputs at 22 mA, 3.3 V. `number: 8-0-1-2` (board-r-g-b). `subtype: led` is needed on the P-ROC, where the default is `matrix`. `platform_settings: polarity: true` = common cathode. DIP 6 sets the power-on state. Amplify with a logic-level N-FET on common ground. **PD-LED v2** adds serial WS281x/LPD880x chains (`p_roc: pd_led_boards: 4: use_ws281x_0: true`, channel offsets 100/250/400). **PD-LED v3** adds 12 servos (`use_servo_N`, `max_servo_value: 300` ≈ 2 ms, which takes LEDs 72–83; keep DIP 6 **OFF**) and 2 steppers (`use_stepper_0/1`, a StepStick driver, a homing switch per stepper, takes LEDs 75–80; `stepper_speed` where higher is slower).
- **Other features:** the P3-ROC accelerometer (`accelerometers: p3_roc_accelerometer: number: 1`), the P3-ROC I2C port J17 (SDA/SCL/GND), P-ROC alphanumeric displays 0–3 (`segment_displays: display1: number: 0`), and a P-ROC 14-pin mono DMD with 16 shades (`dmds: my_dmd: shades: 16`; leave `p_roc: dmd_timing_cycles` alone because bad values can damage the DMD). There is no native RGB DMD, so add a SmartMatrix/RGB.DMD.
- **Bus wiring (P3-ROC):** switch bus J11/J14 and driver bus J12/J15, daisy-chained, **+ to + and − to −**, twisted pair. Terminate the **last board of each chain** (DIP 8 ON) and set P3-ROC DIPs 7 and 8 ON for the switch bus. There is only **one** logical switch bus and one driver bus, so addresses must be unique across both connectors. **A PD-16 and a PD-LED sharing an address can fire coils from LED commands.** DIP addressing is binary with DIP 1 as the LSB (SW-16 uses DIPs 1–6, PD-LED 1–5, PD-16 1–4). The watchdog LED (PD-LED D3, PD-16 D11) goes off while MPF is talking, and flickering while you wiggle a cable reveals a bad cable.

### 4.3 OPP (Open Pinball Project) and CobraPin
```yaml
hardware:
  platform: opp
  driverboards: gen2
opp:
  ports: /dev/ttyACM0, /dev/ttyACM1   # Windows: COM7 ; Mac: /dev/cu.modemXXXX
  # chains: {0: /dev/ttyACM0, 1: /dev/ttyACM1}   # pin port->board
  # poll_hz: 50                       # default 100; lower only if boards can't keep up
```
- **Numbering [CHECK]:** `opp/switches.md` and `drivers.md` show two-part `card-number` (`0-15`, `0-12`), but the CobraPin, LED and Combo docs use three-part `chain-card-number` (`0-0-16`). Use whatever your board's silkscreen or `mpf hardware scan` shows. Switch wing *w* covers `8w`…`8w+7`. Solenoid wings use the first 4 input numbers of their wing (as switches) and coil numbers `4w`…`4w+3`. Incandescent wings use `8w`…`8w+7` (`subtype: matrix`). An 8x8 matrix (wing 2 input, wing 3 strobe) gives switches 32–95 (32–39 = column 0, …).
- **Coils:** hold power uses a fixed 16 ms PWM period (0.25 → 4 ms/16 ms). `default_pulse_power` needs firmware ≥ 2.3.0.5 (minimum 3.125%). Recycle is `default_recycle: true` plus `platform_settings: recycle_factor: 2` (recycle time = pulse × factor).
- **Linux quirks:** blacklist `cytherm` (`/etc/modprobe.d/blacklist.conf`), disable ModemManager, and add a udev rule to create stable symlinks (e.g. `/dev/ttyOPP1`). A real serial port must use 5 V signal levels.
- **CobraPin specifics:** the two STM32s appear as 2 ports. The silkscreen board numbers 0 and 1 must match the port order, or use serial numbers. For a second CobraPin, use serials 10/11, because 2 is used by the CobraPin Xpansion board. The docs warn that mixing up boards "could cause blown FETs, coils, and fuses", so test without coil power and watch the yellow coil LEDs. Coil power input J9 is 24–50 V. Bank fuses F1–F3 (5x20 mm): power bank A only from HV_A, and so on. Neopixel input J10 (5 V, or 12 V for 12 V pixels) with fuse F4. J14 is a fused 5 V tap (7 A per pin, 10 A holder). Switch inputs sit at 3.3 V: **never apply voltage to them.** Coils with axial diodes must observe polarity. The example sets `psus: default: release_wait_ms: 50`.
- **NeoSeg serial segment displays (CobraPin):**
```yaml
hardware:
  platform: opp
  driverboards: gen2
  segment_displays: light_segment_displays
neoseg_displays:
  neoSeg_0:
    start_channel: 0-0-0      # CHANNEL, not light number; 8-digit = 120 channels, 2-digit = 30
    size: 8digit
    light_template: {type: w, subtype: led, color_correction_profile: NeoSeg_orange}
segment_displays:
  neoSegTop:
    number: 1
    size: 16
    integrated_dots: true
    use_dots_for_commas: true
    platform_settings:
      light_groups: [neoSeg_0, neoSeg_1]
      type: 14segment
light_settings:
  color_correction_profiles:
    NeoSeg_orange: {whitepoint: [.9, .9, .9]}   # brightness per colour
```
  Overlapping `segment_displays` built from the same light groups are OR'ed together, so clear one (send an empty string) before writing to the other.
- **OPP EM Combo boards:** identify the board by serial number, not port. Numbers are `card_id-0-output`. Configure the wings with `gen2test.py --serial 0`, `--config opp16o16icfg.py`, `--save`.

### 4.4 Stern SPIKE / SPIKE 2 (experimental)
1. **Image and back up the original SD card** first, and work on a copy. Stern updates are deltas, so a broken card needs a replacement from Stern. Known-good card: SanDisk Ultra Plus 16 GB.
2. Mount the ext3 root partition (probably #3; use Paragon ExtFS on Windows or `fuse-ext2` on Mac). Edit `/etc/inittab` for passwordless serial login (`S0:2345:respawn:/sbin/getty 115200 ttyS0 -n -l /bin/sh`, and optionally a `USB0` line, with `-h` for hardware flow control). Add `/usr/local/bin/avrisp /usr/local/spike/netbridge.hex /usr/local/spike/netbridge.fuses` and `exit 1` as lines 2–3 of `/etc/rc2.d/S95game`. Copy `mpf-spike-bridge` to `/bin/bridge` with `chmod +x`. **Unmount cleanly.** If the red LED in the middle of the CPU board isn't blinking, the card may be corrupt.
3. Connect using one of: (1) an FTDI USB-to-USB null-modem cable (about $50, up to 3 Mbaud, cleanest); (2) a **3.3 V** USB-serial adapter on DBGU/CN2 (GND/RX/TX; no flow control, so only up to roughly 400k; the header is missing on newer boards); (3) two USB-serial adapters back to back (the one on the SPIKE side must be a genuine FTDI; cross RX/TX and RTS/CTS, the doc says "CTS to DTS").
```yaml
hardware:
  platform: spike
spike:
  port: /dev/ttyUSB0
  baud: 115200            # initial; must match the inittab getty speed
  runtime_baud: 2000000   # switched after bridge starts; DMD needs ~1.5-2 Mbaud
  flow_control: true      # required above ~0.5 Mbaud
  nodes: 0, 1, 8, 9, 10, 11   # node addresses from the manual; treat 8a/8b as 8
  # bridge_debug: true
  # bridge_debug_log: /mnt/spike.log
```
- Numbers come straight from the manual: switches `11-0`, drivers `8-0` (`8-DR-0`), lights `8-47` (`8a-LP-47`), backlight `0-0`. GI and flashers are ordinary `lights:`. Optos need an inverted type. **[CHECK]** The text says `type: NO` but the example uses `type: false`.
- Steppers: up to 4 per node, e.g. `number: 10-0` with `platform_settings: {speed: 20, light_number: 10-10}` and a homing switch.
- DMD (SPIKE 1 mono): `dmds: my_dmd: platform: spike, fps: 30`.
- **Not supported:** SPIKE sound (use the PC's sound output), servos, the WWE LE playfield LCD. You cannot reuse Stern's rules or assets. MPF means a full rewrite. It may void your warranty.

### 4.5 LISY (Gottlieb System 1/80, Bally/Stern AS-2518) and APC
- Needs LISY firmware 4.02+. Replace the MPU with the LISY1/LISY80/LISY35 board. Set the game number on DIP bank S2 in binary (e.g. game 18 → DIPs 2 and 5 on).
- **Slave mode** (recommended during development): DIP 6 ON, then DIP 2 ON for network or OFF for serial. **Master mode** (MPF on the LISY's Pi Zero; no media controller, segment-display games only): DIP 4 and DIP 8 ON, all others off, with the config in `/boot/mpfcfg/LISY80/018/`. A USB connection powers the Pi, so unplug it to reboot.
```yaml
hardware:
  platform: lisy
lisy:
  connection: serial      # or: network
  port: com1              # /dev/ttyACM0 on Linux (LISY), /dev/ttyUSBx (APC)
  baud: 115200
  # network_host: a.b.c.d   (hostname "lisy", DHCP; IP shown on displays at boot)
  # network_port: 5963
```
- Coils: manual numbers. **No hold or pulse power: always 100%**, only the pulse length is adjustable. Coils wired to the lamp bank take +100. **[CHECK]** The doc's example says "light output 05 → coil 105" but its YAML shows `107`.
- Flippers, pops and slings: enable the **game-over relay**. LISY1/80 wire it as a light (`digital_outputs: game_over_relay: number: 1, type: light, enable_events: ball_started, disable_events: ball_will_end`). On LISY35 it is `type: driver, number: 16`.
- Switches: LISY1 has a 40-switch matrix plus SLAM 76 (logic already inverted), outhole 66 and reset 56. LISY80 has 64 matrix switches. Undocumented ones: 06/16 advance (80B), 07 play/test, 17/27/37 coins, 47 replay, 57 tilts. The Sys80 SLAM is not supported.
- Segment displays: `number: 0` (info) to `4`. Original sounds: `hardware_sound_systems: default: label: LISY`, then `hardware_sound_player:` with `play`, `play_file` (mp3s in `…/hardwaresounds`), `text_to_speech`, `set_volume`/`increase_volume`/`decrease_volume`, also usable in shows.
- **LISY protocol limits (also apply to APC):** 127 switches, 256 simple lamps, 256 lights, 256 coils (MPF uses 100), 7 displays, no error correction. The watchdog is sent every 500 ms and outputs turn off after 1 s without it.
- **APC:** select "USB Control" in APC and use the same `lisy:` serial config with a normal USB A-B cable. The example config also adds `game_over_relay` (light 1), `segment_displays` 0–4 and `hardware_sound_systems: default: label: APC`.

### 4.6 Penny K Pinball PKONE
```yaml
hardware:
  platform: pkone
pkone:
  port: com3            # Linux: /dev/ttyACM0 (doc typo "ttyASM0"); Mac: /dev/cu.usbmodem...
```
- Chain: Nano OUT → board IN → …. Each board has a unique Address ID: Extension 0–7, Lightshow 0–3, and an Extension and a Lightshow **must not share an ID**. Chain order does not matter. Set the CANBUS termination jumper on the last board.
- Switches `addr-input` (the doc says 1–35 but its example uses `0-0` **[CHECK]**). Inputs 31–35 are hardware-inverted for optos/NC, so **don't** mark them NC. Coils `addr-1..10` with `default_pulse_power`, `default_hold_power` and `platform_settings: recycle_ms`. Servos `addr-11..14` (not 1–4). Simple LEDs `addr-N` with `subtype: simple` (up to 45 per Lightshow). WS281x `addr-group(1-8)-index` with `subtype: led`, 64 per group, RGB or RGBW depending on Lightshow firmware. With `start_channel`/`previous`, `type:` is required.

### 4.7 Snux (System 11 with a P-ROC/FAST WPC controller; legacy)
The doc says "This board is most likely not available". It was a hobby kit by Mark Sunnucks ("Snux"). **Current alternatives for System 11:** the FAST System 11 Retro Controller, or APC.

Key System 11 concepts (still useful for any Sys11/Data East work):
- The flipper-enable relay feeds the flippers directly (EOS switch cuts the power winding).
- "Special solenoids" (pops/slings) fire through their own high-voltage skirt switches. The *matrix* switch only reports that the device fired.
- The **A/C relay** multiplexes drivers 1–8 between A-side devices (important playfield devices) and C-side devices (flashers, knocker).
- GI is **active-off**: enabling the driver turns the GI off.
- Troughs are two-device chains: outhole → trough → plunger (`confirm_eject_type: target`, `mechanical_eject: true`).

```yaml
hardware:
  platform: virtual       # [CHECK] the doc's own example; prose says platform p_roc
  driverboards: wpc
  coils: snux
  switches: snux
system11:
  ac_relay_delay_ms: 75           # 50 was too short on Pin*Bot
  ac_relay_driver: c_ac_relay     # config ref name; older prose uses ac_relay_driver_number: c14
snux:
  diag_led_driver: c_diag_led_driver    # C24 diag LED: solid=connected, 2 Hz blink=running
digital_outputs:
  flipper_enable_relay:
    number: c23
    type: driver
    enable_events: ball_started
    disable_events: ball_will_end
coils:
  c_diag_led_driver: {number: c24, default_hold_power: 1.0}
  c_ac_relay:        {number: c25, default_hold_power: 1.0}   # check the manual (C14 Pin*Bot, C12 Jokerz!)
  outhole:  {number: c01a}
  knocker:  {number: c01c}
```
- Lamps `L<col><row>` and switches `S<col><row>` come from the **matrix position**, not the manual's 1–64 numbers. **[CHECK]** The doc typo says "you actually enter L56" for a switch. It should be S56.
- `config/system11.md` also has `platform:` (the upstream platform), `ac_relay_switch`, `prefer_a_side_event` (game_ended) and `prefer_c_side_event` (game_will_start). The docs describe Snux support as "new" and not proven by a complete game.

### 4.8 Add-on platforms: quick configs
```yaml
# FadeCandy (fcserver must be running; MPF talks OPC to it)
hardware: {platform: p_roc, driverboards: pdb, lights: fadecandy}
lights:
  l_led0: {number: 0}      # connector 0, first LED; connector 2 starts at 128
# With an fcserver "map" giving each connector its own OPC channel: number: 1-0 etc.
# 4 FadeCandys max (2048 LEDs). If LEDs flicker after many MPF restarts, power-cycle the FadeCandy.

# SmartMatrix / RGB.DMD (Teensy 3.2/3.5 + SmartMatrix shield)
hardware: {rgb_dmd: smartmatrix}
smartmatrix:
  smartmatrix_1: {port: com12, baud: 2500000, old_cookie: false}   # RGB.DMD & FAST DMD: 3000000
rgb_dmds:
  smartmatrix_1: {hardware_brightness: .17, source_display: dmd}

# PIN2DMD (pip3 install pyusb); rgb_dmds entry MUST be named "default"
hardware: {rgb_dmd: pin2dmd}
pin2dmd: {resolution: 128x32, panel: rgb}   # or 192x64 / rbg
rgb_dmds:
  default: {hardware_brightness: .5, fps: 30}

# Raspberry Pi RGB matrix (rpi-rgb-led-matrix python bindings; run `sudo mpf game`)
hardware: {platform: rpi_dmd}
rpi_dmd: {cols: 32, rows: 32, gpio_slowdown: 2, pwm_lsb_nanoseconds: 300}
rgb_dmds:
  rpi_dmd: {source_display: dmd}

# Pololu Maestro (set "USB Dual Port" mode; use the FIRST/lower port)
hardware: {servo_controllers: pololu_maestro}
pololu_maestro: {port: /dev/ttyACM0}
servos:
  servo1: {number: 1, servo_min: 0.2, servo_max: 0.8, positions: {0.1: servo1_down, 0.9: servo1_up},
           reset_position: 0.5, reset_events: reset_servo1, speed_limit: 0.5, acceleration_limit: 0.5}

# I2C servo board (PCA9685/9635, default addr 0x40)
hardware: {servo_controllers: i2c_servo_controller}
servos:
  servo_on_controller_63_0: {number: 63-0}   # addr 0x3F, channel 0

# Native Linux I2C + MMA8451 accelerometer (pip3 install smbus2_asyncio)
hardware: {i2c: smbus2, accelerometers: mma8451}
accelerometers:
  my_accelerometer: {number: 1-29, level_x: 0, level_y: 0, level_z: 1}   # bus 1, addr 0x1D

# Raspberry Pi GPIO via pigpio (pip3 install apigpio_mpf; pigpiod service; Broadcom GPIO numbers)
hardware: {platform: rpi}
raspberry_pi: {ip: localhost, port: 8888}

# StepStick / DRV8825 driven by digital outputs; steps/s = 1000/(low_time+high_time)
hardware: {stepper_controllers: step_stick}
steppers:
  stepper1:
    number: c_direction:c_step:c_enable
    homing_mode: switch
    homing_switch: s_home
    platform_settings: {low_time: 20ms, high_time: 20ms}

# Pololu Tic (install ticcmd) / Trinamic StepRocker
hardware: {stepper_controllers: pololu_tic}     # or trinamics_steprocker (+ trinamics_steprocker: port:)

# MyPinballs / PBL TNA (PBL-600-0473-00) serial segment displays (up to 6)
hardware: {segment_displays: mypinballs}
mypinballs: {port: /dev/ttyUSB0}
segment_displays:
  display1: {number: 1}

# Segment displays built from any lights (BCD/parallel 7-seg, WS2811 serial segments)
hardware: {segment_displays: light_segment_displays}
segment_displays:
  display1:
    number: 1
    platform_settings:
      type: 7segment          # 7segment | 14segment | 16segment ...
      lights:
        - {a: segment1_a, b: segment1_b, c: segment1_c, d: segment1_d, e: segment1_e, f: segment1_f, g: segment1_g}

# OSC (pip3 install python-osc): in /sw/<name> and /event/<name>; out /light/<name>/<color> and events_to_send
hardware: {platform: osc}
osc: {remote_ip: 127.0.0.1, remote_port: 8000, events_to_send: [player_score]}

# SPI bit-bang (e.g. SPIKE trough on another platform)
hardware: {platform: "your_platform, spi_bit_bang"}
spi_bit_bang: {miso_pin: s_miso, cs_pin: o_cs, clock_pin: o_clock, bit_time: 50ms, inputs: 8}
```
Notes:
- **SPI bit-bang [CHECK]:** the doc gives the refresh rate as "`bit_time / (inputs + 2)`" but then says 8 inputs at 50 ms gives 2 Hz. That works out to 1 / (bit_time × (inputs + 2)). Expect about 250 ms average latency over USB.
- Segment display transitions (`none`, `push`, `cover`, `uncover`, `wipe`, `split`, with `direction`, `text`, `text_colors`, `mode`) are set with `transition:` / `transition_out:` in the `segment_display_player` or in shows. An incoming transition beats an outgoing one.
- Light segment displays have no colour or brightness support. Use light shows or a color_correction whitepoint instead.

### 4.9 Virtual / smart virtual / VPX / keyboard
- `platform: virtual` or `mpf -x`: switches change only when you drive them (keyboard, Monitor, OSC). A ball device eject will "fail" unless you move the switches by hand quickly.
- `platform: smart_virtual` or `mpf -X`: watches coil pulses. It moves balls out of ball devices into their `eject_targets` (the target switch activates about 100 ms later) and resets drop-target switches when their reset coil pulses. Options are under `smart_virtual:`. Pair it with **MPF Monitor**.
- **`-x`, `-X` and `--vpx` override your `hardware:` section.** Remove them when you connect real hardware. This is the #1 "hardware not working at all" cause.
- **VPX:** register the COM bridge with `python register_vpcom.py --register` (admin CMD) and set `platform: virtual_pinball` or run `mpf both --vpx`. In the table script: `Set Controller = CreateObject("MPF.Controller")`, an `MPFTimer` at 10–50 ms (well below your shortest `default_pulse_ms`), `Controller.Switch(n)=state`, `Controller.PulseSW(n)` for targets/slings/bumpers, and the `ControlledLamps` collection. Run order: start VPX as admin, then MPF, then the table. Exit by closing the table first.
- **Keyboard (0.80 / GMC):** configure it in `gmc.cfg`:
```ini
[keyboard]
1=["switch", "s_switch_1"]
enter=["switch", "s_start_button"]
x=["switch", "s_trough_6", "toggle"]
m=["event", "start_mode_multiball"]
```
  The `keyboard:` YAML section in `hardware/virtual/keyboard.md` (keys like `z: {switch: left_flipper}`, `toggle`, `invert`, `shift+p`, `debug: yes`) is the **legacy MPF-MC** mechanism (0.57 and earlier).

---

## 5. Working with existing machines vs homebrew

### 5.1 Three paths (from `machines/index.md`)
1. **Build from scratch** (homebrew).
2. **Rewrite the rules** of an existing machine (hardware unchanged, software replaced).
3. **Retheme:** keep the mechs and electronics, replace the artwork, write new rules.

For existing machines you usually swap the original MPU for a modern controller, which then drives the original driver boards. For unsupported machine types you rewire everything with modern control hardware: "homebrew on the inside, retheme on the outside".

### 5.2 WPC / WPC-S / WPC-95 (FAST Retro or P-ROC)
- Pull the MPU and plug the existing cables into the new controller. Switches go directly to the controller. Coils, lamps and GI go through the existing **power driver board** via the 34-pin ribbon. The sound board goes unused (sound comes from the PC; most people fit a new amp and speakers). The DMD plugs into the controller's 14-pin header, so the DMD driver board can be removed.
- **Critical P-ROC setting:**
```yaml
hardware:
  platform: p_roc
p_roc:
  driverboards: wpc     # FAST Retro: fast: driverboards: wpc  (0.80: fast: net: controller: wpc89/wpc95)
```
  With `driverboards: pdb` in a WPC machine the polarity is inverted. MPF "disables" every driver, which actually turns them **all on at once**, is very loud, and blows every fuse.
- Numbers come from the operator's manual and are not case-sensitive. Matrix switches are `S11`…`S88` (column/row, so no 0s or 9s; a WPC-95 9th column gives `S91`–`S98` and is auto-detected). Direct switches (coin door) `SD1`…`SD8`. Fliptronics `SF1`–`SF8`. Coils `C01`…. Fliptronics coils `FLRM`/`c29`, `FLRH`/`c30`, `FLLM`/`c31`, `FLLH`/`c32`, `FURM`/`c33`, `FURH`/`c34`, `FULM`, `FULH`. Lamps `L11`… with `subtype: matrix`. GI `G01`… with `subtype: gi`.
- About **25% of WPC manuals have wrong switch numbers** (usually two swapped). If a switch misbehaves, check its neighbours.
- **[CHECK]** Doc bugs on the WPC page: `FULM`/`FULH` are listed as "`s35`/`s36`" (probably `c35`/`c36`), yet the same page's example uses `c35` for a magnet. The text says flashers go in `flashers:`, but the example puts `f_claw: number: c17` under `coils:`.

### 5.3 Other existing machines
- **System 11/11A/B/C:** the FAST System 11 Retro Controller (drop-in; can also run the original ROMs), or P-ROC + Snux, or APC (optionally with LISY ROM emulation).
- **Data East:** Snux + a WPC-type controller (P-ROC, not P3-ROC). Untested per the Snux page.
- **Stern Whitestar / SAM:** P-ROC (not P3-ROC), wired per Multimorphic's P-ROC connector mappings PDF.
- **Pinball 2000:** a libpinproc-compatible board by "Jimmy", configured like a P-ROC.
- **Williams System 3–9:** APC, which replaces the CPU, sound and driver boards. You keep the playfield and PSU.
- **Gottlieb System 1 / 80:** LISY1 / LISY80. **Bally/Stern AS-2518-17/-35:** LISY35.
- **SPIKE / SPIKE 2:** direct connection (§4.4).
- **[CHECK]** The support table in `machines/index.md` is incomplete. It leaves P-ROC unticked for System 11, Data East, SAM, Whitestar and Pinball 2000, although the per-machine pages say P-ROC works.

### 5.4 Homebrew
- Controller choices named in the doc: FAST, CobraPin, Multimorphic P3-ROC, OPP, LISY Home, APC. FAST and Multimorphic are commercial. OPP is cheaper but bare-bones and needs time and skill. CobraPin makes OPP more accessible and is close to all-in-one. Add FadeCandy for WS2812 (FAST and P3-ROC have their own) and Pololu Maestro for servos.
- **Spend time on power and wiring at the start** (§6).
- Buy **mech assemblies** rather than parts, because a mech has many parts and assemblies are often cheaper (e.g. Pinball Life's homebrew section, Marco Specialties).
- CAD models for many components are at hardware.missionpinball.org, along with DIY PCB designs.

### 5.5 Physical building / layout (from `physical_building/*`)
- Play a lot of pinball first. Every switch hit should reward the player (light, sound or score). Think about where the "shot entered" and "shot made" switches go.
- **Pop bumpers:** surround them with rubber, not steel, and give them a defined exit. Steel and big gaps kill the action.
- **Upper flippers:** feed them from a ramp or orbit, and make access easy because shots from them are hard.
- **Inserts:** give every shot a dedicated insert. RGB arrows work as generic shot indicators, and lower inserts are mode-specific (e.g. Demolition Man).
- **Metal:** the ball should never hit metal except a ball guide, and guide ends need rubber posts. Orbits should return the ball toward a flipper, not onto a slingshot tip.
- **Shot lines:** every shot must be a straight line from a flipper. Allow half a ball diameter of clearance and check for backhands. A fan layout (7–8 shots) is common.
- **CAD:** overlay the playfield photo from an IPDB manual to borrow proven shot geometry. Draw trajectories for orbits, ball-lock exits and trap checks. Subtract the ball diameter (1.0625") from ramp and lane widths to get the effective opening (a 0.5" mini target can be easier to hit than a 2" ramp).

---

## 6. Power, wiring & safety

> **Common ground is non-negotiable.** Connect the logic ground (5 V/12 V) and the high-voltage coil ground (48 V/70–80 V). Otherwise coils can lock on, overheat, "burn down your house or kill you". This is the **most common cause of broken driver boards**. Use a power entry/filter board. **Turn all PSUs off before connecting power**, especially when a board has several supplies. The docs recommend a professional electrical engineer if you are unsure.

- **Mains (230/110 V):** check the PSU input range or selector switch. Traditional transformers must be wired for the local voltage. Fuse before the PSU or transformer.
- **Coil HV:** 48 V is recommended for new designs (typically 6–10 A). 70–80 V is legacy (heavier, harder to certify). 24 V works but gives weak, unreliable coils. Add large capacitors or a power entry board to keep the rail stable. If longer pulses make no difference, the voltage is sagging. Fuse the HV rail, ideally one fuse per bank. A coil enabled without PWM will burn, so use `default_hold_power`.
  - 48 V PSUs named: Meanwell SP320-48 (SPIKE, a bit weak), RSP500-48 (SPIKE 1 from Ghostbusters, SPIKE 2), SE-600-48 (Spooky). 70 V: AnTek PS-4N70R5R12.
- **Lights:** incandescent 12–24 V, LEDs 5 V (sometimes 12 V). Budget about 20 mA per LED and ×3 for RGB. The doc's example: 80 RGB inserts + 80 RGB GI ≈ 10 A / 50 W. Most connectors are rated under 10 A, so fuse it and size the wiring.
- **Displays:** RGB DMDs need 5 V or 12 V and several amps. A 128x32 SmartMatrix is 2 panels, which the doc calls "12,228 LEDs" (4,096 pixels × 3 = 12,288; **[CHECK]** arithmetic typo). Use a 5 V 10 A PSU. People run these panels at 17–25% brightness. Cut the Teensy VUSB trace before powering it externally. Traditional plasma DMDs use very high voltages, so ask a professional.
- **Logic:** 12 V for switches and 5 V for logic. Keep them separate from light and display power if interference is a problem. Fuse every rail.
- **EMI:** run supply and return wires in parallel at the same length, and fit flyback (free-wheeling) diodes on coils.
- **Grounding vs earth:** pinball machines are **Class 1 appliances** (IEC/EN 61140). Bond every exposed metal part (legs, backbox connector metal, speaker grills, lockdown bar, service door, cabinet screws) to protective earth, e.g. with braid, and test for low impedance. "Common ground" means the PSUs' DC 0 V/negative, not earth. Join grounds at the PSUs and run a separate ground per rail to the playfield.
- **Power entry/filter boards:** Multimorphic Power Entry (up to 4 DC rails: 5/12/15/HV, capacitor bank, HV safety relay on J10 wired to the coin-door switch; **J10 must be closed during development or HV stays off**), FAST Power Filter / Smart Power Filter, Spooky/PBL #600-0253-00, OPP Power Filter, Stern SPIKE PDB 520-5343-01, CobraPin (built in). Distribution boards: Spooky/PBL #600-0224-00, FAST Playfield Interchange, Multimorphic PCBA-0031-0003.
- **Wire and connectors:** use AWG 18 or thicker (≥1 mm²) above 1 A. Coils use **.156" Molex KK** (about 7 A; use multiple pins for more): housings 09-50-30x1 (2–12 pos), crimps 39-00-0342 / 08-52-0072. Logic uses AWG 20–24 with **.100" KK** (about 1 A): housings 22-01-20x7, crimps 08-51-0108 / 08-50-0114. Wire-to-wire uses **.093" Molex** (250 V/14 A), e.g. 03-09-1022/2022, crimps 02-09-1118/1119 (buy the loose ones, not reel), tool IWISS SN-28B, extractor Molex 0011030006. Buy from Digikey or Mouser.
- **Software power management (`psus:`):** MPF serialises non-time-critical pulses (ball device ejects, drop target resets, score reels) per PSU so switching supplies don't trip on overcurrent. Hardware-rule devices (flippers, pops, slings) are unaffected. Without this, score reels fail when 15 pulse at once.
```yaml
psus:
  default:
    voltage: 48
    release_wait_ms: 50     # default 10ms gap between pulses
  psu_12v:
    voltage: 12
coils:
  c_score_reel_1k_p1:
    psu: psu_12v
    number: ...
```
- **Safe bring-up practice** (from the CobraPin and P-ROC troubleshooting pages): test with coil power off or coils unplugged and watch the per-output LEDs. Then test at lower voltage (12 V instead of 48 V) or with lamps in place of coils before full HV.

---

## 7. Hardware troubleshooting

**Generic checklist** (`troubleshooting_hardware/index.md` and the shared includes):
1. **Nothing works at all:** remove `-x`/`-X`/`--vpx`. Check the USB cable and hubs (bad or long cables are common). On Linux run `lsusb` / `dmesg` with and without the device plugged in (OPP/CobraPin show as `0483:5740 STMicroelectronics Virtual COM Port`).
2. **Serial "Permission denied" on Linux:** `sudo usermod -a -G dialout $USER` and log in again, or add a udev rule. Don't run MPF as root. The exception is `rpi_dmd`, which needs `sudo mpf game`.
3. **Run `mpf hardware scan`** to see firmware and boards on FAST (NET/RGB/DMD CPUs and each I/O board's model, firmware, switch and driver counts; NET and node firmware should match), P/P3-ROC (firmware, SW-16 list; PD-16/PD-LED are invisible), OPP (CPUs, incandescent/input/solenoid/LED cards with their valid numbers), PKONE (Nano, Extension and Lightshow boards with firmware) and LISY (hardware, versions, counts).
4. **Enable `debug: true`** in the platform section (`fast:`, `p_roc:`, `opp:`, `spike:`, `lisy:`, `pkone:`, `fadecandy:`, `pin2dmd:`) and on the individual devices. Run `mpf both -t -v -V`. Turn debug off afterwards because it slows MPF.
5. **Switches work but coils don't:** check the **watchdog** (most boards have an LED; no watchdog means no coils). This usually points to a wiring problem.
6. **Check the numbering:** start the game, then in a second console run `mpf service`, `list_coils` and `coil_pulse <name>`. With no `default_pulse_ms`, MPF uses **10 ms**, which may be too weak, so try 20–30 ms.
7. **Lights lag or colours are corrupt (bus contention):** `mpf: default_light_hw_update_hz: 30` (default 50). **[CHECK]** The FAST LED page calls this `default_led_hw_update_hz` in its prose.

**Platform-specific:**
- **FAST:** support is via FAST's Slack. Upgrade to the latest firmware, since MPF isn't tested against old versions. A stuck-on coil or a blown fuse usually means a burned FET. An output that never fires is unlikely to be the FET.
- **P/P3-ROC:**
  - `ImportError: DLL load failed`: wrong FTDI libraries, missing VC++ redistributable, or pinproc not installed.
  - `Failed to reset P/P3-Roc … wrote 0 of 8 bytes` repeating: the board is not powered or not connected.
  - Random `OSError: Error in WriteData` crashes: an unreliable or overloaded 5 V supply, or a bad USB cable.
  - Check the four blue LEDs circling.
  - P-ROC switches dead: no 12 V, or bad switch ground. P3-ROC: SW-16 missing from the scan means a reversed or twisted bus.
  - `Refusing to update driver #… polarity differs on non-custom machine`: a driverboard/polarity mismatch.
  - **All coils on at power-up before MPF runs:** no common ground. **Shortly after MPF starts (P-ROC):** wrong polarity or machine type.
  - Firmware upgrade uses `pinprocfw` (download from Multimorphic). Never power down during the upgrade.
- **OPP:** reduce `poll_hz` if the boards can't keep up (you risk missing fast hits). Blacklist cytherm and stop ModemManager.
- **SPIKE:** turn on bridge logging to a USB stick (`bridge_debug`, `bridge_debug_log: /mnt/spike.log`). Capture Stern's own bus traffic with `interceptty-arm` on `/dev/ttyS4` (SPIKE 1) or `/dev/ttymxc1` (SPIKE 2) and share it on the forum.
- **FadeCandy:** flicker after many MPF restarts is fixed by power-cycling the FadeCandy (a known firmware race).
- **PIN2DMD:** blank display usually means brightness is too low (`rgb_dmds: default: brightness: .8`).
- **Keyboard (legacy MC):** with `debug: yes`, look for `s-numlock` in the key logs. NumLock left on breaks the mappings.

---

## 8. Notable contradictions / outdated bits (summary)

1. The FAST in-tree docs are Nano/≤0.56 only. The Neuron/0.80 configuration (`fast: net: io_loop`, `exp: boards`) lives only in the config reference and on fastpinball.com.
2. FAST watchdog default: 1000 ms (Nano doc) vs "Default: 500" in `fast_net.md`, whose own note says the default was 1000 until 0.58/0.81. Normal debounce: 4 ms (Nano doc) vs 10 ms (`fast_net.md`).
3. FAST RGB DMD baud: 4000000 (`fast/rgb_dmd.md`) vs 3000000 (`smartmatrix.md`).
4. The `fast_exp_board.md` example uses `neuron-2-54` for "last_on_chain_four" (probably `neuron-4-54`). The Nano LED examples have typos in the channel comments.
5. Default platform: `virtual` (config ref) vs `smart_virtual` (smart_virtual page).
6. `driverboards:` appears both under `hardware:` and under the platform section.
7. The OPP switch and coil docs use 2-part numbers, while the CobraPin, LED and Combo docs use 3-part numbers.
8. SPIKE opto `type: NO` (text) vs `type: false` (example).
9. LISY lamp-bank coil: "05 → 105" (text) vs `107` (example).
10. PKONE switch range "1-35" vs example `0-0`, and the Linux port typo `ttyASM0`.
11. Snux: the prose says `platform: p_roc`/`driverboards: snux`, the YAML says `platform: virtual`/`driverboards: wpc` with `coils/switches: snux`, and the relay key appears as both `ac_relay_driver_number` and `ac_relay_driver`. Switch example typo `L56` for `S56`. The board itself is likely unobtainable.
12. WPC page: `s35/s36` for FULM/FULH, flashers "in flashers:" but shown under `coils:`, and a duplicate section number 5.
13. The `machines/index.md` support table omits P-ROC for Sys11, Data East, SAM, Whitestar and P2K.
14. SPI bit-bang refresh formula as written is inverted.
15. `hardware/index.md` says "pick one of these three" and then lists 7. "New in 0.5x" tags are historical.
16. All DMD, window and slide examples and the `keyboard:` YAML are legacy MPF-MC. In 0.80 the GMC uses `gmc.cfg` (`[keyboard]`, window filters), and physical DMD output under GMC isn't documented in this tree.
17. `hardware/pinball_controllers.md` and `hardware/hobbyist.md` are stubs (TODO / "see table of contents").

---

## Source doc paths used
(relative to `mpf-docs-dev/docs/`; snippet includes from `mpf-docs-dev/includes/`)

- hardware/: index.md, platform.md, numbers.md, hw_rules.md, pinball_controllers.md, hobbyist.md, computer.md, snux.md, dmd_platforms.md, servo_platforms.md, stepper_platforms.md, i2c_platforms.md, segment_display_platforms.md, segment_display_transitions.md, light_segment_displays.md, smartmatrix.md, eli_dmd.md, rpi_dmd.md, rpi.md, smbus.md, i2c_servo.md, mma8451.md, pololu_maestro.md, pololu_tic.md, trinamics.md, stepstick.md, osc.md, spi_bit_bang.md
- hardware/fast/: index, config, connecting, switches, drivers, hw_rules, leds, lights, dmd, rgb_dmd, servos, power_filter, cabinet_board_0024, troubleshooting
- hardware/multimorphic/: index, platform, connecting, hardware_drivers, win_x64, win_x86, mac, linux, switches_p_roc, switches_p3_roc, drivers, leds, lights, dmd, rgb_dmd, alpha_numeric, accelerometer, i2c, power_entry, servos, steppers, firmware_upgrade, troubleshooting
- hardware/opp/: index, connecting, config, switches, drivers, leds, lights, troubleshooting, cobrapin/index, cobrapin/cobrapin_serial_segment_displays, oppcombo/index
- hardware/spike/: index, connection, config, mpf-spike-bridge, switches, drivers, leds, dmds, steppers, troubleshooting
- hardware/lisy/: index, connection, drivers, flippers_slings_popbumpers, lights, segment_displays, sound, switches_lisy1, switches_lisy80, troubleshooting, protocol (theory/limitations; command reference skimmed)
- hardware/apc/: index, connection
- hardware/pkone/: index, connecting, config, switches, drivers, leds, lights, servos, troubleshooting
- hardware/virtual/: index, virtual, smart_virtual, virtual_pinball_vpx, keyboard, segment_display_emulator
- hardware/fadecandy/: index, troubleshooting; hardware/pin2dmd/: index, troubleshooting; hardware/mypinballs/: index, wiring
- hardware/voltages_and_power/: index, voltages_and_power, ground_and_appliance_classes, wiring_and_connectors, power_management
- hardware/troubleshooting_hardware/index.md
- machines/: index, homebrew, wpc, system11, data_east, sam, whitestar, spike, pinball2000, williams_system3_to_9, gottlieb_system1, gottlieb_system80, bally_stern_as_2518
- physical_building/: index, layout_considerations, planning_layout_with_cad
- Cross-checked (outside assigned section, for 0.80 accuracy): config/hardware.md, config/system11.md, config/fast.md, config/fast/fast_net.md, config/fast/fast_exp.md, config/fast/fast_exp_board.md, gmc/keyboard.md, gmc/guides/window-filters.md (grep only)
- Includes: hardware_platform.md, light_channels_numbers.md, common_ground_warning.md, troubleshooting.md, troubleshooting_coils.md, troubleshooting_lights.md
- Nav: mkdocs.yml (hardware/machines/physical_building nav)
