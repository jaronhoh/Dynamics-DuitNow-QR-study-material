"""CRC-16/CCITT-FALSE utility used for DuitNow QR research."""

def crc16_ccitt_false(data: str) -> str:
    crc = 0xFFFF
    for byte in data.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"

def append_crc(payload_without_crc_value: str) -> str:
    return payload_without_crc_value + crc16_ccitt_false(payload_without_crc_value)