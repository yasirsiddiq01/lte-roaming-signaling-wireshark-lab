# Wireshark Filters for LTE Roaming Signaling Troubleshooting

This document lists useful Wireshark display filters for investigating LTE roaming signaling issues in a roaming integration test.

The current project uses simulated signaling events, not real PCAP files. These filters are included to document how similar issues would be investigated in Wireshark during real operator integration testing.

---

## 1. Diameter Signaling

Diameter is commonly used for LTE roaming authentication and subscriber data exchange.

### Show all Diameter traffic

```wireshark
diameter
```

### Show Diameter messages on common Diameter ports

```wireshark
tcp.port == 3868 || sctp.port == 3868
```

### Show Diameter errors

```wireshark
diameter.flags.error == 1
```

### Show Diameter result codes

```wireshark
diameter.Result-Code
```

### Troubleshooting use

Use these filters when checking:

- authentication timeout
- missing authentication response
- roaming partner routing problem
- home network response delay
- Diameter peer configuration issue

---

## 2. GTPv2 Signaling

GTPv2 is used for LTE session management. In roaming testing, it is important for checking session creation, APN handling, and tunnel setup.

### Show all GTPv2 traffic

```wireshark
gtpv2
```

### Show GTPv2 Create Session messages

```wireshark
gtpv2.message_type == 32 || gtpv2.message_type == 33
```

### Show GTPv2 cause values

```wireshark
gtpv2.cause
```

### Troubleshooting use

Use these filters when checking:

- create session failure
- GTP tunnel setup issue
- APN rejection
- packet core session establishment problem

---

## 3. S1AP Signaling

S1AP is used between the eNodeB and MME in LTE attach and mobility procedures.

### Show all S1AP traffic

```wireshark
s1ap
```

### Show Initial UE Message

```wireshark
s1ap.procedureCode == 12
```

### Troubleshooting use

Use these filters when checking:

- attach request visibility
- whether the subscriber attach attempt reached the core network
- initial signaling failure before authentication


---

## 4. DNS and IP Connectivity

Roaming integrations may fail because of DNS, routing, firewall, transport, or IP connectivity problems.

### Show DNS traffic

```wireshark
dns
```

### Show failed DNS responses

```wireshark
dns.flags.rcode != 0
```

### Show ICMP traffic

```wireshark
icmp
```

### Show TCP retransmissions

```wireshark
tcp.analysis.retransmission
```

### Show TCP reset packets

```wireshark
tcp.flags.reset == 1
```

### Troubleshooting use

Use these filters when checking:

- roaming hub or IPX connectivity
- DNS resolution problem
- peer reachability issue
- firewall or transport-layer failure
- high latency or retransmission problem


---

## 5. APN-Related Troubleshooting

APN mismatch can cause roaming session setup failure. In a real packet trace, the APN may appear inside GTPv2 session setup messages or packet core signaling details.

### Search packet details for expected APN

```wireshark
frame contains "iot.sateliot"
```

### Search packet details for wrong APN

```wireshark
frame contains "wrong.apn"
```

### Troubleshooting use

Use these filters when checking:

- APN mismatch
- incorrect roaming APN configuration
- rejected packet data session
- wrong packet core or partner-side configuration


---

## 6. Session-Level Investigation Approach

A practical Wireshark investigation should follow the signaling flow step by step.

### Suggested investigation order

1. Confirm that the attach request is visible.
2. Check whether the Diameter authentication request was sent.
3. Check whether the Diameter authentication response was received.
4. Check Diameter result codes or timeout behaviour.
5. Check GTPv2 create session request and response.
6. Check the APN value.
7. Check GTPv2 cause values if session setup failed.
8. Confirm whether the GTP tunnel was established.
9. Confirm whether charging or CDR trigger was generated.
10. Check DNS, TCP retransmissions, resets, and latency if signaling is missing or delayed.

### Troubleshooting purpose

This order helps identify where the roaming procedure failed:

- radio/core attach stage
- authentication stage
- Diameter routing stage
- APN/session creation stage
- GTP tunnel setup stage
- charging/billing trigger stage
- IP connectivity or transport stage


---

## 7. Mapping to This Project

This table maps the simulated issues in this lab to the type of Wireshark investigation that would be useful in a real roaming integration test.

| Simulated issue in this project | Wireshark investigation area |
|---|---|
| AUTH_RESPONSE timeout | Diameter filters and response timing |
| APN_MISMATCH | GTPv2 session messages and APN string search |
| CREATE_SESSION_REQUEST failed | GTPv2 cause values |
| ROAMING_PARTNER_NOT_ALLOWED | Diameter routing and partner configuration |
| HIGH_SIGNALING_LATENCY | TCP retransmission, delay, routing path, IPX/roaming hub latency |
| MISSING_SIGNALING_EVENT | Session trace sequence inspection |
| Missing CHARGING_TRIGGER | Charging/CDR event validation after session setup |

---

## Note

This document is for portfolio learning and interview demonstration. It does not use private operator traffic, real subscriber data, or confidential roaming traces.