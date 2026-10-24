# Seven pieces, four checks, all required

Seven pieces of hardware run four checks every few seconds. **Same heartbeat:** one heartbeat, seen at the chest, the ear, the face and the finger on schedule. **Same hands:** wrist muscles that fire before every keystroke. **Same person:** the owner's ear canal, face or fingerprint, always freshly matched. **Custody:** nothing removed since the owner last proved who they are. The computer's keys stay alive only while all four hold. Most parts exist today as research hardware or developer kits; two, a microneedle ECG patch and wired sensing earbuds, have to be built.

*Numbers are typical seated-adult or lab values from the cited studies, and every threshold has to be calibrated per owner. Nothing here has been tested end to end. "Proposal" marks design choices made for Vault rather than measured results.*

## 1. The rig: seven pieces, one job each

| Piece | Where | Measures | Proves | Build it today with |
|---|---|---|---|---|
| Chest patch (microneedle ECG) | Chest, replaced every 1–2 weeks | Heartbeat (ECG) and electrode contact | The heartbeat clock; a single-use seal whose removal shows up within milliseconds [1, 3] | Movesense sensor, ECG at 125–512 Hz [4]. Microneedle ECG electrodes: research only, 14 days of wear in 3 people [2] |
| Wired earbuds | Both ears | In-ear pulse, ear-canal echo, in-ear sensor | The owner's identity every 1–3 seconds; ear pulse timing | Custom. Ear-canal echo identification reaches 98.7% in research [6]; the last wired heart-rate earbud was sold in 2014 [5]; research ear rigs already record ECG and pulse in the ear canal [36] |
| Ring | Index finger of the typing hand | Finger pulse, finger motion | Finger pulse timing; the finger moved before each key | Research ring with raw pulse up to 400 Hz [7]. Consumer rings expose no raw data |
| Wristbands (sEMG) | Both wrists | Muscle activity, 8–16 channels | Which hand and finger fired before each key; a soft identity signal | MindRove armband, 8 channels at 500 Hz, $679–729 each [9]. Meta's 16-channel, 2 kHz band keeps its raw signal private [8] |
| Analog keyboard with fingerprint key | Desk | Depth of every key at 8 kHz; fingerprint | Key events signed with their own timestamps; the owner's fingerprint on demand | Wooting 80HE, $199.99 [10], plus a fingerprint key paired the way Apple's Touch ID keyboard pairs [11] |
| IR camera, 60–120 fps | On the monitor | Infrared face, face pulse | The owner's face; face pulse timing | An integrated IR camera on an attested path, as in Windows Enhanced Sign-in Security [12], with signed frames and capture timestamps |
| Vault hub | Desk, cabled to the computer | Nothing itself | Runs the four checks, keeps one clock for every device, holds the keys | Custom: a secure element, like a hardware wallet |

The keyboard, camera and earbuds are cabled to the hub, because Bluetooth relays survive encryption and add only about 8 ms [29]. The patch, ring and wristbands pair with per-device keys and sign their own timestamps. Prototype parts: about €119 for the patch sensor, $1,400–1,800 for two wristbands and $200 for the keyboard. Prices for a research ring, custom earpiece, camera and hub were not found.

## 2. How they work together: every piece sits in at least two checks

The rig runs four checks at once. Each device feeds at least two of them, so an attacker who fakes or steals one piece still fails another check.

| Check | Question | Stops | Does not stop |
|---|---|---|---|
| Same heartbeat | Are the chest, ears, face and finger one living body, right now? | Replayed or injected video; a live deepfake, whose face pulse arrives late; devices split between two people | Someone wearing the owner's stolen devices, whose own heart keeps the timing consistent |
| Same hands | Did the hands wearing the bands press these keys? | AI agents, malware and injected USB devices; another person typing | One swapped key typed by the same finger; a forged band signal |
| Same person | Is this body the owner? | Another person wearing the owner's gear | A coerced owner |
| Custody | Has anything come off since the owner last proved who they are? | Gear handed to someone else mid-session | Gear stolen and re-anchored, which needs the owner's ear, face and fingerprint |

Each attack fails a different check. Stolen gear fails *same person*. A deepfake fails *same heartbeat*. An AI agent or a malicious USB cable fails *same hands*. Handing the gear over fails *custody*. Only a coerced owner passes all four, which is why the fingerprint key also takes a duress finger.

## 3. The two new checks, in milliseconds

Both checks compare events that one body produces in a fixed order, measured on different devices against one clock.

### Muscle to keystroke

Forearm flexor muscles fire about 150 ms before a key bottoms out and stop about 50 ms after it, and the finger starts moving about 83 ms before [13]. A detector can place a keystroke from wrist signals to within about 21 ms (one standard deviation), and finds 94% of keystrokes within ±50 ms [13]. Vault therefore pairs every signed key-down with exactly one muscle burst that starts between 200 ms before and 50 ms after it, in the right hand, from a plausible finger (proposal). The pairing runs both ways: a burst with no key also counts against the session. That closes the hole that broke the earlier ZEBRA wristband scheme, where the attacker's own typing decided when comparisons ran [14, 18].

Single keys are too noisy to judge. At 4.4 keys per second the bursts overlap, and even a decoder trained on its owner misreads 7–11% of characters [17]. Vault decides over windows of 20–50 keys, about 5–12 seconds. That catches injected input within seconds, but it cannot catch one swapped key typed by the same finger. Key travel and switch type shift the muscle timing by 20–40 ms, so the template is calibrated per owner and per keyboard [37]. A different person wearing the bands is also likely to be caught: wrist muscle patterns told people apart at about a 2.5% equal error rate across days, in a 43-person lab study [19]. No one has published this exact check, and every figure here is a lab result. The band stream is also a keylogger, so raw signals never leave the hub.

### Heartbeat timing

After each heartbeat, the pulse reaches the ear about 120–200 ms later and the finger about 200–270 ms later. The ear-to-finger gap is usually 48–80 ms [15, 16]. Absolute delays drift with blood pressure and posture: a 21 mmHg rise shortened the finger delay by 12 ms [21]. The gap between two sites is much steadier. On irregular beats the absolute delay jumped about 110 ms while the finger–ear gap moved 8 ms [16]. Vault checks the gaps, per owner, over 10–30 beats (proposal).

Video can't fake this because the next heartbeat is unpredictable. In healthy adults successive beat intervals differ by about 42 ms (RMSSD 42 ± 15 ms) [22]. A forger guessing beat times lands inside a ±20 ms window about 37% of the time, so ten beats in a row pass with a probability near 5 × 10⁻⁵. Owners with low variability need longer windows (inference from [22]). A live deepfake carries the pulse of the attacker driving it [23]. But rendering costs at least ~43 ms per frame, since the fastest real-time pipeline found ran at 23.5 frames per second [24]. Its face pulse therefore arrives late, at or after the finger's, instead of with the ear's. Inserting a chosen pulse into video is possible [28], but the forger would need the owner's live heartbeat ahead of time.

The check needs three things:
- a camera at 60 fps or more, since 30 fps alone leaves ±16.6 ms of ambiguity per beat [27];
- capture timestamps from the camera itself, because ordinary webcam pipelines add 91–310 ms of variable delay [25];
- a one-time calibration.

FaceHeart compared face and finger pulse rates in 2017 and named the delay itself as future work [26]. No one has tested the delay check yet.

## 4. If a piece is missing

Every piece must be on. Two rules keep that livable (proposal). *Missing* data lets trust fade for a few seconds: you look away, pause typing, or a sensor loses contact briefly. *Contradicting* data locks at once: a different face, a key with no muscle burst, or a beat off schedule.

| Piece off or failing | What goes blind | What Vault does (proposal) |
|---|---|---|
| Chest patch removed | Heartbeat clock, custody seal | Locks at once. A new single-use patch goes on during a fingerprint and face check |
| Earbuds out | Ear identity, ear pulse | Locks after a short grace period, about 30 s; re-checks the ear canal when they go back in |
| Ring off | Finger pulse, finger motion | Locks after a short grace period; re-anchors with the fingerprint key |
| A wristband off | Same hands | Typing stops reaching the computer at once; resumes after the band is back and the fingerprint key is touched |
| Face out of view | Face identity, face pulse | Nothing for short gaps, while the ear check carries identity; vault actions wait for the face |
| Unknown keyboard or USB device | Signed input | Its input is blocked |
| Hub unplugged | Everything | Keys expire within seconds; the computer locks |

## 5. The options, scored

| Option | Verdict | Why |
|---|---|---|
| Chest ECG patch | **Keep**, as the microneedle chest patch | The heartbeat clock every other timing is measured against. Not an identity signal |
| Microneedle or CGM sensor | **Keep**, merged into the chest patch | Microneedle electrodes recorded clean ECG for 14 days in research [2] and can be built single-use, so removal is final [1]. Glucose itself adds nothing |
| Wrist ECG band (Nymi-style) | **Drop** | Replayed ECG fooled it 81% of the time [20]. The chest patch gives a better heartbeat, and the wrist is needed for the muscle band |
| Watch or ring PPG | **Keep the ring, drop the watch** | The ring gives finger pulse timing and finger motion. Wrist pulse as identity collapsed in real-world use, to an MCC of 0.07–0.08 [30] |
| Wrist detection + secure ranging (Apple Watch) | **Drop** | Proves a token is nearby, not who is typing; Mac-only; Bluetooth relays add only ~8 ms [29, 31]. Cables to the hub replace it |
| sEMG band | **Keep**, on both wrists | The only signal that ties each keystroke to muscles [13] |
| DNA or metabolome | **Drop** | Rapid DNA takes about 90 minutes [32]; DNA is left on everything you touch [34]; metabolic profiles re-identify only about 40% of people after 7 years [33] |
| Touch ID keyboard or ESS fingerprint | **Keep**, in the keyboard | Identity on demand, the confirm button for vault actions, and a duress finger [11] |
| RGB webcam face | **Demote** | Never identity, because virtual cameras and injected frames can feed it [23, 35]. Useful only as a pulse sensor at 60+ fps with capture timestamps |
| IR face on an attested path (ESS) | **Keep** | The owner's face whenever they face the screen, over a camera path that software cannot feed [12] |
| Wired earbuds (new) | **Keep** | The ear-canal echo identifies the wearer in about a second, all day [6]; the cable rules out radio relay |
| Analog keyboard (new) | **Keep** | Every key event signed with its own timestamp, plus a depth curve per key [10] |

## 6. What is not proven yet

- **Neither new check has been run.** Muscle-to-keystroke pairing and heartbeat-gap checking are untested end to end; every number above comes from a separate lab study.
- **Two parts do not exist as products:** a single-use microneedle ECG patch, and wired earbuds with in-ear pulse sensing plus an inward-facing microphone.
- **Forging a sensor's signal.** ECG replayed into a band's electrodes worked 81% of the time on the Nymi [20]. Whether muscle signals can be injected into a 16-channel band is untested. Sensor firmware must be signed, and the hub should probe electrodes with random challenges.
- **Stolen gear.** An attacker wearing the owner's devices passes the heartbeat check with their own heart. Identity then rests on the ear, face and fingerprint checks.
- **Daily burden.** The patch is replaced every 1–2 weeks, and today's raw-data wristbands last 4–6 hours per charge [9].
- **Coercion.** All four checks pass for a coerced owner. The duress finger, time delays and second approvers handle that; see the full report, section 9.

## 7. Sources

1. [FDA De Novo decision summary DEN240080, Biolinq Shine ("cannot be re-applied if it falls off")](https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240080.pdf). *Regulatory document.*
2. ["Antifouling all-polymeric microneedle array for long-term wearable ECG" (Advanced Science, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12866678/). *Peer-reviewed; 3 subjects.*
3. [Texas Instruments ADS1292 datasheet, lead-off detection](https://www.ti.com/document-viewer/ADS1292/datasheet/lead-off-sbas4593942). *Vendor datasheet.*
4. [Movesense FAQ (ECG sampling rates)](https://www.movesense.com/faq/). *Vendor documentation.*
5. [Engadget, "SMS Audio BioSport headphones with Intel heart-rate sensing" (2014)](https://www.engadget.com/2014-08-14-sms-audio-biosport-headphones-intel.html). *News coverage.*
6. ["Who's Wearing? Ear Canal Biometric Key Extraction" (EarID, arXiv 2510.02563, 2025)](https://arxiv.org/abs/2510.02563). *Preprint.*
7. [Senstream Researcher Ring, sensor documentation](https://docs.senstream.com/senstream-researcher-ring-application-user-guide/senstream-research-ring/ring-sensors). *Vendor documentation.*
8. [Kaifosh et al., "A generic non-invasive neuromotor interface for human-computer interaction" (Nature, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12443603/). *Peer-reviewed.*
9. [MindRove armband product page](https://mindrove.com/armband/). *Vendor page.*
10. [Wooting 80HE product page](https://wooting.io/wooting-80he). *Vendor page; figures are vendor claims.*
11. [Apple Platform Security, "Magic Keyboard with Touch ID"](https://support.apple.com/guide/security/magic-keyboard-with-touch-id-secf60513daa/web). *Vendor documentation.*
12. [Microsoft Learn, "Windows Hello Enhanced Sign-in Security"](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/windows-hello-enhanced-sign-in-security). *Vendor documentation.*
13. [Gazzari et al., "My(o) Armband Leaks Passwords" (IMWUT, 2021)](https://ar5iv.labs.arxiv.org/html/2112.02382). *Peer-reviewed; cites Dennerlein et al. 1998 for keystroke EMG timing.*
14. [Huhta et al., "Pitfalls in Designing Zero-Effort Deauthentication" (NDSS 2016)](https://arxiv.org/abs/1505.05779). *Peer-reviewed.*
15. [Obata et al., pulse arrival time at ear, finger and toe (Frontiers in Physiology, 2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5292563). *Peer-reviewed; 11 subjects.*
16. [Zheng, Allen and Murray, ear and finger pulse timing (Computers in Cardiology, 2006)](https://www.cinc.org/old/Proceedings/2006/pdf/0289.pdf). *Peer-reviewed.*
17. [Sivakumar et al., "emg2qwerty" (NeurIPS 2024)](https://arxiv.org/html/2410.20081v1). *Peer-reviewed; 108 users.*
18. [Mare et al., "ZEBRA: Zero-Effort Bilateral Recurring Authentication" (IEEE S&P 2014)](https://www.ieee-security.org/TC/SP2014/papers/ZEBRA_c_Zero-EffortBilateralRecurringAuthentication.pdf). *Peer-reviewed.*
19. [Pradhan, He and Jiang, GRABMyo multi-day EMG dataset (Scientific Data, 2022)](https://www.arxiv.org/pdf/2201.01051v2). *Peer-reviewed; 43 subjects.*
20. [Eberz et al., "Broken Hearted: How To Attack ECG Biometrics" (NDSS 2017)](https://www.ndss-symposium.org/ndss2017/ndss-2017-programme/broken-hearted-how-attack-ecg-biometrics/). *Peer-reviewed.*
21. [Finnegan et al., pulse arrival time and blood pressure (Scientific Reports, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8611024/). *Peer-reviewed; 27 subjects.*
22. [Shaffer and Ginsberg, "An Overview of Heart Rate Variability Metrics and Norms" (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/). *Peer-reviewed review.*
23. [Seibold et al., "High-quality deepfakes have a heart!" (Frontiers in Imaging, 2025)](https://www.frontiersin.org/journals/imaging/articles/10.3389/fimag.2025.1504551/full). *Peer-reviewed.*
24. [Mittal, Hegde and Memon, "GOTCHA" (EuroS&P 2024)](https://arxiv.org/html/2210.06186v4). *Peer-reviewed.*
25. [Webcam rPPG timing study (Behavior Research Methods, 2026)](https://link.springer.com/article/10.3758/s13428-026-02953-x). *Peer-reviewed; figures from a search summary.*
26. [Chen et al., "FaceHeart" (INFOCOM 2017)](https://www.eecis.udel.edu/~ruizhang/paper/Chen-INFOCOM17.pdf). *Peer-reviewed; 18 users.*
27. [Kumar et al., "DistancePPG" (arXiv 1502.08040)](https://arxiv.org/pdf/1502.08040). *Peer-reviewed (preprint version).*
28. [Chen, Liao and Wu, "PulseEdit" (IEEE TIFS, 2022)](https://par.nsf.gov/servlets/purl/10358190). *Peer-reviewed.*
29. [NCC Group, "BLE proximity authentication vulnerable to relay attacks" (2022)](https://www.nccgroup.com/research/technical-advisory-ble-proximity-authentication-vulnerable-to-relay-attacks/). *Security research advisory.*
30. [Alecci et al., "What the Heart Can(not) Tell" (Sensors, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12736706/). *Peer-reviewed; 44 subjects over 13 weeks.*
31. [Apple Platform Security, "Automatically unlock Apple devices"](https://support.apple.com/guide/security/automatically-unlock-apple-devices-sec6ab47ebfc/web). *Vendor documentation.*
32. [BioSpace / Thermo Fisher, FBI approval of Rapid DNA for booking stations](https://www.biospace.com/fbi-approves-thermo-fisher-scientific-s-rapid-dna-solution-for-use-in-law-enforcement-booking-stations). *Vendor release.*
33. [Metabotype conservation and individual identification in the KORA cohort (Metabolomics, 2014)](https://link.springer.com/doi/10.1007/s11306-014-0629-y). *Peer-reviewed.*
34. [UNH Today, touch-DNA transfer study (2024)](https://www.unh.edu/unhtoday/news/release/2024/03/14/new-simpler-and-cost-effective-forensics-test-helps-identify-touch-dna). *University release on research.*
35. [The Record, "Windows Hello bypassed using infrared image" (CyberArk, CVE-2021-34466)](https://therecord.media/windows-hello-bypassed-using-infrared-image/). *News coverage of security research.*
36. [Kusche et al., in-ear ECG and PPG measurement system (arXiv 2008.02055, 2020)](https://arxiv.org/abs/2008.02055). *Research prototype.*
37. [Lee, Kuo, Jindrich and Dennerlein, keyswitch design and finger muscle activity (J Electromyogr Kinesiol, 2009)](https://stacks.cdc.gov/view/cdc/187670). *Peer-reviewed; 6 subjects.*
