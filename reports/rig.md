# Six pieces, five checks, all required

Every few seconds, Vault proves that the owner's own body is producing what the computer receives, and that every agent action traces back to it. **Earbuds** carry the voice and the ear. **Muscle-sensing wristbands and a signed keyboard** carry the hands. **An IR camera** carries the face. **The hub** ties them together and holds the keys. **A master agent and a checking gateway** carry every command down to the tools. All five checks must hold, in daylight or in the dark. Vault makes its own hardware: the earbuds, the wristbands, the keyboard, the camera module and the hub. Off-the-shelf products serve only as references and early prototypes.

*Numbers are lab values from the cited studies, and every threshold has to be calibrated per owner. Nothing here has been tested end to end. "Proposal" marks design choices made for Vault rather than measured results.*

## 1. The rig: six pieces, all made by Vault

| Piece | Where | What it does | Reference parts and prototypes |
|---|---|---|---|
| Wired earbuds | Both ears | Ear-canal echo says *who*; a skull-vibration sensor and inner mic prove *your* voice for dictation; an in-ear sensor detects removal; a faint coded signal goes out through your skin to the wristbands | OpenEarable 2.0, an open research earbud, has the bone sensor and inner mics [1]; ear-canal ID reached 98.7% in research [2]; body-signal chips exist (Ixana Wi-R, vendor-claimed 5 Mb/s) [3] |
| Wristbands (sEMG) | Both wrists | Muscle signals that fire before every keystroke and show which hand and finger moved; a soft identity signal; skin contact for custody; they receive the earbuds' body code | Built to Meta's research spec: 16 channels at 2 kHz, dry electrodes [4]. Meta's own Neural Band lasts about 18 hours [5] but gives developers only gesture events [6]. Early prototypes can use MindRove: 8 channels at 500 Hz, $679–729 [7] |
| Vault keyboard | Desk | Signs every key event with its own timestamp; electrode keycaps that hear the earbuds' body code on every press; a fingerprint key for identity, confirmations and a duress finger | Analog Hall-effect switches like the Wooting 80HE's [8]; a fingerprint key paired the way Apple's Touch ID keyboard pairs [9]; touch electrodes as in the DiamondTouch table [10] |
| Face camera | On the monitor | Infrared face on a signed path that software cannot feed. Its own infrared light works in the dark | A camera module that signs its frames, the protection Windows Enhanced Sign-in Security gives built-in cameras [11] |
| Vault hub | Desk, cabled to the computer | Runs the checks, keeps one clock, holds the keys, shows and reads confirmations, keeps the trace log | A secure element with a small screen and speaker, built like a hardware wallet |
| Master agent and gateway | Software, keys held in the hub | Turns verified commands into signed roots and checks every agent action | Vault software on open building blocks: narrowing tokens [12], injection-resistant planning [13]; see [the command chain](agents.html) |

The earbuds, keyboard and camera are cabled to the hub, because Bluetooth relays survive encryption and add only about 8 ms [14]. The wristbands pair with per-device keys and sign their own timestamps. The earbuds' cable also closes the body-signal loop through a shared ground. The bands pick the code up at the wrist all the time, and the keycaps pick it up on every press. That proves the earbuds, the wrists and each pressing finger belong to one body. It is the DiamondTouch table's design in reverse: in 2001 that table sent a signal through each user to a receiver in their chair, so it knew who touched where [10].

## 2. Five checks, all required

Five checks run at once, and every piece feeds at least two of them, so faking or stealing one piece breaks another check.

| Check | Question | How | Stops | Does not stop |
|---|---|---|---|---|
| Same voice | Did the wearer's own throat produce this speech? | Each voiced 20–40 ms piece the earbud mic hears must also show up as skull vibration in the same earbud | Loudspeakers, AI voice clones, injected audio | The owner speaking under coercion |
| Same hands | Did the owner's own fingers press these keys? | Each signed key-down pairs with exactly one muscle burst from the right hand and a plausible finger, starting 80–200 ms before it, and its keycap heard the body code; every burst must have a key | AI agents, malware, injected USB devices, another person typing, a key pushed mechanically | A forged band signal; someone touching the owner while pressing a key |
| Same person | Is this the owner? | Ear canal in speech pauses, IR face, fingerprint key, and the owner's own muscle pattern | Another person wearing the gear | A coerced owner |
| Custody | Has anything changed since the owner last proved who they are? | Earbuds in, bands on the skin, the earbuds' body code reaching both wrists, one person in view | Gear handed over mid-session; earbuds and bands split between two people | Someone touching the owner, since the body code passes through touch |
| Same chain | Does every agent action trace to a verified command? | Hub-signed roots, tokens that only narrow, a gateway that checks every call | Prompt-injected or rogue agents acting on their own | A verified command that was itself a mistake |

Each attack fails a different check. A voice clone fails *same voice*. An agent, a malicious USB cable or a robot pressing keys fails *same hands*. Stolen gear fails *same person*. A swap mid-session fails *custody*. An agent tricked by a web page fails *same chain*. Only a coerced owner passes all five, which is why the fingerprint key also takes a duress finger.

## 3. Dictation: the same-voice check

AirPods already ship a "speech-detecting accelerometer" [15]. Apple's patent describes it as an in-canal sensor sampled at 2–6 kHz, used for noise suppression and closed to developers [16]. Research turns the same signal into a security check. VAuth accepted 97% of genuine commands with 0.09% false positives across 18 users, and airborne sound could fool it only from within about 30 cm at 90 dB [17]. AirBone reached a 1.1% equal error rate for liveness and 4.0–4.5% against replay and impersonation, with 31 users [18].

The check runs on the earbud itself (proposal). The skull sensor and inner mic share the earbud's clock and are signed by it. The physical lag between the two paths is under 1 ms, since the skull carries sound across the head in about 0.4 ms [19]. Every 20–40 ms of voiced speech must line up within ±5 ms, and only matching audio reaches transcription. Words get ±50 ms of slack, because even the best aligner places only about 73% of word boundaries within 25 ms [20]. Dictated commands become signed roots only from this verified audio.

Three limits remain:
- **What vs when.** The skull signal proves *when* you spoke with high confidence, but *what* you said only roughly. The best ear-worn systems recognize about 95% of words from a 100-word vocabulary [21]. Unvoiced sounds such as *s*, *f* and *t* barely reach the skull sensor [16].
- **Sensor forging.** Loud sound at a sensor's resonant frequency biased 75% of 20 tested accelerometer models [22]. The earbud must sign its data and filter out-of-band vibration.
- **Untested attacks.** No one has tested modern AI voice clones against this check, or speech injected while the owner is talking [17]. Jaw movement also changes the ear canal's shape, so ear-canal ID runs in speech pauses [21].

## 4. Typing: wristbands and keycaps

Forearm muscles fire about 150 ms before a key bottoms out and stop about 50 ms after it, and the finger starts moving about 83 ms before [23]. A detector can place a keystroke from wrist signals to within about 21 ms, and finds 94% of keystrokes within ±50 ms [23]. Vault pairs every signed key-down with exactly one burst that starts 80–200 ms before it, from the right hand and a plausible finger. Every burst must also have a key. Pairing both ways closes the hole that broke the earlier ZEBRA wristband scheme, where the attacker's own typing decided when comparisons ran [24, 25].

Single keys are too noisy to judge. At 4.4 keys a second the bursts overlap, and even a decoder trained on its owner misreads 7–11% of characters [26]. So Vault decides over windows of 20–50 keys, about 5–12 seconds (proposal). That catches injected input within seconds. It cannot catch one swapped key typed by the same finger. Key travel and switch type shift the timing by 20–40 ms, so the template is calibrated per owner and per keyboard [27]. The bands also identify their wearer: wrist muscle patterns told people apart at about a 2.5% equal error rate across days, in a 43-person lab study [28]. Muscles work the same in the dark.

Meta's research band is the model to build to: 16 channels at 2 kHz with very low noise, decoding handwriting at about 21 words a minute [4]. Its consumer Neural Band runs about 18 hours per charge [5] but exposes only gesture events [6]. So Vault builds its own band to that spec, with signed firmware and its own timestamps. Today's raw-signal bands are a step down: MindRove has 8 channels at 500 Hz, costs $679–729, and lasts 4–6 hours per charge [7].

The **keycaps** add proof for each individual key. The earbuds send a faint coded signal at roughly 100 kHz–1 MHz that spreads over the skin [29]. The current is a few microamps, about 2,000 times below the contact current where pain begins [30, 31]. The bands hear the code constantly at the wrist. Each keycap carries an electrode that hears it during the press, so a key pushed by a mechanical plunger or by someone else's finger arrives without it. A keystroke lasts only about 100–150 ms, and earlier security prototypes at 0.5–1 kb/s needed touches over 300 ms to deliver a full 128-bit code [32]. So Vault's link must run at 10–100 kb/s or more, which body-network chips advertise [3]. The signal mostly stays on the body: an Oxford prototype told the body channel from fakes 99.3% of the time [33].

Two limits remain. Coupling starts about a centimetre before contact, so the code proves that *a finger of the owner's body* pressed the key, not which finger; the bands supply which finger. And anyone touching the owner carries the code too, while a live relay through a second person can be caught only by time or distance bounds, not by the code itself [34], so the face camera also requires exactly one person in view (proposal).

## 5. Commands and agents

Everything the verified owner says or types becomes a hub-signed command. A master agent plans only from those commands. It reads web pages, email and files through a quarantined reader that has no tools, and it hands sub-agents tokens that can only narrow [12, 13]. A gateway outside any AI model checks every action against its chain. It asks the owner when an action is consequential or was shaped by untrusted data, and it logs everything, including refusals. The full design is on [the command chain page](agents.html).

## 6. If a piece is missing

Missing data lets trust fade for a few seconds. Contradicting data locks at once: a different face, a key with no muscle burst or body code, speech with no skull vibration (proposal).

| Piece off or failing | What goes blind | What Vault does (proposal) |
|---|---|---|
| Earbuds out | Voice, ear identity, body code | Typing and dictation stop reaching the computer at once. When the earbuds go back in, the fingerprint key and face re-anchor |
| A wristband off | Same hands for that hand, body code | That hand's keys stop reaching the computer at once. When it goes back on, the fingerprint key re-anchors |
| A key arrives without the body code | Same hands | Treated as a contradiction: the key is dropped and vault actions lock until the owner re-anchors |
| Wristband battery low | Nothing yet | Warns ahead of time. A second pair swaps in during a fingerprint touch |
| Face out of view | Face identity | Nothing for short gaps, while the ear check carries identity. Vault actions wait for the face |
| A second person in view | Custody | Vault actions pause until the owner confirms with the fingerprint key |
| Unknown keyboard or USB device | Signed input | Its input is blocked |
| Hub unplugged | Everything | Keys expire within seconds; the computer locks |

## 7. The options, scored

| Option | Verdict | Why |
|---|---|---|
| Wired earbuds | **Must-have** | Voice binding for dictation, all-day ear identity, and the source of the body code. The cable rules out radio relay |
| sEMG wristbands, both wrists | **Must-have** | The only signal that ties each keystroke to muscles, in any light [23]. Also a soft identity signal and the receiver for the body code |
| Vault keyboard: signed keys, electrode keycaps, fingerprint key | **Must-have** | Every key event signed at the switch and tied to a finger of the owner's body. Identity on demand, the confirm button and a duress finger |
| IR face camera on an attested path | **Must-have** | The owner's face whenever they face the screen, day or night, over a path software cannot feed [11] |
| Master agent and gateway | **Must-have** | Every agent action traced to a verified command |
| Hands camera | **Optional** | Infrared, so darkness is no problem [35]. But keys sit under 1 cm apart, and one tracker missed 7–10% of keystrokes [36]. A cross-check, not a requirement |
| Chest or microneedle patch | **Optional** | A single-use custody seal for the highest-stakes sessions [37] |
| Heartbeat timing check | **In reserve** | Needed only if Vault must accept ordinary webcams; see section 8 |
| Ring, watch, Apple Watch ranging | **Drop** | Wrist pulse fails as identity in real use [38]. Watch ranging proves a token is near, not who is typing [39] |
| Nymi-style ECG band | **Drop** | Replayed ECG fooled it 81% of the time [40] |
| RGB webcam face | **Demote** | Never identity, because virtual cameras and injected frames can feed it [41, 42] |
| DNA or metabolome | **Drop** | Rapid DNA takes about 90 minutes [43]; metabolic profiles re-identify only about 40% of people after 7 years [44] |

## 8. In reserve: heartbeat timing and a hands camera

**Heartbeat timing.** After each heartbeat, the pulse reaches the ear about 120–200 ms later and the finger about 200–270 ms later [45, 46]. Successive beats differ by about 42 ms, so a forger can't predict them [47]. A live deepfake's face pulse comes from the attacker and arrives late, because rendering adds at least ~43 ms per frame [41, 48]. With a camera that signs its frames, this check is redundant.

**Hands camera.** A downward infrared tracker can confirm that a finger landed on each reported key. Headset cameras detected touches at an F1 score of 0.99 and named the finger at 0.96 [49]. It is worth adding as a cross-check if the bands misfire in testing, but it cannot replace them.

## 9. What is not proven yet

- **None of the core checks has been measured.** That covers skull-versus-mic matching against modern voice clones, per-key pairing of muscle bursts with signed key events, and a body code carried from the ear to the wrists and keycaps. No one has published muscle-to-keystroke pairing as a security check, and every number above comes from a separate lab study.
- **Vault makes all of the hardware.** None of these exists as a product: wired earbuds with a skull sensor, inner mic and body-signal transmitter; a wristband with Meta-class signal quality, raw access, signed firmware and all-day battery; a keyboard with signed analog keys, electrode keycaps and a fingerprint key; a camera module that signs its frames; and the hub.
- **Forging the band's signal.** ECG replayed into a band's electrodes worked 81% of the time on the Nymi [40]. Whether muscle signals can be injected into a 16-channel band is untested. The band stream is also a keylogger, so raw signals never leave the hub.
- **Touch passes the body code.** A second person touching the owner carries it to the keycaps too, and a live relay needs time or distance bounds to catch it. The one-person rule carries that risk.
- **Daily wear.** Earbuds plus two bands. Meta's band shows about 18 hours per charge is possible [5]. No study of consumer earbuds worn for 8+ hours was found.
- **Coercion.** All five checks pass for a coerced owner. The duress finger, delays and second approvers handle that; see the [full report](report.html).
- **The agent chain's open problems.** No planner design has been tested against adaptive attackers, and turning speech into permissions is itself a trust boundary; see [the command chain](agents.html).

## 10. Sources

1. [OpenEarable 2.0: open-source earphone platform (University of Bath research portal)](https://researchportal.bath.ac.uk/en/publications/openearable-20-open-source-earphone-platform-for-physiological-ea/). *Research platform.*
2. ["Who's Wearing? Ear Canal Biometric Key Extraction" (EarID, arXiv 2510.02563, 2025)](https://arxiv.org/abs/2510.02563). *Preprint.*
3. [Ixana, Wi-R body-area network technology](https://www.ixana.ai/technology/wi-r-ban). *Vendor page; figures are vendor claims.*
4. [Kaifosh et al., "A generic non-invasive neuromotor interface for human-computer interaction" (Nature, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12443603/). *Peer-reviewed.*
5. [Android Authority, Meta Ray-Ban Display and Neural Band](https://www.androidauthority.com/meta-ray-ban-display-3598809/). *Trade press (vendor figures).*
6. [VR.org, Meta Ray-Ban Display developer SDK (2026)](https://vr.org/articles/meta-ray-ban-display-developer-sdk-2026). *Trade press; Meta's own developer documentation not retrieved.*
7. [MindRove armband product page](https://mindrove.com/armband/). *Vendor page.*
8. [Wooting 80HE product page](https://wooting.io/wooting-80he). *Vendor page; figures are vendor claims.*
9. [Apple Platform Security, "Magic Keyboard with Touch ID"](https://support.apple.com/guide/security/magic-keyboard-with-touch-id-secf60513daa/web). *Vendor documentation.*
10. [Dietz and Leigh, "DiamondTouch: A Multi-User Touch Technology" (UIST 2001)](https://resenv.media.mit.edu/classarchive/MAS965/readings/DiamondTouch.pdf). *Peer-reviewed.*
11. [Microsoft Learn, "Windows Hello Enhanced Sign-in Security"](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/windows-hello-enhanced-sign-in-security). *Vendor documentation.*
12. [Niyikiza, "Attenuating Authorization Tokens for Agentic Delegation Chains" (IETF individual draft, June 2026)](https://www.ietf.org/archive/id/draft-niyikiza-oauth-attenuating-agent-tokens-01.html). *IETF individual draft.*
13. [Debenedetti et al., "Defeating Prompt Injections by Design" (CaMeL, 2025)](https://arxiv.org/html/2503.18813v2). *Research paper.*
14. [NCC Group, "BLE proximity authentication vulnerable to relay attacks" (2022)](https://www.nccgroup.com/research/technical-advisory-ble-proximity-authentication-vulnerable-to-relay-attacks/). *Security research advisory.*
15. [Apple, AirPods comparison ("speech-detecting accelerometer")](https://apple.com/uk/airpods/compare). *Vendor page.*
16. [Apple patent US9313572, accelerometer-based voice activity detection in earbuds](https://patents.google.com/patent/US9313572). *Patent.*
17. [Feng, Fawaz and Shin, "Continuous Authentication for Voice Assistants" (VAuth, MobiCom 2017)](https://ar5iv.labs.arxiv.org/html/1701.04507). *Peer-reviewed; 18 users.*
18. [AirBone: air- and bone-conducted speech for liveness and authentication (arXiv 2309.15203)](https://ar5iv.arxiv.org/html/2309.15203). *Research paper; 31 users.*
19. [Bone-conduction wave propagation in the human skull (Hearing Research, 2017)](https://pubmed.ncbi.nlm.nih.gov/28964568/). *Peer-reviewed.*
20. [Rousso et al., word-level forced-alignment accuracy (arXiv 2406.19363)](https://arxiv.org/pdf/2406.19363). *Research paper.*
21. [Earable authentication and sensing survey (arXiv 2506.05720, 2025)](https://arxiv.org/pdf/2506.05720). *Survey; secondary for individual system figures.*
22. [University of Michigan, "Sonic cyber attacks show security holes in ubiquitous sensors" (WALNUT, EuroS&P 2017)](https://micl.engin.umich.edu/stories/sonic-cyber-attacks-show-security-holes-in-ubiquitous-sensors). *University summary of peer-reviewed research.*
23. [Gazzari et al., "My(o) Armband Leaks Passwords" (IMWUT, 2021)](https://ar5iv.labs.arxiv.org/html/2112.02382). *Peer-reviewed; cites Dennerlein et al. 1998 for keystroke EMG timing.*
24. [Huhta et al., "Pitfalls in Designing Zero-Effort Deauthentication" (NDSS 2016)](https://arxiv.org/abs/1505.05779). *Peer-reviewed.*
25. [Mare et al., "ZEBRA: Zero-Effort Bilateral Recurring Authentication" (IEEE S&P 2014)](https://www.ieee-security.org/TC/SP2014/papers/ZEBRA_c_Zero-EffortBilateralRecurringAuthentication.pdf). *Peer-reviewed.*
26. [Sivakumar et al., "emg2qwerty" (NeurIPS 2024)](https://arxiv.org/html/2410.20081v1). *Peer-reviewed; 108 users.*
27. [Lee, Kuo, Jindrich and Dennerlein, keyswitch design and finger muscle activity (J Electromyogr Kinesiol, 2009)](https://stacks.cdc.gov/view/cdc/187670). *Peer-reviewed; 6 subjects.*
28. [Pradhan, He and Jiang, GRABMyo multi-day EMG dataset (Scientific Data, 2022)](https://www.arxiv.org/pdf/2201.01051v2). *Peer-reviewed; 43 subjects.*
29. [Das et al., "Enabling Covert Body Area Network using Electro-Quasistatic Human Body Communication" (Scientific Reports, 2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6411898/). *Peer-reviewed.*
30. [Maity et al., safety of capacitive body-channel communication (2020)](https://par.nsf.gov/servlets/purl/10249173). *Peer-reviewed.*
31. [ICNIRP, Guidelines for limiting exposure to electromagnetic fields (2020)](https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf). *International guidelines.*
32. [BGComm: body-guided communication for touch authentication (MobiCom 2018)](https://www.winlab.rutgers.edu/~gruteser/papers/2018%20BGComm_Viet.pdf). *Peer-reviewed.*
33. [Roeschlin, Martinovic and Rasmussen, device pairing through the body (NDSS 2018)](https://www.cs.ox.ac.uk/files/9833/pairing.pdf). *Peer-reviewed.*
34. [OneTouch: body-channel touch authentication (USENIX Security 2025)](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-351-yan-yihui.pdf). *Peer-reviewed.*
35. [Ultraleap Leap Motion Controller 2 datasheet](https://www.ultraleap.com/datasheets/leap-motion-controller-2-datasheet_issue13.pdf). *Vendor datasheet.*
36. [Yang et al., keystroke inference from video (USENIX Security 2023)](https://www.usenix.org/system/files/usenixsecurity23-yang-zhuolin.pdf). *Peer-reviewed; 16-user study.*
37. [FDA De Novo decision summary DEN240080, Biolinq Shine ("cannot be re-applied if it falls off")](https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240080.pdf). *Regulatory document.*
38. [Alecci et al., "What the Heart Can(not) Tell" (Sensors, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12736706/). *Peer-reviewed; 44 subjects over 13 weeks.*
39. [Apple Platform Security, "Automatically unlock Apple devices"](https://support.apple.com/guide/security/automatically-unlock-apple-devices-sec6ab47ebfc/web). *Vendor documentation.*
40. [Eberz et al., "Broken Hearted: How To Attack ECG Biometrics" (NDSS 2017)](https://www.ndss-symposium.org/ndss2017/ndss-2017-programme/broken-hearted-how-attack-ecg-biometrics/). *Peer-reviewed.*
41. [Seibold et al., "High-quality deepfakes have a heart!" (Frontiers in Imaging, 2025)](https://www.frontiersin.org/journals/imaging/articles/10.3389/fimag.2025.1504551/full). *Peer-reviewed.*
42. [The Record, "Windows Hello bypassed using infrared image" (CyberArk, CVE-2021-34466)](https://therecord.media/windows-hello-bypassed-using-infrared-image/). *News coverage of security research.*
43. [BioSpace / Thermo Fisher, FBI approval of Rapid DNA for booking stations](https://www.biospace.com/fbi-approves-thermo-fisher-scientific-s-rapid-dna-solution-for-use-in-law-enforcement-booking-stations). *Vendor release.*
44. [Metabotype conservation and individual identification in the KORA cohort (Metabolomics, 2014)](https://link.springer.com/doi/10.1007/s11306-014-0629-y). *Peer-reviewed.*
45. [Obata et al., pulse arrival time at ear, finger and toe (Frontiers in Physiology, 2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5292563). *Peer-reviewed; 11 subjects.*
46. [Zheng, Allen and Murray, ear and finger pulse timing (Computers in Cardiology, 2006)](https://www.cinc.org/old/Proceedings/2006/pdf/0289.pdf). *Peer-reviewed.*
47. [Shaffer and Ginsberg, "An Overview of Heart Rate Variability Metrics and Norms" (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/). *Peer-reviewed review.*
48. [Mittal, Hegde and Memon, "GOTCHA" (EuroS&P 2024)](https://arxiv.org/html/2210.06186v4). *Peer-reviewed.*
49. [TouchInsight: touch detection from headset cameras (UIST 2024, arXiv 2410.05940)](https://arxiv.org/abs/2410.05940). *Peer-reviewed.*
