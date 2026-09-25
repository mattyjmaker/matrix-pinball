# MPF Documentation Summary

This is a condensed review of the whole **Mission Pinball Framework** documentation site
(docs.missionpinball.org), written as a working reference for this pinball machine.

- **Source:** the `dev` branch of `github.com/missionpinball/mpf-docs`, the markdown behind the website. It has about 1,340 pages and 600k words, and all of it was read.
- **Reviewed:** 2026-09-19.
- **Target version:** **MPF 0.80.0**, released April 2026, with the **Godot Media Controller (GMC) 1.0.0**. Anything that applies only to 0.57 or the legacy Kivy MPF-MC is marked as legacy in these files.

> **Location note:** these files also live outside the repo at `~/claude-workspace/mpf-documentation/`.
> The copy in `docs/` is the one to edit and commit; `The-Matrix-BOM.xlsx` alongside it is the parts source of truth.

## Files

| File | Covers |
|---|---|
| [00-setup-guide.md](00-setup-guide.md) | **Start here.** How the pieces connect, then step-by-step: host PC, install, project layout, GMC, virtual dev, minimal config, hardware bring-up, production. |
| [01-install-running-tools.md](01-install-running-tools.md) | What MPF is, the architecture and BCP ports, installing MPF and GMC, every `mpf` command and flag, Monitor/service/benchmark tools, logging, error codes, troubleshooting, testing basics, migrating from 0.57 to 0.80, version history. |
| [02-hardware.md](02-hardware.md) | Hardware rules, choosing and mixing platforms, a comparison table of every controller (FAST, P-ROC/P3-ROC, OPP/CobraPin, SPIKE, LISY/APC, PKONE, Snux, add-ons), numbering cheat-sheet, setup per platform, re-theming existing machines vs homebrew, power/wiring/safety, hardware troubleshooting. |
| [03-config-reference.md](03-config-reference.md) | How config files work (versions, YAML rules, time and colour formats, dynamic values, conditional events, templates), config players, a categorised index of **every** config section with deep dives on the key ones, built-in player/machine/game variables, 0.80 deprecations. |
| [04-game-logic-and-mechs.md](04-game-logic-and-mechs.md) | Game flow and built-in modes, the mode system, shots/profiles/groups, logic blocks, scoring, ball save/search/tracking, multiball and locks, bonus, high scores, credits, tilt, and how to configure every mechanism (flippers, autofires, troughs, plungers, drop targets, diverters, magnets, motors, servos...). |
| [05-media-gmc-and-shows.md](05-media-gmc-and-shows.md) | GMC in depth (Godot project, slides/widgets as scenes, GMC nodes, sounds and buses, video, DMD look, multiple screens, `gmc.cfg`), the show system (format, tokens, `show_player`, sync), and a legacy MPF-MC → GMC mapping table. |
| [06-tutorials-cookbook-finalization.md](06-tutorials-cookbook-finalization.md) | The official 20-step tutorial condensed (it targets the legacy MC; GMC equivalents noted), all cookbook recipes, game design patterns, flowcharts, finishing and deploying a cabinet, community links. |
| [07-code-and-events.md](07-code-and-events.md) | MPF internals, writing custom Python (mode code, `custom_code`), the BCP protocol, the machine test framework, contributing, and a categorised reference of ~230 MPF events. |
| [08-this-machine.md](08-this-machine.md) | **This cabinet PC:** what's installed where, the `pinball` launch commands, changes made to the repo, and the remaining to-do list. |
| [09-parts-inventory.md](09-parts-inventory.md) | **Physical parts** from The Matrix BOM spreadsheet: each part marked as owned, ordered or planned, grouped by playfield area; also measurements and a rough coil/switch count for the config. |
| [10-dropbox-design-files.md](10-dropbox-design-files.md) | **The user's Matrix Dropbox folder:** what's in it (VPX table versions, playfield DXF/CNC files, STLs, audio, art, invoices), how to list and download from it, and the rules prototype taken from the Matrix v1.7 VPX script. |
| [11-rules-act-1.md](11-rules-act-1.md) | **Act I rules (movie 1), as implemented:** chapter modes, the kept VPX multiballs, the FREED roster, The One wizard and the act select, with every timer and score; the mode map, the pending-hardware layer and how to run the tests. |
| [12-fast-boards.md](12-fast-boards.md) | **The FAST boards this machine owns:** part numbers, header pinouts and fuse map for each board, how MPF 0.80 sees them, FAST's wiring standard compared with this machine's, the checks still to do on the machine, and the discrepancies found. |

Each file ends with the list of source doc pages it was drawn from.

## Most important things to know

1. **0.80 changed the media side completely.**
   - The Godot GMC replaces MPF-MC, so `slides:`, `widgets:`, `sounds:`, `sound_system:`, `window:`, `keyboard:` and similar sections are gone from MPF YAML.
   - Slides are now Godot scenes, and sounds use Godot buses (`track:` became `bus:`).
   - `slide_player`, `widget_player` and `sound_player` still live in MPF YAML.
2. **Much of the docs is still written for 0.57.**
   - The official tutorial, most cookbook recipes, the Linux and Raspberry Pi install pages, the FAST hardware pages (Nano only) and every DMD example use the legacy MC.
   - Use the `gmc/`, `config/` and `install/0.80.md` pages as the source of truth.
3. **The docs contain many internal contradictions and typos.** Each file flags the ones found, marked **[DOC CONFLICT]**, **[CHECK]**, **[STALE]** or ⚠. The ones that bite:
   - The GMC autoload file is `mpf_gmc.gd`, and the node must be named `MPF`.
   - `pip install mpf --pre` is outdated advice now that 0.80.0 is final.
   - Many examples use `#config_version=5`; 0.80 uses `=6`.
4. **Gaps with no 0.80 documentation yet:**
   - driving a **physical DMD** from GMC;
   - GMC virtual segment displays;
   - changing the GMC BCP port;
   - a Raspberry Pi / Linux cabinet install for 0.80;
   - auto-starting the exported Godot binary;
   - writing custom devices or platforms.
5. **Post-0.80 content is mixed in.** The dev docs already describe some 0.81 features, such as FAST `led_ports`, soft power and soft-shutdown events. These are flagged in the files and don't work on 0.80.0.

## Useful links

- Docs: https://docs.missionpinball.org
- MPF: https://github.com/missionpinball/mpf (branch `0.80.x`, tag `v0.80.0`; `dev` = 0.81)
- GMC: https://github.com/missionpinball/mpf-gmc
- Community: https://github.com/orgs/missionpinball/discussions and https://groups.google.com/g/mpf-users
