# RHB Personal / P2P Dynamic QR Research

> STATUS: FROZEN / HISTORICAL. This is not the baseline for Merchant Presented Dynamic QR.

## Why it was frozen

The original RHB samples came from the RHB mobile banking Receive / Request Money flow. They repeatedly contained 01=12 and 52=0000.

PayNet identifies 52=0000 with P2P usage.

## Observed RHB values

- AID: A0000006150001
- Acquirer ID: 564160
- Recipient ID: 221217000072525RHBQR000000

## Official samples

### RM1.00

~~~
00020201021226580014A000000615000101065641600226221217000072525RHBQR000000520400005303458540115802MY5912HOH HUN YUEN6002MY82649574E3E39536D3AEA8B570F607C5BCCB489EFDCBB0FB1EFCB0FFA8D86E38A30263044C49
~~~

### RM0.05

~~~
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.055802MY5912HOH HUN YUEN6002MY826467CD0FED69A253E4A50378658CFDF0E5059614CF31B5957AF0F91B8D2CD07C67630423F3
~~~

### RM0.01

~~~
00020201021226580014A000000615000101065641600226221217000072525RHBQR00000052040000530345854040.015802MY5912HOH HUN YUEN6002MY826443A6E0B8C92621538FA72BB3934D71934309EC824BD1AD76C19786DB03FCCABC363047BA3
~~~

## Tests

- 62-05=INV26-001: UOB displayed Recipient Reference in one test, but transfer could not proceed.
- 62-01 and 62-08 were also tested.
- Changing 52=0000 to 52=9999 did not convert the QR into a Merchant QR.
- Removing/copying/modifying 82 produced Invalid QR in some tests.

## Real payment test

A self-generated RHB-style P2P Dynamic QR was successfully paid from Affin for RM1.00. The payment showed recipient HOH HUN YUEN and amount RM1. This confirms P2P processing, not Merchant QR behavior.

## Conclusion

Freeze this track for Merchant QR development.