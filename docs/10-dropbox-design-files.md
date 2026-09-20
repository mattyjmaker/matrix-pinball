# The Matrix Dropbox Folder (design files)

**Shared folder:** (private Dropbox link — not published; see the local copy in `claude-workspace/mpf-documentation/`)
It holds about 16,200 files (13.6 GB) and was indexed on 2026-09-19.

- **Full file index:** `claude-workspace/dropbox-folder/tree.json`, with a path, size and download href for each file.
- **Lister script:** `claude-workspace/dropbox-folder/dbx.py`. Dropbox won't zip a folder this large, so the script calls the site's `list_shared_link_folder_entries` endpoint with the `t` cookie as CSRF token. Each subfolder needs its own hash, taken from the entry's href.
- **Downloading one file:** swap `dl=0` for `dl=1` in its href.
- **Already downloaded:** a few files are under `claude-workspace/dropbox-folder/files/`.

## What's there, by usefulness for this build

### Game design (useful for writing the MPF rules)
- **`Drawings/Visual Pinball/Matrix v1.7.vpx`** is the latest of 20 VPX versions of the table (v0.1 to v1.7), and it contains a working rules prototype. Its script has been extracted to `claude-workspace/dropbox-folder/matrix_v1.7_script.vbs`. See the rules summary below.
- `Drawings/Playfield/Playfield v79.dxf` is the latest playfield outline; it's also available as gcode. There's also `Playfield - Backwall v24.dxf`, `PF lower third v06_22_2022.dxf/.f3d`, `Matrix v1 6/v1 7 Blueprint.png`, `Initial Sketches.ai` and `Blueprint comparison.psd`.
- `Drawings/Visual Pinball/Playfield Art/Matrix v1.1 - Draft Art v1.psd/png` is the draft playfield art.
- `Progress/Video Walkthrough/`: a YouTube walkthrough of the VPX table (June 2023, 5.6 GB export).

### 3D-print / CNC parts
- **Cabinet** (`Drawings/Cabinet/`):
  - CNC dxf and gcode for every cabinet and backbox panel (Matt Jackson set, plus Stern-6 cabinet `.ai` files from Ernie at Trident Pinball)
  - `williams widebody cabinet rev3.pdf`
  - STLs: monitor guide and mount bracket, leg bolt drilling jig, NUC PSU bracket, SPDT switch housing
- **Playfield parts** (`Drawings/Playfield/Parts/`):
  - layout blocks: EMP left wall, outlanes, slings, inlane spacer, plunge lane guide, upper right flipper lane guide, back right block, wireform bracket
  - ramps: Neo Ramp v2 (top and bottom), Real World Ramp, Trinity Ramp V3
  - Sentinel front gate gcode
  - `Left Ramp Jun092022.f3d`
  - No Fear operator's manual (upper playfield long flipper; see page 87)
- `Drawings/STLs/Fast Pinball Brackets/` has heat-press M3 mounts for every FAST board: Neuron, Neuron power, 1616, 3208, 0804, Cabinet I/O, expansion, audio, power, opto power, interchange, Nano. There's also a coin door RGB LED holder.
- `Drawings/STLs/GitHub Homebrew Pinball/` has Fusion 360 models of stock mechs: trough, shooter lane kicker, WPC flippers, slings, DE pop bumper, Sega VUK, open-back scoop, smart drop, spinner, appearing post, standups, posts, lane guides, opto mount, FAST light boards.
- `Drawings/STLs/Google Drive STLS/`: printed guides (drain, flipper, plunger, trough), LED mounts, solenoid mounts, opto trough mounts.
- `Drawings/STLs/Theme/`: Sentinel head and full Sentinel model (obj/stl).
- `Misc/`: mounts for the Mean Well LRS-150-12 and LRS-150-24 power supplies, FAST Neuron controller mount, FAST smart power filter mount, wireform ramp clips.

### Media (for GMC)
- `Drawings/Visual Pinball/Audio/`: Matrix sound effects (dodge, "Dodge this", exit the Matrix, gunfire, computer noise and more) and *Clubbed to Death*.
- `Video Cuts/Sound FX/`: gunshots, impacts, mecha.
- `Video Cuts/Music/`: 139 FLAC tracks (2.9 GB) plus *Spybreak!*.
- `Video Cuts/Matrix 1/`: Premiere project for movie clip cuts.
- `Art/`: official movie posters, fan art, **`matrix.ttf` (Matrix font)**, Pinside banner.
- `Screen/Unity v0.1/Matrix HUD/`: an earlier Unity HUD project (about 15k files), superseded by GMC. There's also a link to a "Matrix Rain Code 4K" VideoHive asset.

### Purchasing records
- **`Invoices Purchases/Trident Pinball/Order 1 - Feb 2023/`** has cart screenshots of the big Pinball Life + FAST order. Its findings are recorded in 09-parts-inventory.md.
- The Pinside invoice/receipt (US$2,846, 2023-02-04), the Pinball Spare Parts order 100054402 (Nov 2023), the plywood invoice (Sep 2023), the Alienware monitor invoice, wirebot order WB-1540, and the SSV subwoofer receipt.

### Other
- Hobbit manual (full PDF, plus extracted pages 90 and 92, which are parts diagrams, probably for the pop-up beasts).
- `Led Zeppelin Homebrew BOM.xlsx`: another homebrew's BOM, kept for reference.
- `The Matrix - BOM.xlsx` is identical to the copy already summarised.
- `Community Notes.docx`: tips on fixing plastics (#8 pan-head screws with an 8 mm flange, or #6/#8 machine screws with T-nuts; avoid hex nuts; use heat-set inserts). It also links Ky1ebasa's Fusion livestreams.
- `Misc/Virtual Pinball/`: other VPX tables (AFM, Stargate, TheMATRIX_2.0, and others).

## Rules prototype from Matrix v1.7.vpx

The VPX table implements these rules:

- **Basics:** 3 balls per game, 20 s ball save started at the shooter lane gate (`MainGate`), up to 6 balls in multiball, auto-plunged balls. `LeftDrainSavePost` is a post that saves the left outlane.
- **Agents (3 pop-ups `Agent1-3`):** hitting a raised agent scores "Agent Kill" (10k). All three down scores "Agents Down" (50k). The **Cypher kicker** re-raises the agents when all are down ("Agents are Coming", 50k), or scores 5k otherwise.
- **Trinity lock / Trinity Multiball:** `TrinityOcto` locks a ball (10k) and auto-plunges a new one. The third lock starts **Trinity Multiball**; `TrinityPost` holds the locked balls. During multiball the shot scores "Trinity Bonus" (15k).
- **Ammo Lock:** `AmmoLockedTrigger` locks one ball behind `RightPost` (15,861). The next hit, or a drain with no other ball in play, releases it. This works as a drain save.
- **Morpheus Rescue:** `LeftSubwayCatch` is a 3-ball subway lock (50k each; "Two Balls Left!", "One More Ball!"). The third lock ejects all three from `LeftKicker`, and the second ball is sent a different way by the `BackDiverter`.
- **Human Pod / "Unplugged" Multiball:** `HumanPodSubway` locks 3 balls (10k each). It then starts a 3-ball multiball from `HumanPodReleaseKicker` (100k), but not while Trinity or Sentinel multiball is running.
- **Sentinel fight:** 4 hits across `SentinelEntranceLeft/Right` open the entrance wall and raise the Sentinel ("Hit the Sentinel!", 100k). Getting the ball into `SentinelDrain` starts **Sentinel Multiball**, which releases balls via the Deja Vu subway and auto-plunges. The Sentinel closes when the multiball ends.
- **Deja Vu subway kicker:** "Dejavu" (2,570) and re-kick.
- **Kicker001:** "Back at You" (5k) and resets `Target001`.
- **Real World ramp:** `RightRampKicker` feeds `RealWorldReturn` onto the Real World mini-playfield. `RealWorldFlipper` is tied to the left flipper button.
- **Music changes per mode:** intro, main, TrinityAgentsStart, Human Pod Multiball Start, SentinelMultiball.

Use these names as the starting vocabulary for MPF modes, shots and devices.
