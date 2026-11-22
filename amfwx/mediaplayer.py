"""Synchronized video/audio media player."""

from __future__ import annotations

from .mfvideo import MediaAudio, MediaVideo


class MediaPlayer:
    def __init__(self, path, with_audio=True):
        self.path = str(path)
        self.video = MediaVideo.from_file(self.path)
        self.stream = self.video.stream()
        self.audio = None
        self.audio_player = None
        self.playing = False
        self.time = 0.0
        self.audio_offset = 0.0
        self.fps = 25.0
        self.frames_decoded = 0
        self.frames_dropped = 0
        self.frames_duplicated = 0
        if with_audio:
            try:
                self.audio = MediaAudio.from_file(self.path, seconds=5)
            except Exception:
                self.audio = None

    def play(self):
        if self.audio is not None:
            try:
                self.audio_player = self.audio.play()
            except Exception:
                self.audio_player = None
        self.playing = True
        return self

    def pause(self):
        self.playing = False
        if self.audio_player is not None:
            self.audio_player.stop()
            self.audio_player = None

    def advance(self, seconds):
        if not self.playing:
            return None
        if self.audio_player is not None:
            target = self.audio_offset + self.audio_player.position()
            if target > self.time + 0.001:
                wanted = int((target - self.time) * self.fps)
                frames = min(8, max(1, wanted))
                frame = None
                for _ in range(frames):
                    candidate = self.stream.next_frame()
                    if candidate is not None:
                        frame = candidate
                        self.frames_decoded += 1
                if wanted > frames:
                    self.frames_dropped += wanted - frames
                self.time = target
                return frame
            if target < self.time - 0.001:
                self.frames_duplicated += 1
                return None
        frame = self.stream.next_frame()
        if frame is not None:
            self.frames_decoded += 1
        self.time += seconds
        return frame

    def seek(self, seconds):
        seconds = max(0.0, float(seconds))
        self.stream.seek(seconds)
        self.time = seconds
        self.audio_offset = seconds
        if self.audio is not None and self.audio.data:
            from .audio import AudioPlayer, Wav
            width = max(1, self.audio.channels * (self.audio.bits // 8))
            offset = int(seconds * self.audio.rate) * width
            data = self.audio.data[offset:]
            if self.audio_player is not None:
                self.audio_player.stop()
                self.audio_player = None
            if data:
                player = AudioPlayer()
                player.play(Wav(self.audio.channels, self.audio.rate,
                                self.audio.bits, data))
                self.audio_player = player
        return self

    def close(self):
        self.pause()
        if self.stream is not None:
            self.stream.close()
            self.stream = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
