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
- Unfinished wiring is why the placeholder switch numbers below can't all be replaced yet. Note the split: the flipper **coils** and the lower third are on the 3208 and wired, so those can be numbered now — but `s_left_flipper`, `s_right_flipper` and `s_start` are `cab-…` **switches** on the unwired Cabinet I/O, so they must stay placeholders until the cabinet is wired.

## Installed software

| What | Version | Location |
|---|---|---|
| Python | 3.14.4 (system) | `/usr/bin/python3` |
| MPF | 0.80.0 (pinned) | venv `~/.mpfenv/matrix` |
| MPF Monitor | 1.0.0.dev1 (+ PyQt6 6.11) | same venv |
| Godot editor | 4.6.3-stable | `~/.local/opt/godot/`, symlinked as `~/.local/bin/godot` |
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
- [ ] Replace placeholder switch numbers. MPF won't start on real hardware until these are fixed:
  - `s_left_flipper`, `s_right_flipper` and `s_start` (`cab-9993…`)
  - `s_trough1`, `s_trough_jam` and `s_plunger` (`bottom32-999-…`)
- [ ] **Add the second 1616 to `io_loop:` in `config/config.yaml`.** The config declares only three boards (`cab`, `top16`, `bottom32`) but two 1616s are installed. Until the fourth entry exists — with `order:` values matching the real daisy-chain order out of the Neuron — switch and driver numbers will land on the wrong boards.
- [ ] Run `mpf hardware scan` to confirm the board models and loop order match the config (`FP-CAB-0001`, `FP-I/O-1616` ×2, `FP-I/O-3208`, `FP-EXP-2000` + `FP-PWR-0007`). This is the fastest way to get the true `order:` values.
- [ ] Wire the Cabinet I/O (FP-CAB-0001). It's mounted but unwired, which blocks the `cab-…` switch numbers (flipper buttons, start) and the cabinet drivers (knocker, button lamps).
- [ ] Check whether the Cabinet I/O's **NET cable** is plugged into the I/O loop. If it isn't, it won't appear in `mpf hardware scan` and the config's `order: 1` for `cab` is wrong — every other board's order shifts.
- [ ] No LED expansion boards are wired or configured yet (FP-EXP-0081 and FP-EXP-0071 are owned). Needed before any playfield RGB inserts or servos work.
- [ ] Decide the plunger behaviour. `bd_plunger` has `eject_coil: c_auto_plunge` plus `mechanical_eject: true` but no `player_controlled_eject_event`, so a ball in the lane waits for a manual plunge. `eject_timeouts: 15s` is long; the docs suggest 3–5 s.
- [ ] Modes `welcome`, `plunge_ready` and `skillshot` exist but aren't listed under `modes:` and have no start events. `skillshot.yaml` is empty.
- [ ] `slide_player` for attract is defined in both `config.yaml` and `modes/attract`, so it is duplicated.
- [ ] Later, for production: export the Godot project to a binary, build the MPF production bundle, and set up auto-start on boot.
