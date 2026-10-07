"""Basic TLV parser and encoder for DuitNow QR research."""

def parse_tlv(payload: str):
    result = []
    i = 0
    while i < len(payload):
        if i + 4 > len(payload):
            raise ValueError("Incomplete TLV header")
        tag = payload[i:i+2]
        length = int(payload[i+2:i+4])
        start = i + 4
        end = start + length
        if end > len(payload):
            raise ValueError(f"Invalid length for tag {tag}")
        result.append((tag, payload[start:end]))
        i = end
    return result

def encode_tlv(tag: str, value: str) -> str:
    if len(tag) != 2:
        raise ValueError("Tag must be two digits")
    if len(value) > 99:
        raise ValueError("Value too long")
    return f"{tag}{len(value):02d}{value}"