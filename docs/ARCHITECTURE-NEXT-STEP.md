# Architecture – Next Step

## Target

Expose a REST API from D365 / ERP / POS that accepts amount and reference and eventually returns a valid Merchant Presented Dynamic DuitNow QR.

## Architecture

~~~text
D365 / POS
    |
    | amount + reference
    v
QR REST API
    |
    v
DuitNow QR Engine
    +-- Payload Builder
    +-- TLV Encoder
    +-- CRC16
    +-- Integrity / Acquirer Adapter
    +-- QR Renderer
~~~

## Important restriction

Do not implement the production Merchant QR generator from the historical RHB P2P samples.

## Required next evidence

1. Genuine RHB Reflex Merchant Dynamic QR
2. Multiple official samples
3. Controlled amount variations
4. Controlled transaction-reference variations
5. Scan result from multiple participating banks
6. Successful payment result
7. Only then determine what can be generated independently