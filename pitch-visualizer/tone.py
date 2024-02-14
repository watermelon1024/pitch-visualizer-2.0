TONES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BASE_DIFF = [0, 2, 4, 5, 7, 9, 11]
TONE_FREQ_MAP = {
    f"{t}{i}": 2 ** (TONES.index(t) / 12 + i) * 16.3516 for t in TONES for i in range(0, 8)
}


class Tonality:
    def __init__(self, tone: str):
        assert tone in TONES
        self.tone = tone
        self.scale = [TONES[(TONES.index(tone) + diff) % len(TONES)] for diff in BASE_DIFF]

    @classmethod
    def normalize_to_freq(cls, tone_or_freq):
        if isinstance(tone_or_freq, (float, int)):
            return tone_or_freq
        return TONE_FREQ_MAP[tone_or_freq]

    def get_tone_and_freq(self, min_freq=0, max_freq=4186) -> list[tuple[str, float]]:
        min_freq = self.normalize_to_freq(min_freq)
        max_freq = self.normalize_to_freq(max_freq)

        ret = []
        for i in range(0, 8):
            for base_tone in self.scale:
                tone = f"{base_tone}{i}"
                freq = TONE_FREQ_MAP[tone]
                if min_freq <= freq <= max_freq:
                    ret.append((tone, freq))

        return ret
