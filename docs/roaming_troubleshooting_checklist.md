# LTE Roaming Integration Troubleshooting Checklist

This checklist is for investigating LTE roaming integration problems during onboarding, testing, and technical acceptance.

The project uses simulated signaling events. This checklist explains how a real integration engineer would investigate similar problems using signaling traces, Wireshark filters, logs, and partner configuration checks.

---

## 1. Basic Session Information

Before troubleshooting, collect the basic session details.

| Item          | What to check                                              |
| ------------- | ---------------------------------------------------------- |
| IMSI          | Subscriber identifier used in the test                     |
| HPMN          | Home network/operator                                      |
| VPMN          | Visited network/operator                                   |
| APN           | APN requested by the subscriber/session                    |
| Test time     | Timestamp of the failed test                               |
| Session ID    | Internal test/session reference                            |
| Partner       | MNO or roaming partner under test                          |
| Failure point | Attach, authentication, session setup, tunnel, or charging |

---

## 2. First Question: Where Did the Flow Fail?

Check the roaming flow in this order:

1. Attach request received?
2. Authentication request sent?
3. Authentication response received?
4. Session creation request sent?
5. Session creation response received?
6. GTP tunnel established?
7. Charging/CDR trigger generated?

If one step is missing, start troubleshooting from that point.

---

## 3. Authentication / Diameter Checks

Use this section when the failure is around authentication request or authentication response.

| Check                 | What it means                                        | Action                                               |
| --------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| AUTH_REQUEST exists   | The visited/core side sent authentication request    | Confirm Diameter routing toward home network         |
| AUTH_RESPONSE exists  | Home network responded                               | Check response time and result code                  |
| AUTH_RESPONSE missing | Authentication did not complete                      | Check Diameter peer, route, firewall, or roaming hub |
| TIMEOUT result        | Home network or routing path did not respond in time | Check IPX/roaming hub latency and peer availability  |
| Diameter error        | Diameter response contains an error                  | Review result code and partner configuration         |

### Useful Wireshark filters

* `diameter`
* `tcp.port == 3868 || sctp.port == 3868`
* `diameter.flags.error == 1`
* `diameter.Result-Code`

### Typical root causes

* Diameter peer not reachable
* wrong Diameter realm or routing rule
* roaming partner not configured
* firewall blocking Diameter traffic
* IPX/roaming hub connectivity problem
* home network response delay

---

## 4. APN and GTP Session Setup Checks

Use this section when authentication succeeds but data session setup fails.

| Check                          | What it means                         | Action                                                  |
| ------------------------------ | ------------------------------------- | ------------------------------------------------------- |
| APN value correct              | Subscriber requested the expected APN | Compare with agreed roaming/APN configuration           |
| APN mismatch                   | Wrong APN was used                    | Check partner APN mapping and packet core configuration |
| CREATE_SESSION_REQUEST exists  | GTP session setup started             | Check request content and APN                           |
| CREATE_SESSION_RESPONSE exists | Packet core responded                 | Check cause value                                       |
| CREATE_SESSION failed          | Session could not be established      | Inspect GTPv2 cause code and APN policy                 |
| GTP tunnel missing             | User-plane tunnel was not established | Check S8/S5 path, routing, and gateway configuration    |

### Useful Wireshark filters

* `gtpv2`
* `gtpv2.message_type == 32 || gtpv2.message_type == 33`
* `gtpv2.cause`
* `frame contains "iot.sateliot"`

### Typical root causes

* wrong APN
* APN not provisioned
* partner APN mapping mismatch
* packet core policy rejection
* gateway selection issue
* S8/S5 tunnel setup failure

---

## 5. Roaming Partner and Configuration Checks

Use this section when the visited network or partner is not allowed, not recognized, or not correctly routed.

| Check                     | What it means                                   | Action                                       |
| ------------------------- | ----------------------------------------------- | -------------------------------------------- |
| VPMN is allowed           | Visited network exists in allowed partner list  | Confirm partner agreement and configuration  |
| VPMN unknown              | Partner is not recognized                       | Add or correct partner configuration         |
| Diameter routing exists   | Authentication route exists toward home network | Check realm, peer, and routing table         |
| APN mapping exists        | Partner APN maps to expected packet core APN    | Check APN translation/mapping                |
| Test SIM allowed          | IMSI range is allowed for roaming test          | Check test subscriber profile                |
| Launch readiness approved | Partner passed technical acceptance             | Confirm test report and acceptance checklist |

### Typical root causes

* roaming partner not configured
* missing roaming agreement setup
* wrong Diameter realm
* wrong IMSI range
* test SIM not provisioned
* APN mapping missing
* partner not approved for launch

---

## 6. Latency and Transport Checks

Use this section when the signaling flow exists but responses are slow, delayed, or unstable.

| Check                | What it means                                       | Action                                                      |
| -------------------- | --------------------------------------------------- | ----------------------------------------------------------- |
| High latency events  | Signaling response time is above expected threshold | Check network path and peer response time                   |
| TCP retransmissions  | Packets are being resent                            | Check packet loss, firewall, routing, or congestion         |
| TCP resets           | Connection is being closed unexpectedly             | Check peer behaviour, firewall policy, or application crash |
| DNS failure          | Peer hostname cannot be resolved                    | Check DNS configuration                                     |
| ICMP unreachable     | Peer/network path is unreachable                    | Check routing and firewall                                  |
| Intermittent timeout | Failure is not consistent                           | Repeat tests and compare timestamps                         |

### Useful Wireshark filters

* `tcp.analysis.retransmission`
* `tcp.flags.reset == 1`
* `dns.flags.rcode != 0`
* `icmp`

### Typical root causes

* IPX or roaming hub delay
* firewall inspection delay
* overloaded signaling peer
* route instability
* DNS resolution problem
* packet loss or congestion

---

## 7. Launch Readiness and Acceptance Checks

Use this section before moving a roaming integration from testing to commercial launch.

| Check                 | Acceptance condition                              |
| --------------------- | ------------------------------------------------- |
| Attach procedure      | Attach request and response path verified         |
| Authentication        | Authentication request and response successful    |
| Diameter routing      | Correct routing toward home network verified      |
| APN/session setup     | Expected APN accepted and session established     |
| GTP tunnel            | Tunnel setup confirmed                            |
| Charging trigger      | Charging/CDR event generated                      |
| Error handling        | Known failure cases documented                    |
| Latency               | Signaling latency within acceptable range         |
| Partner configuration | MNO/VPMN configuration verified                   |
| Test report           | Issues, results, and acceptance status documented |

## Final Decision

After testing, classify the integration as one of the following:

| Status                 | Meaning                                                   |
| ---------------------- | --------------------------------------------------------- |
| PASS                   | Ready for launch                                          |
| PASS WITH OBSERVATIONS | Minor issues exist but launch may proceed with monitoring |
| FAIL                   | Blocking issue exists; launch should not proceed          |

## Documentation to Keep

For each integration test, keep:

* test date and time
* partner/MNO name
* IMSI/test subscriber
* APN used
* signaling trace reference
* detected issue list
* troubleshooting actions
* final acceptance status
* responsible internal/external team
