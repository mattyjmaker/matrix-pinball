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

## Testing without the library

`gmc/slides/attract/assets/matrixrain.ogv` is tracked in the repo and is a valid
Theora file. Copy it here as `matrixrain.ogv` to exercise the widget on a fresh
checkout.

## Exporting the game

`VideoStreamTheora` has no scriptable file path, so clips must be `res://`
resources. When you build a production export, add `video/*` to the export
preset's include filter or the clips will be left out of the pack.
