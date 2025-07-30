from dataclasses import dataclass


@dataclass
class PowerSettings:
    dac0: int
    dac1: int


POWER_TABLE = {
    100: PowerSettings(305, 500),
    105: PowerSettings(320, 500),
    110: PowerSettings(333, 500),
    115: PowerSettings(350, 500),
    120: PowerSettings(4, 768),
    125: PowerSettings(30, 768),
    130: PowerSettings(56, 768),
    135: PowerSettings(82, 768),
    140: PowerSettings(107, 768),
    145: PowerSettings(128, 768),
    150: PowerSettings(149, 768),
    155: PowerSettings(168, 768),
    160: PowerSettings(185, 768),
    165: PowerSettings(202, 768),
    170: PowerSettings(218, 768),
    175: PowerSettings(233, 768),
    180: PowerSettings(247, 768),
    185: PowerSettings(260, 768),
    190: PowerSettings(273, 768),
    195: PowerSettings(285, 768),
    200: PowerSettings(296, 768),
    205: PowerSettings(308, 768),
    210: PowerSettings(319, 768),
    215: PowerSettings(330, 768),
    220: PowerSettings(342, 768),
    225: PowerSettings(353, 768),
    230: PowerSettings(364, 768),
    235: PowerSettings(374, 768),
    240: PowerSettings(385, 768),
    245: PowerSettings(396, 768),
    250: PowerSettings(408, 768),
    255: PowerSettings(420, 768),
    260: PowerSettings(433, 768),
    265: PowerSettings(445, 768),
    270: PowerSettings(459, 768),
    275: PowerSettings(474, 768),
    280: PowerSettings(490, 768),
    285: PowerSettings(506, 768),
    290: PowerSettings(524, 768),
    295: PowerSettings(545, 768),
    300: PowerSettings(568, 768),
    305: PowerSettings(593, 768),
    310: PowerSettings(623, 768),
    315: PowerSettings(660, 768)
}
