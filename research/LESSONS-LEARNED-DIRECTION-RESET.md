# DuitNow QR Study – Lessons Learned & Direction Reset

> The first development direction was wrong. This file records the mistakes so future work does not repeat them.

## 1. Executive Summary

We started from RHB Mobile Banking / Personal Receive Dynamic QR samples and attempted to turn them into a reusable Merchant Presented Dynamic QR by changing amount, reference, MCC, 82 and CRC.

Observed results included:
- UOB could parse some generated QR content.
- UOB could display `Recipient Reference = INV-001`.
- Transfers could not be completed.
- UOB could report `Invalid QR`.
- Copying an 82 value from another QR did not make a valid transaction.

Main lesson:

> **A P2P Dynamic Receive QR is not a valid development baseline for a Merchant Presented Dynamic QR solution.**

## 2. Mistake #1 – Starting from the Wrong QR Product

The main RHB samples came from the mobile banking Receive / Request Money flow. They repeatedly showed `01=12` and `52=0000`.

PayNet documentation identifies `52=0000` with P2P QR usage. We therefore spent significant effort reverse-engineering an RHB Personal / P2P Dynamic Receive QR.

Our real objective is:

```text
Merchant Presented Dynamic QR
        ↓
D365 / POS
        ↓
Amount + Invoice Reference
        ↓
Customer scans
        ↓
DuitNow payment
```

These are different use cases. Do not use a Personal Receive QR as the baseline for a Merchant Presented Dynamic QR.

## 3. Mistake #2 – Assuming PayNet QR Format Equals Transaction Acceptance

We correctly learned TLV structure and CRC rules, but incorrectly treated:

```text
Valid TLV + Valid CRC + Scanner can decode
        ↓
Bank will accept payment
```

That assumption is wrong.

PayNet Merchant Presented QR documentation defines QR format/content, while processing and network-level behavior are outside the QR data object itself.

Therefore:

```text
QR parsing       ≠ Payment authorization
CRC valid        ≠ Acquirer transaction valid
```

## 4. Mistake #3 – Treating 82 as a Field We Could Copy

Official RHB samples showed different `82` values for different Dynamic QR instances:

```text
RM1.00 → 82 = 9574E3...
RM0.05 → 82 = 67CD0F...
RM0.01 → 82 = 43A6E0...
```

We then tried removing `82`, copying it from another amount, and changing amount/reference while retaining an old `82`.

Some of these QR strings had correct TLV and CRC but were rejected as Invalid QR.

Lesson: treat `82` as dynamic integrity/authentication data until proven otherwise. Do not copy it from QR-A into QR-B.

## 5. Mistake #4 – Changing 52 Does Not Convert P2P to Merchant QR

We changed `52=0000` to `52=9999` to test whether a P2P QR could become a merchant POS QR.

It did not work.

Therefore:

```text
P2P QR + MCC change ≠ Merchant QR
```

Merchant QR behavior depends on the complete merchant/acquirer configuration and transaction processing environment.

## 6. Mistake #5 – Treating 62-05 as Proof of a Merchant QR

We tested `62-05=INV-001`. UOB displayed `Recipient Reference = INV-001`, but the transfer still could not be completed.

This proves that the field can be parsed. It does not prove merchant transaction authorization.

Therefore `62-05` is a data field, not a mechanism for converting P2P QR into Merchant QR.

## 7. Mistake #6 – Changing Too Many Variables Without a True Merchant Baseline

Experiments changed amount, reference, MCC, 82, field ordering and CRC while the starting QR was the wrong product.

Without a genuine Merchant Dynamic QR baseline, an Invalid QR result cannot be reliably attributed to one field.

## 8. Mistake #7 – Building the QR Engine Too Early

The proposed PayloadBuilder / TLVEncoder / CRC16 / QRRenderer / AcquirerProfile architecture may still be useful, but implementation should wait until the correct Merchant QR baseline and acquirer behavior are understood.

Correct order:

```text
1. Identify correct QR product
2. Obtain official Merchant Dynamic QR
3. Decode official samples
4. Compare multiple official samples
5. Understand dynamic fields
6. Understand acquirer validation
7. Confirm payment acceptance
8. Implement QR Engine
```

## 9. What the Previous Research Still Proved

The previous work was not wasted.

- PayNet TLV handling is understood at a practical level.
- CRC-16/CCITT-FALSE implementation was verified against official samples.
- UOB can parse `62-05` as Recipient Reference.
- Scanner acceptance and payment authorization are separate stages.
- RHB `82` changes between official Dynamic QR instances.

Working CRC assumptions:

```text
CRC-16/CCITT-FALSE
Polynomial = 0x1021
Initial value = 0xFFFF
`63` is the final field
CRC is calculated over the payload including `6304`, excluding the final CRC value
```

## 10. Correct Direction From Now On

The new main baseline should be a genuine Merchant Presented Dynamic QR, preferably from the RHB business merchant flow / RHB Reflex.

RHB documentation indicates that its Reflex DuitNow QR flow supports Dynamic QR and transaction reference.

Target official sample:

```text
Amount = RM0.01
Transaction Reference = INV-001
Dynamic QR generated by the official merchant system
```

Do not construct this sample ourselves.

## 11. New Experimental Method

Once an official Merchant Dynamic QR is available, create multiple official samples:

```text
Sample A: RM0.01 / INV-001
Sample B: RM0.02 / INV-002
Sample C: RM1.00 / INV-003
Sample D: RM1.00 / INV-004
```

Then compare every field:

```text
00, 01, 26-00, 26-01, 26-02, 52, 53, 54,
58, 59, 60, 62, 82, 63
```

Only after this comparison should dynamic fields and `82` be investigated.

## 12. New Rule – Official QR First

Future reverse-engineering should follow:

```text
Official QR
   ↓
Decode
   ↓
Understand
   ↓
Generate controlled variation
   ↓
Scan
   ↓
Payment test
```

Not:

```text
Guess structure
   ↓
Generate QR
   ↓
Invalid QR
   ↓
Guess again
```

## 13. New Project Architecture

The long-term architecture remains possible:

```text
D365 / POS
     │
     │ amount + reference
     ▼
QR REST API
     │
     ▼
DuitNow QR Engine
     ├── Payload Builder
     ├── TLV Encoder
     ├── CRC16
     ├── Integrity / Acquirer Adapter
     └── QR Renderer
```

The engine must be based on a legitimate Merchant/Acquirer profile and validated integration model, not copied from a personal P2P Receive QR.

## 14. Current Status

### Frozen / Secondary Research

```text
RHB Personal Receive / P2P Dynamic QR
```

Useful for understanding P2P QR, `52=0000`, dynamic amount, RHB `82` behavior, and scanner-vs-payment authorization. It is **not** the development baseline.

### New Main Research

```text
RHB Merchant Presented Dynamic QR
        ↓
RHB Reflex / Business Merchant flow
        ↓
Official samples
        ↓
Decode
        ↓
Compare
        ↓
Validate with UOB / other bank
        ↓
Build engine
```

## 15. Final Principle

The project goal is not:

> Make a QR that looks like an RHB QR.

The real goal is:

> **Understand and implement a legitimate Merchant Presented Dynamic DuitNow QR that an Acquirer and participating banks can process.**

That requires separating:

1. PayNet QR data format
2. Merchant/acquirer identity
3. Dynamic transaction data
4. Integrity/authentication mechanism
5. Acquirer backend validation
6. Payment processing

Only after these are understood should the QR generation API be considered production-ready.