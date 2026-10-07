# OCBC OneCollect Dynamic QR Research

## Purpose

OCBC OneCollect was studied as a merchant-oriented reference.

## Observed merchant profile

~~~
00=02
01=12
26-00=A0000006150001
26-01=504324
26-02=MJ0X5KZI4VYSRTFAC9YR2LFMVRAR
52=7338
53=458
58=MY
59=MGX (MALAYSIA) SDN. BHD.
60=SELANGOR
62-03=MGX (MALAYSIA) SDN. BHD.
62-07=10000001
~~~

## Dynamic observations

- 54: amount
- 62-01: bill/reference number
- 62-05: reference label
- 82: integrity data
- 63: CRC

Observed 62-05 values included Unix timestamp-like values such as 1791339779, 1791339797, 1791339847, 1791340431, 1791340636 and 1791340773.

82 values were 64-character hexadecimal strings and changed between samples. Simple SHA-256 candidate calculations did not reproduce the observed values.

## Conclusion

OCBC provides useful merchant Dynamic QR comparison data, but the exact 82 algorithm remains unresolved.