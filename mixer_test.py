from amfwx import MixerPanel,MixerStrip
p=MixerPanel([MixerStrip("A"),MixerStrip("B")]); print(len(p.strips))
