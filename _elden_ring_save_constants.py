"""credits https://docs.google.com/spreadsheets/d/1LQXz9WHL9hE9Sgo5cTwjCsnywdChpoCt4AQU-__ROfQ/edit#gid=174090149"""
from typing import NamedTuple

class CharctersDataSectionAndLoadScreen(NamedTuple):
    data_section_offset: int
    load_screen_offset: int

SAVE_FILE_MAGIC_HEADER = b'\xcb\x01\x9c\x2c'
SAVE_FILE_SIZE = 28967040

SLOTS_IN_USE_BOOLEAN_ARRAY_OFFSET: int = 0x19019C4
SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING: str = '??????????'
SLOTS_IN_USE_BOOLEAN_ARRAY_LENGTH = len(SLOTS_IN_USE_BOOLEAN_ARRAY_STRUCT_STRING)


CHARACTER_DATA_SECTION_LENGTH: int = 0x280_000
LOAD_SCREEN_SECTION_LENGTH: int = 0x24c


CHARACTER_DATA_SECTIONS_AND_OFFSETS = (
    CharctersDataSectionAndLoadScreen(0x70, 0x19019CE),
    CharctersDataSectionAndLoadScreen(0x280070, 0x1901C1A),
    CharctersDataSectionAndLoadScreen(0x500070, 0x1901E66),
    CharctersDataSectionAndLoadScreen(0x780070, 0x19020B2),
    CharctersDataSectionAndLoadScreen(0xA00070, 0x19022FE),
    CharctersDataSectionAndLoadScreen(0xC80070, 0x190254A),
    CharctersDataSectionAndLoadScreen(0xF00070, 0x1902796),
    CharctersDataSectionAndLoadScreen(0x1180070, 0x19029E2),
    CharctersDataSectionAndLoadScreen(0x1400070, 0x1902C2E),
    CharctersDataSectionAndLoadScreen(0x1680070, 0x1902E7A)
)

CHARACTER_NAME_OFFSET: int = 32