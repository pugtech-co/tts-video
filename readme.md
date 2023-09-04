[Jolene](notebooks/output/jolene.mp4)
# Installation
## Requirements
- Pipenv

## Setup
1. Clone this repository
2. Run `pipenv install`
3. Run `pipenv shell`
4. Run `python3 -m ipykernel install --user --name=tts-video`
5. Run one of the jupyter notebooks in your favorite notebook environment
- If using VSCode, make sure to reload the kernels (`cmd+shift+p -> Developer: Reload Window`) and select the `tts-video` kernel


# Usage
This software works by taking text, generating audio using coqui TTS, matching up the audio with the text, and then painting the text on a video at the right timestamps. There are also a few options for automating the creation of the video and audio componenets of the video.
## Generating audio from text
see [src.tts](src/tts.py)
## Painting words on a video based on the generated audio
see [src.video_composition.combo.tts_component](src/video_composition/combo/tts_component.py)
## Adding videos, background, and audio together
see [notebooks.lyrics](notebooks/lyrics.ipynb)
