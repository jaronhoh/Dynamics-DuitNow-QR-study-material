# PayNet DuitNow QR Specification Notes

## Core fields

| Tag | Meaning | Key observation |
|---|---|---|
| 00 | Payload Format Indicator | 02 |
| 01 | Point of Initiation Method | 11 static, 12 dynamic |
| 26-27 | Merchant Account Information | Merchant/acquirer information |
| 52 | Merchant Category Code | 0000 is used for P2P; merchant examples use merchant MCC |
| 53 | Transaction Currency | 458 = MYR |
| 54 | Transaction Amount | Dynamic amount |
| 58 | Country Code | MY |
| 59 | Merchant Name | Merchant name |
| 60 | Merchant City | Merchant city |
| 61 | Postal Code | Optional |
| 62 | Additional Data Template | Invoice/reference-related fields |
| 63 | CRC | Mandatory and last |
| 82 | Data Integrity Check | Optional in PayNet data object; acquirer-specific behavior requires investigation |

## Additional Data

- 62-01: Bill Number / invoice number
- 62-05: Reference Label
- 62-07: Terminal Label

## Merchant Account Information

- 26-00: AID A0000006150001
- 26-01: Acquirer ID
- 26-02: Merchant/Recipient ID assigned by the acquirer

## CRC

- CRC-16/CCITT-FALSE
- Polynomial 0x1021
- Initial value 0xFFFF
- Calculate over the payload including 6304
- Exclude the final CRC value
- 63 must be the final field

## Critical distinction

QR format validity is not the same as acquirer validation or payment authorization.