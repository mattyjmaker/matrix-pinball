# Film clips

Clips played during the game live here as **Ogg Theora `.ogv`** files.

## These files are not in version control

`.gitignore` excludes everything in this folder except this README and
`manifest.txt`. Two reasons:

1. **Size.** A clip library runs to gigabytes. GitHub's free Git LFS allowance is
   1 GB of storage and 1 GB of bandwidth a month, and every clone pays it.
2. **Distribution.** Committing film footage publishes it. Keeping the clips out
   of the repository keeps that a local matter.

Keep the library in Dropbox alongside the design files (see
`docs/10-dropbox-design-files.md`) and sync it into this folder on the machine.

## Adding a clip

1. Encode to Ogg Theora. Godot 4 supports no other video format:

       ffmpeg -i source.mkv -vf "scale=1280:-2,fps=30" \
              -c:v libtheora -q:v 8 -an clip_name.ogv

   `-q:v` runs 0 to 10. Use 1280x720 for inset clips and 1920x1080 only for
   full-screen moments. Theora is an old codec, so encode at the size you will
   actually display rather than at source resolution.

   `-an` drops the audio. Prefer driving sound through GMC's sound system, which
   gives you buses and ducking. Keep audio embedded only where lip-sync matters,
   by replacing `-an` with `-c:a libvorbis -q:a 4`.

2. Name it after the clip, lower case with underscores, and drop it in here.
3. Add the name to `manifest.txt`, without the folder or the extension.
4. Run `tools/check_video.py` to confirm it is seen.

## Playing a clip

One widget serves every clip. Pass the name as a token:

    widget_player:
      agent_battle_started:
        video_clip:
          tokens:
            clip: agent_smith_intro

Add `loop: true` to the tokens to loop a clip until the widget is removed. The
widget's `expire` is then what ends it:

    widget_player:
      crew_freed:
        video_clip:
          expire: 6s
          tokens:
            clip: portrait_trinity
            loop: true

## Crew portrait loops

`portrait_<name>` clips are short "living portraits" of the FREED roster: a
film still animated with an AI image-to-video tool (breathing, a blink, a
slight head turn), then looped.

1. **Pick the still.** Sharp, front-facing, neutral expression, plain
   background, hands out of frame (AI video deforms hands).
2. **Generate.** Keep the motion prompt small, for example: "static camera,
   subtle breathing, slow blink, slight head tilt, no camera movement". Five
   seconds is enough. If the tool lets you set the last frame, set it to the
   same still for a seamless loop.
3. **Convert.** This crops to a 480x640 head-and-shoulders frame, applies one
   shared green grade so the eight read as a set, plays the clip forward then
   backward so it loops without a jump, and encodes to Theora:

       tools/make_portrait_loop.sh ~/Downloads/trinity_ai.mp4 trinity

   That writes `portrait_trinity.ogv` here. Pass `--crop W:H:X:Y` if the
   centre crop cuts the face, `--no-pingpong` if the tool already matched the
   last frame to the first, and `--no-grade` to keep the source colour. Run the
   script with `--help` for every option. Needs ffmpeg built with libtheora.

Check each AI video service's terms before uploading film stills. They
generally require you to hold rights to what you upload, and some block
recognisable people. The clips are derived from the film, so like the rest of
this folder they stay out of version control.

Theora decodes on the CPU. One portrait at a time is the safe use. Several
looping at once is untested on the cabinet PC.

## Testing without the library

`gmc/slides/attract/assets/matrixrain.ogv` is tracked in the repo and is a valid
Theora file. Copy it here as `matrixrain.ogv` to exercise the widget on a fresh
checkout.

## Exporting the game

`VideoStreamTheora` has no scriptable file path, so clips must be `res://`
resources. When you build a production export, add `video/*` to the export
preset's include filter or the clips will be left out of the pack.
