# Dynamic DuitNow QR Study Notes

> Research log and working notes for generating and validating Malaysia DuitNow Merchant Presented Dynamic QR.
>
> Status: **reverse-engineering / experimental**. The observations below are based on PayNet documentation plus QR samples tested from RHB and OCBC, and live scanning/payment tests. They are not a statement of any bank's internal implementation.

## 1. Objective

The current objective is to understand the DuitNow QR data structure well enough to build a reusable QR engine later, with a potential REST API such as:

```
POST /api/duitnow/qr
{
  "amount": 0.01,
  "reference": "INV-001"
}
```

Potential response:

```
{
  "qrPayload": "...",
  "qrImage": "...",
  "amount": 0.01,
  "reference": "INV-001"
}
```

The study deliberately starts with QR construction and validation. Payment gateway integration, bank API integration, reconciliation and webhooks are out of scope for the current phase.

---

## 2. Official PayNet QR Data Object – Working Reference

Primary reference:
- PayNet – QR Data Object V1.5: https://docs.paynet.my/docs/duitnow-qr/merchant-presented-qr/qr-data-object
- PayNet – Merchant Presented Mode: https://docs.paynet.my/docs/duitnow-qr/merchant-presented-qr/qr-generation-specification/merchant-presented-mode
- PayNet – Examples: https://docs.paynet.my/docs/duitnow-qr/merchant-presented-qr/examples

Important fields observed / documented:

| Tag | Meaning | Notes |
|---|---|---|
| `00` | Payload Format Indicator | `02` |
| `01` | Point of Initiation Method | `11` static, `12` dynamic |
| `26`-`27` | Merchant Account Information | `27` is RFU in PayNet documentation |
| `52` | Merchant Category Code | `0000` is used for P2P in current PayNet docs |
| `53` | Transaction Currency | `458` = MYR |
| `54` | Transaction Amount | Example: `0.01` |
| `58` | Country Code | `MY` |
| `59` | Merchant Name | Merchant/account display name |
| `60` | Merchant City | Example samples showed `MY` for the RHB P2P sample |
| `61` | Postal Code | Optional |
| `62` | Additional Data Template | Can contain invoice/reference data |
| `62-01` | Bill Number | Up to 25 characters |
| `62-05` | Reference Label | Up to 25 characters; merchant/acquirer-defined reference |
| `62-07` | Terminal Label | Optional |
| `63` | CRC | Mandatory and must be last |
| `82` | Data Integrity Check | Optional in PayNet QR Data Object; exact acquirer implementation may differ |

### Merchant account information observed in RHB samples

```
26-00 = A0000006150001
26-01 = 564160
26-02 = 221217000072525RHBQR000000
```

RHB Bank Berhad acquirer ID observed from PayNet/acquirer reference material: `564160`.

### CRC

Working implementation used in generated test payloads:

- CRC-16/CCITT-FALSE
- Polynomial: `0x1021`
- Initial value: `0xFFFF`
- CRC is calculated over the payload including the `6304` header, but excluding the 4-character CRC value itself.
- `63` is the final field.

---

## 3. RHB Dynamic P2P QR – Official Samples

### RHB official sample: RM1.00

Decoded payload:

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR000000520400005303458540115802MY5912HOH HUN YUEN6002MY82649574E3E39536D3AEA8B570F607C5BCCB489EFDCBB0FB1EFCB0FFA8D86E38A30263044C49
```

Parsed:

```
00 = 02
01 = 12
26-00 = A0000006150001
26-01 = 564160
26-02 = 221217000072525RHBQR000000
52 = 0000
53 = 458
54 = 1
58 = MY
59 = HOH HUN YUEN
60 = MY
82 = 9574E3E39536D3AEA8B570F607C5BCCB489EFDCBB0FB1EFCB0FFA8D86E38A302
63 = 4C49
```

CRC checked successfully.

### RHB official sample: RM0.05

Decoded from an RHB app screenshot:

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.055802MY5912HOH HUN YUEN6002MY826467CD0FED69A253E4A50378658CFDF0E5059614CF31B5957AF0F91B8D2CD07C67630423F3
```

Key dynamic fields:

```
54 = 0.05
82 = 67CD0FED69A253E4A50378658CFDF0E5059614CF31B5957AF0F91B8D2CD07C
63 = 23F3
```

### RHB official sample: RM0.01

Decoded from an RHB app screenshot:

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.015802MY5912HOH HUN YUEN6002MY826443A6E0B8C92621538FA72BB3934D71934309EC824BD1AD76C19786DB03FCCABC363047BA3
```

Key dynamic fields:

```
54 = 0.01
82 = 43A6E0B8C92621538FA72BB3934D71934309EC824BD1AD76C19786DB03FCCABC
63 = 7BA3
```

These official samples establish that the RHB `82` value changes between otherwise similar Dynamic P2P QR samples.

---

## 4. RHB Experiments and Live Tests

### 4.1 Reference field experiments

Several RHB QR variants were generated and scanned.

Examples included:

- `62-05 = INV26-001`
- `62-01 = INV26-001`
- `62-08 = INV26-001`

The QR could be parsed by Affin, but the payment receipt still showed a generic `Fund Transfer` and did not surface the tested reference in the way expected.

### 4.2 MCC experiment

Changing:

```
52 = 0000
```

to:

```
52 = 9999
```

did not convert the P2P QR into a merchant POS payment.

Conclusion: simply changing the MCC does not make a P2P QR a merchant-acquirer QR.

### 4.3 UOB test with INV-001

A generated RHB QR with:

```
54 = 0.01
62-05 = INV-001
```

and no `82` was scanned by UOB.

Observed:

- UOB displayed **Recipient Reference = INV-001**
- Transfer could not be completed.

This is evidence that the standard `62-05` reference field is parsed by UOB even when the transaction is not accepted for payment.

### 4.4 Invalid QR tests

Multiple experiments copied an official RHB `82` from another amount or removed `82`, then changed the amount and recalculated CRC.

Examples that resulted in **Invalid QR** in UOB included:

- RHB + RM0.01 + no `82`
- RHB + RM0.01 + `INV-001` + copied/old `82`
- RHB + RM0.01 + `INV-001` with different `62` / `82` ordering

Important conclusion:

> A QR can have structurally correct TLV and CRC values but still be rejected by the payment flow. This indicates that the bank/acquirer can perform additional validation beyond the QR container CRC.

---

## 5. RHB `82` – Current Research Status

The strongest current evidence is:

```
Official RM1.00 -> 82 = 9574E3...
Official RM0.05 -> 82 = 67CD0F...
Official RM0.01 -> 82 = 43A6E0...
```

Therefore:

> RHB's `82` is dynamic and changes between generated QRs.

What is **not yet known**:

- exact hash/HMAC algorithm
- exact input string
- whether a secret/key is involved
- whether timestamp/nonce/expiry is included
- whether the value is validated by an RHB backend
- whether it is tied to amount, merchant ID, transaction instance, or multiple fields

We tried simple candidate hashing ideas, but no verified algorithm has been established.

Do **not** treat `82` as solved.

---

## 6. RHB Dynamic QR Expiry Observation

The RHB app displays a countdown/refresh period for Dynamic QR.

Repeated screenshots indicated that the countdown itself was not encoded as a visible QR field in a straightforward way. The likely validity control is app/backend-side, but this is an inference and has not been fully reverse engineered.

---

## 7. OCBC OneCollect Research

Official references:
- OCBC OneCollect: https://www.ocbc.com.my/business-banking/accounts-and-services/onecollect/
- OCBC OneCollect FAQ: https://www.ocbc.com.my/business-banking/help-and-support/collections/ocbc-onecollect
- OCBC OneCollect User Guide: https://www.ocbc.com.my/edm/business-banking/onecollect-journey/pdf/OneCollect-user-guide.pdf

Decoded OCBC OneCollect Dynamic QR samples showed a consistent merchant profile:

```
00 = 02
01 = 12
26-00 = A0000006150001
26-01 = 504324
26-02 = MJ0X5KZI4VYSRTFAC9YR2LFMVRAR
52 = 7338
53 = 458
58 = MY
59 = MGX (MALAYSIA) SDN. BHD.
60 = SELANGOR
62-03 = MGX (MALAYSIA) SDN. BHD.
62-07 = 10000001
```

OCBC Acquirer ID observed: `504324`.

Dynamic fields included:

- `54` amount
- `62-01`
- `62-05`
- `82`
- `63`

### Timestamp relationship found in OCBC samples

`62-05` matched Unix timestamps exactly in several samples:

```
1791339779
1791339797
1791339847
1791340431
1791340636
1791340773
```

The observed `62-01` also contained a hex timestamp-like section.

Examples:

```
DND006AC5B399184
DND016AC5B3A104F
```

The 8-hex component corresponded to a timestamp one second before `62-05` in those samples.

The remaining suffix did not yet show a verified deterministic pattern.

### OCBC `82`

OCBC `82` values were 64 hexadecimal characters and changed between QR instances.

Simple candidate SHA-256 calculations did not match observed values.

Current conclusion:

> OCBC `82` appears to be acquirer-specific integrity/authentication data. The exact generation method is unresolved.

---

## 8. Important Distinction: QR Format vs Payment Authorization

One of the most useful conclusions from the experiments is that these are separate layers:

```
Layer 1 - QR data construction
  TLV
  Merchant data
  Amount
  Reference
  CRC
  QR rendering

Layer 2 - Acquirer / DuitNow processing
  Merchant onboarding
  Acquirer validation
  Dynamic transaction validation
  Authentication / integrity checks
  Routing
  Account status
```

A scanner can successfully parse a QR and display fields such as `INV-001`, while the payment can still be rejected later.

Therefore:

> **"UOB can read the QR" does not mean "UOB can authorize the payment".**

Likewise:

> **A valid CRC does not prove that an acquirer considers the Dynamic QR transaction valid.**

---

## 9. Current Development Direction

The intended future architecture is an internal QR engine, not a payment gateway integration.

Suggested components:

```
QR Engine
├── PayloadBuilder
├── TLVEncoder
├── CRC16
├── QRRenderer
└── AcquirerProfile

REST API
└── POST /api/duitnow/qr

ERP / D365 / POS
└── amount + reference -> QR API
```

Later integration targets may include D365 / ERP / POS.

Actual merchant/acquirer onboarding is still required for production transaction acceptance.

---

## 10. Current Test Matrix

| Sample / Experiment | Result |
|---|---|
| RHB official Dynamic QR | Valid |
| RHB official RM1.00 | Valid |
| RHB official RM0.05 | Valid |
| RHB official RM0.01 | Valid |
| Self-generated RHB + RM0.01 + no 82 | UOB reported Invalid QR |
| Self-generated RHB + RM0.01 + INV-001 + no 82 | UOB could parse reference, transfer failed in an earlier variant |
| Self-generated RHB + copied old 82 | UOB reported Invalid QR |
| RHB 52 changed to 9999 | Did not become Merchant POS payment |
| OCBC-style generated QR without 82 | UOB could parse but transfer failed |
| OCBC-style QR + 62-05 reference | UOB displayed Recipient Reference; transfer failed |

---

## 11. Known Good RHB Payloads

### RM1.00

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR000000520400005303458540115802MY5912HOH HUN YUEN6002MY82649574E3E39536D3AEA8B570F607C5BCCB489EFDCBB0FB1EFCB0FFA8D86E38A30263044C49
```

### RM0.05

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.055802MY5912HOH HUN YUEN6002MY826467CD0FED69A253E4A50378658CFDF0E5059614CF31B5957AF0F91B8D2CD07C67630423F3
```

### RM0.01

```
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.015802MY5912HOH HUN YUEN6002MY826443A6E0B8C92621538FA72BB3934D71934309EC824BD1AD76C19786DB03FCCABC363047BA3
```

---

## 12. Open Questions

1. How exactly does RHB calculate `82`?
2. Is RHB `82` a plain hash, keyed HMAC, encrypted/authenticated token, or another proprietary structure?
3. Which exact fields are included in the RHB `82` calculation?
4. Is time / expiry included?
5. Can a legitimate RHB Dynamic P2P QR be reproduced outside the RHB app without a server-side secret?
6. Which portions of the PayNet specification are sufficient for a scanner versus sufficient for transaction authorization?
7. What is required to build a genuine Merchant Presented Dynamic QR for a merchant-acquirer account rather than a P2P receive QR?

---

## 13. Important Guardrails for Future Experiments

- Do not assume `CRC=valid` means transaction-valid.
- Do not assume `82` can be copied from one QR to another.
- Keep official samples separate from generated experimental samples.
- Record the exact source screenshot, amount, timestamp, full payload, and scan result for each experiment.
- When changing one field, change only one field where possible.
- Preserve a known-good official QR baseline for every new test series.
