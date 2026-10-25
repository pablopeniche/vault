# One bench, about $5,000, and the first numbers for the three checks

The P0 bench is the first stop on the [prototype path](spec.html): one table of off-the-shelf parts, no Vault-made hardware, no secure elements, nothing a deployment would trust. Research earbuds stand in for the earbuds, two muscle-sensing armbands for the wristbands, an analog keyboard for the keyboard, a signal generator and a microcontroller board for the body code, and a Raspberry Pi for the hub. The bench exists because none of the three core checks has been measured: skull-versus-microphone voice matching against replay, per-key pairing of muscle bursts with key presses, and a body code carried from the ear to the wrists and the keycaps. An agar-saline phantom stands in for the owner during the body-code sweeps, so those numbers repeat day to day, and short live runs on the owner keep them honest. Everything is on sale today, the two research pieces arrive made-to-order in two to three weeks, and the whole list costs about $5,000 before tax and shipping.

*Prices are vendor prices checked in October 2026, before tax and shipping. The earbuds are quoted in euros and converted at about $1.12. "Proposal" marks design choices made for the bench, and the pass marks are proposals carried over from the hardware spec, not established benchmarks.*

## 1. The bench: what P0 measures, what it defers

P0 answers one question: do the three core checks work at all, on parts you can buy this month? The [hardware spec](spec.html) puts it first in the build plan for exactly that reason. Everything after it, the device boards of P1 and the alpha rig of P2, assumes these numbers exist.

| Check | Question | P0 pass mark (proposal) |
|---|---|---|
| Same voice | Did the wearer's own throat produce this speech? | Dictation from the wearer accepted at least 97% of the time, loudspeaker replay rejected |
| Same hands | Did the owner's own fingers press these keys? | At least 95% of keys paired in 20-key windows |
| Body code | Is the earbud's signal on the body that pressed the key? | Detected on at least 99% of presses at a few microamps |

What P0 defers is everything that makes the rig a product. No device signs anything, because the Raspberry Pi hub has no trusted execution environment and no secure elements are on the bench. The camera and the face check are P1 work, and the fingerprint key waits anyway: the FPC2534 development kit is listed at $170 with restock estimated January 2027 [1]. The bench also measures something the spec asks for but does not have: how much a shared ground changes the body channel, since the published body-channel prototypes all floated their loops, decoupling lab instruments from ground to simulate battery-powered devices [2]. One owner and two colleagues are enough wearers for P0; the pass marks are per-owner numbers, and VAuth's 18-user study remains the reference scale [3].

## 2. Shopping list: every part, priced

Three groups: the stand-ins for Vault's devices, the bench instruments that drive and measure the body code, and the consumables. Prices checked October 2026.

**Stand-ins for the rig.**

| Part | Stands in for | Why this one | Price |
|---|---|---|---|
| OpenEarable 2.0, developer bundle (a left and right pair) | The earbuds | The open research earbud: inner and outer microphones plus a 3-axis bone-conduction sensor, recorded on one device clock to microSD, mics at up to 48 kHz and the bone channel at up to 6.4 kHz [4, 5]. BLE streaming tops out at 800 Hz, so the bench records to card | €2,348, about $2,630; made to order, ships in 2–3 weeks [6] |
| MindRove armband ×2 | The wristbands | 8 channels of raw sEMG at 500 Hz per band (0–250 Hz bandwidth, 24-bit), 8+2 stainless electrodes, Wi-Fi to the hub, Python SDK on Linux; 4–6 hours per charge [7] | $679 each on current sale (lists at $729), $1,358 |
| Wooting 80HE | The keyboard | Analog Hall-effect switches, every key scanned at 8 kHz, 0.1–4.0 mm travel reported per key, with an open analog SDK [8] | $199.99 |
| Raspberry Pi Development Kit for Compute Module 5 (4 GB, wireless) | The hub | The spec's prototype hub in one box: the module, IO board, power supply, cooler and antennas [9] | $195 |

**Bench instruments for the body code.**

| Part | Role | Why this one | Price |
|---|---|---|---|
| Digilent Analog Discovery 3 | The body-code transmitter, and the bench meter | A 2-channel 14-bit waveform generator and 2-channel 125 MS/s oscilloscope on USB: one AWG drives the ear electrode, the other channels measure levels and leakage, and WaveForms scripts it all from Python — including a software lock-in amplifier for the small carrier signals [10] | $379 |
| NUCLEO-G474RE | The receiver for the wrist electrode and the electrode keycap | The spec's keycap correlator chip on a $20 board: five 12-bit ADCs at 4 Msps and a CORDIC unit for the matched filter [11] | $20 |
| Two OPA320 buffers on SOT-23 adapters, plus passives | The receiver front end | 0.9 pA input bias keeps the electrodes high-impedance, the same part the spec puts behind each keycap [12] | About $25 (estimate) |

**Electrodes, the phantom, and small parts.**

| Part | Role | Notes | Price |
|---|---|---|---|
| Kendall Ag/AgCl foam electrodes, 50-pack ×2 | Skin electrodes: the ear transmitter, the wrist receiver, the sync pulse | Pre-gelled, snap connectors, the usual research-grade consumable [13] | $24.99 each, $49.98 |
| Copper tape, wire, BNC leads, breadboard | The electrode keycap and the harness | A stock keycap wrapped in copper foil over a spring contact, wired to the receiver: the hand-made keycap the [spec](spec.html) calls for | About $60 (estimate) |
| Agar, salt, PVC pipe, two containers, gloves | The body phantom (section 5) | Agar-saline mixed to the muscle range; agar phantoms hold conductivity between about 0.02 and 1.23 S/m and keep their shape for a year [15, 16] | About $60 (estimate) |
| Conductivity meter, piezo sounder, finger cot, acrylic rod | Phantom checks, the sync chirp, the two press tools | The meter verifies each phantom mix before a sweep; the agar-filled cot and the rod are the paired press test of section 5 | About $50 (estimate) |
| Any powered 3.5 mm speaker | The loudspeaker attack | Replays the owner's recorded voice at the wearer | About $30 (estimate) |
| microSD cards, USB-C audio dongle, spares | Storage and replay plumbing | OpenEarable records to microSD and recommends the Micron 64 GB card; the dongle gives the hub an audio jack for replays [5] | About $60 (estimate) |

The itemized total is about $5,100, of which the earbuds and the two bands are about $4,000. Not on the list on purpose: the SE051 evaluation board and all signing (P1), the camera module and the face check (P1), and the AI HAT+ 2 at $200 [18], which joins when the camera and on-device transcription arrive. The Raspberry Pi alone runs all three P0 checks.

## 3. Wiring and sync: one clock, one shared ground

Everything lands on the hub, which is the only clock on the bench. The body code bypasses the hub entirely: it runs from the generator's electrode, through the wearer or the phantom, to the receiver's electrodes, exactly as it will between the earbuds, the wristbands and the keycaps.

| Device | Link to the CM5 hub | What flows |
|---|---|---|
| OpenEarable 2.0 | BLE while worn; microSD card pulled after each session | Sensor control and 800 Hz streams over BLE; the full-rate 48 kHz mics and 6.4 kHz bone channel arrive as files [5] |
| MindRove armbands ×2 | Wi-Fi, one SDK connection per band | 8 × 500 Hz sEMG plus IMU per band [19] |
| Wooting 80HE | USB | Analog key positions at 8 kHz, read through the analog SDK [20] |
| NUCLEO-G474RE | USB serial | Per-press correlation results, and the sync pulses it fires |
| Analog Discovery 3 | USB, from the hub or from a battery laptop | The AWG out to the ear electrode; the scope back from the receivers and the leakage probe [10] |
| Loudspeaker | USB-C audio dongle | Replay attacks, timed from the hub so they land in the log |

The body-code loop closes through ground, and the bench measures both configurations the spec asks about. With the AD3 on the hub's USB, the generator, the receiver and the keyboard share the hub's ground, which is what the product will do; with the AD3 on a battery laptop the loop floats, which is how the published prototypes ran, their instruments decoupled from ground to stand in for battery-powered devices [2]. DiamondTouch is the clear exception: its receivers shared a ground with the transmitter [14]. Section 5 measures the difference.

Sync is a measurement of its own. The earbuds and the bands cannot share the hub's clock natively, so the Nucleo fires a physical sync pulse every session start and every 60 seconds: it drives a piezo chirp pressed to the earpiece, which lands in both the microphone and the bone channel, and it injects a skin pulse near each band, which lands on all eight EMG channels. Post-hoc cross-correlation gives every stream its offset and drift against the hub, and the residuals are a reported result. The voice check needs ±5 ms and the keystroke pairing ±50 ms, and the bench targets residuals under 1 ms after correction. All streams ingest through the Lab Streaming Layer, so the analysis reads one timeline [21]. The Wooting needs no such help: its keys scan at 8 kHz, so a key-down lands on the hub within 0.125 ms of actuation.

## 4. Software per check: what runs where

One Python code base on the CM5, one process per source, everything written to disk per session: the raw streams, the parameters, and the firmware and script hashes. The pass-mark numbers in section 6 are all computed by the same offline code that the live path uses.

**Same voice.** The pipeline takes the microSD files: the inner microphone at 48 kHz and the bone channel at 6.4 kHz, resampled to a common rate. Voice activity detection finds the voiced 20–40 ms frames on the microphone; for each frame, the normalized cross-correlation between the two channels must peak within ±5 ms. That is VAuth's structure, feature matching between body-conducted and air-conducted speech, updated from their 2017 hardware [3]. An utterance is accepted when at least 80% of its voiced frames match (proposal), with the correlation threshold set per wearer on ten calibration utterances. Accepted audio is transcribed offline with Whisper to confirm the dictation itself survives the gate [22].

**Same hands.** The MindRove SDK streams both bands [19]; the Wooting analog SDK feeds key travel, with the tachywooting Python bindings logging per-key 0.0–1.0 positions with microsecond timing [20, 23]. Per band: bandpass 20–250 Hz, envelope, then burst detection with a Teager–Kaiser energy threshold. Pairing assigns each key-down exactly one burst that starts 80–200 ms before it, from the correct hand, with a plausible finger from the channel topography; the timing window comes from the forearm-muscle measurements Gazzari et al. report from Dennerlein's key-switch studies, where bursts begin about 150 ms before a key bottoms out [24]. The score is per 20-key window, because at typing speed the bursts overlap and even owner-trained decoders misread 7–11% of single characters, as emg2qwerty showed across 108 users [25]. A 200-key calibration run per owner fixes the channel-to-finger templates and the thresholds.

**Body code.** A WaveForms script drives the AWG: a carrier at 100, 250 or 500 kHz, on-off keyed by a 127-chip m-sequence at 10–100 kb/s, repeated throughout the press. Series resistance sets the skin current and the scope channel verifies it across a shunt, a few microamps, about 2,000 times below the contact current where pain begins [26]. On the receive side, each electrode feeds its OPA320 buffer into a 4 Msps ADC channel on the Nucleo, whose firmware mixes at the carrier and runs the matched filter against the known sequence, using the CORDIC unit; the AWG's trigger output clocks the Nucleo, so demodulation is synchronous, the DiamondTouch approach [14]. The Wooting's travel signal gates the keycap electrode: it is listened to only while a press is in flight. The Nucleo reports a correlation peak and a level per press, plus the sync pulses.

## 5. Phantom tests: the body code without a body

The phantom exists for repeatability. A person's impedance, posture and sweat change hour to hour; an agar-saline phantom holds a set conductivity and geometry for a year [15, 16]. Intrabody-communication work already uses liquid phantoms of 0–1 S/m to cover the tissue range [17], so the bench builds one rather than inventing a new method.

Phantom A stands in for the owner: a torso block and a 60 cm arm tube of agar-saline mixed to about 0.3 S/m, inside the muscle range at these frequencies (proposal), verified with a conductivity meter before each sweep. The transmitter electrode sits at the tragus position, the receiver electrodes at the wrist position and under the keycap, at the same spacings a seated owner would have. Phantom B, a smaller saline tank, plays the second person. An agar-filled finger cot on a stick, coupled to the arm, presses the keycap; an acrylic rod presses it without coupling, the mechanical-plunger attack the [rig page](index.html) describes.

| Sweep | What varies | What is recorded |
|---|---|---|
| Level | Carrier 100, 250, 500 kHz; skin current 1, 3, 10 µA; hub-shared ground vs floating | Signal at the wrist and keycap electrodes, as dB above the receiver's noise floor, with the current actually measured |
| Leakage | Probe electrode at 5, 10, 20, 40 cm off the body; phantom B touching vs not touching | Level vs distance, and whether the code crosses to a stranger through touch |
| Press | 1,000 presses each: agar finger, acrylic rod | Detection rate with the code present vs absent, and the per-press margin |
| Rate | m-sequence at 10, 50, 100 kb/s | Correlation margin vs rate, and code errors |

Leakage at 100 kHz should stay under about 10 cm, against about 40 cm at 1 MHz, which is why the carriers start low [27]. Touch is expected to carry the code to phantom B, a relay risk that body-channel defenses still struggle to bound [28]; the bench quantifies how much crosses, in dB, rather than assuming it.

Then the same levels, currents and press counts run live on the owner, one short session, same few microamps, same electrodes. The phantom buys repeatability and the owner buys validity, and the phantom-to-skin delta is itself one of the bench's reported numbers.

## 6. Pass marks: how each one is measured

Every pass mark below is a rate with its raw counts and a 95% binomial interval, computed by the offline path, per wearer, from logged sessions. With 200 utterances the interval on 97% is about ±2.4 points, so the bench records margins, not just pass or fail (proposal).

| Check | Pass mark (proposal) | Protocol | Metric |
|---|---|---|---|
| Same voice | Dictation from the wearer accepted at least 97% of the time; loudspeaker replay rejected | 3 wearers × 200 utterances of ordinary dictation; each wearer's 50 recorded utterances replayed from 30 cm at 75 dB and 90 dB; 50 utterances spoken live by each non-wearer while the wearer wears the earbuds | Acceptance: share of the wearer's utterances with ≥80% of voiced frames matching within ±5 ms. Rejection: share of replays and impostor utterances below that bar, VAuth's 97% and 0.1% as the reference [3] |
| Same hands | At least 95% of keys paired in 20-key windows | 3 typists × 5,000 keys of ordinary prose at their own speed, after a 200-key calibration each; roughly 750 windows in total | Per non-overlapping 20-key window: the share of key-downs with exactly one burst 80–200 ms earlier, the right hand and a plausible finger; also the orphan-burst rate. Report the median and 10th-percentile windows per typist [24, 25] |
| Body code | Detected on at least 99% of presses at a few microamps | 1,000 presses on the phantom with the agar finger; 1,000 live presses by the owner; 1,000 acrylic-rod presses as the negative control; all at ≤10 µA measured skin current, targeting 1–5 µA | Detection: correlation peak above a threshold fixed on 100 calibration presses. False positives: rod presses detected, target ≤1%. The level and leakage tables of section 5 are required artifacts alongside it [26] |
| Sync | Supporting number, not a pass mark | Sync pulses at session start and every 60 s, every session | Per-stream offset and drift after correction, and the worst-case residual, target under 1 ms |

A check that misses its mark is a result, not a failure of the bench: it feeds P1 directly. If the MindRove bands miss bursts, that is evidence for the per-electrode buffers the spec already worries about; if the shared ground costs the channel tens of dB, the earbud's transmitter design changes before a PCB exists.

## 7. Sources

1. [DigiKey, FPC2534 development kit listing](https://punchouttest.digikey.com.mx/en/products/detail/fingerprint-cards-ab/100026232/25649788). *Distributor listing.*
2. [Roeschlin, Martinovic and Rasmussen, device pairing through the body (NDSS 2018)](https://www.cs.ox.ac.uk/files/9833/pairing.pdf). *Peer-reviewed.*
3. [Feng, Fawaz and Shin, "Continuous Authentication for Voice Assistants" (VAuth, MobiCom 2017)](https://ar5iv.labs.arxiv.org/html/1701.04507). *Peer-reviewed; 18 users.*
4. [Röddiger et al., OpenEarable 2.0 (Proc. ACM IMWUT 9(1), 2025)](https://dl.acm.org/doi/10.1145/3712069). *Peer-reviewed.*
5. [OpenEarable 2.0 product page](https://open-earable.teco.edu/index.html). *Vendor page.*
6. [OpenEarable 2 developer starter bundle](https://shop.openearable.com/products/openearable-2-starter-bundle). *Vendor store.*
7. [MindRove armband product page](https://mindrove.com/product/emg-armband). *Vendor page.*
8. [Wooting 80HE product page](https://wooting.io/wooting-80he). *Vendor page; figures are vendor claims.*
9. [Raspberry Pi Compute Module 5](https://www.raspberrypi.com/products/compute-module-5). *Vendor page.*
10. [Digilent, Analog Discovery 3](https://digilent.com/shop/analog-discovery-3). *Vendor store.*
11. [STMicroelectronics, NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html). *Vendor page.*
12. [TI OPA320 operational amplifier](https://www.ti.com/product/OPA320). *Vendor product page.*
13. [OpenBCI, Kendall EMG/ECG foam electrodes, 50-pack](https://shop.openbci.com/products/kendall-emg-ecg-foam-solid-gel-electrodes-50-pack). *Vendor store.*
14. [Dietz and Leigh, "DiamondTouch" (MERL TR2003-125)](https://www.merl.com/publications/docs/TR2003-125.pdf). *Technical report.*
15. [Kato and Ishida, agar phantom for tissue simulation (Phys. Med. Biol., 1987)](https://pubmed.ncbi.nlm.nih.gov/3562535/). *Peer-reviewed.*
16. [NaCl doping and the conductivity of agar phantoms (Materials Science and Engineering: C, 2011)](https://www.sciencedirect.com/science/article/pii/S0928493110002110). *Peer-reviewed.*
17. [Towards wideband characterization of in-body to on-body intrabody communication channels (Bioengineering, 2025)](https://www.mdpi.com/2306-5354/13/1/42). *Peer-reviewed.*
18. [Raspberry Pi AI HAT+ 2](https://www.raspberrypi.com/products/ai-hat-plus-2). *Vendor page.*
19. [MindRove SDK documentation](https://docs.mindrove.com/). *Vendor documentation.*
20. [Wooting Analog SDK (GitHub)](https://github.com/WootingKb/wooting-analog-sdk). *Open-source project.*
21. [Lab Streaming Layer (GitHub)](https://github.com/labstreaminglayer/labstreaminglayer). *Open-source project.*
22. [Whisper (OpenAI, GitHub)](https://github.com/openai/whisper). *Open-source model.*
23. [tachywooting, Python bindings for Wooting analog keyboards (PyPI)](https://pypi.org/project/tachywooting). *Open-source project.*
24. [Gazzari et al., "My(o) Armband Leaks Passwords" (IMWUT, 2021)](https://ar5iv.labs.arxiv.org/html/2112.02382). *Peer-reviewed.*
25. [Sivakumar et al., "emg2qwerty" (NeurIPS 2024)](https://arxiv.org/html/2410.20081v1). *Peer-reviewed; 108 users.*
26. [Maity et al., safety of capacitive body-channel communication (2020)](https://par.nsf.gov/servlets/purl/10249173). *Peer-reviewed.*
27. [Maity, Modak and Sen, sub-microwatt body-channel communication node (IEEE JSSC 56(3), 2021)](https://doi.org/10.1109/JSSC.2020.3041874). *Peer-reviewed.*
28. [OneTouch: body-channel touch authentication (USENIX Security 2025)](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-351-yan-yihui.pdf). *Peer-reviewed.*
