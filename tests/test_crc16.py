from src.crc16 import crc16_ccitt_false

def test_known_empty_crc():
    assert crc16_ccitt_false("") == "FFFF"

def test_crc_is_four_hex_chars():
    value = crc16_ccitt_false("6304")
    assert len(value) == 4
    int(value, 16)