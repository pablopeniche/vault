# Six pieces, five checks, nothing on the wrists

Every few seconds, Vault proves that the owner's own body is producing what the computer receives, and that every agent action traces back to it. **Earbuds** carry the voice and the ear. **A signed keyboard, a hands tracker and a faint signal sent through the body** carry the hands. **An IR camera** carries the face. **The hub** ties them together and holds the keys. **A master agent and a checking gateway** carry every command down to the tools. All five checks must hold. Two parts have to be built, the sensing earbuds and the body-sensing keycaps; the rest exists as products or developer kits.

*Numbers are lab values from the cited studies, and every threshold has to be calibrated per owner. Nothing here has been tested end to end. "Proposal" marks design choices made for Vault rather than measured results.*

## 1. The rig: six pieces, one job each

| Piece | Where | What it does | Build it today with |
|---|---|---|---|
| Wired earbuds | Both ears | Ear-canal echo says *who*; a skull-vibration sensor and inner mic prove *your* voice for dictation; an in-ear sensor detects removal; a faint coded signal goes out through your skin to the keys | Custom. OpenEarable 2.0 has the bone sensor and inner mics [1]; ear-canal ID reached 98.7% in research [2]; body-signal chips exist (Ixana Wi-R, vendor-claimed 5 Mb/s) [3] |
| Signed keyboard | Desk | Signs every key event with its own timestamp; a fingerprint key for identity, confirmations and a duress finger; keycaps or palm rest that receive the body signal | Wooting 80HE analog keyboard, $199.99 [4], plus a fingerprint key paired the way Apple's Touch ID keyboard pairs [5]; the body-signal receiver is custom |
| Hands tracker | Above the keyboard, looking down | Infrared camera at 120 fps that sees which finger lands on which key | Ultraleap Leap Motion Controller 2: 120 fps, 850 nm infrared [6], with a supported screen-top mount [7] |
| Face camera | On the monitor | Infrared face on a signed path that software cannot feed | Integrated IR camera, as in Windows Enhanced Sign-in Security [8], with signed frames |
| Vault hub | Desk, cabled to the computer | Runs the checks, keeps one clock, holds the keys, shows and reads confirmations, keeps the trace log | Custom: a secure element with a small screen and speaker |
| Master agent and gateway | Software, keys held in the hub | Turns verified commands into signed roots and checks every agent action | Open building blocks: narrowing tokens [9], injection-resistant planning [10]; see [the command chain](agents.html) |

Everything is cabled to the hub, because Bluetooth relays survive encryption and add only about 8 ms [11]. The earbuds' cable also closes the body-signal loop through a shared ground. That is the DiamondTouch table's design in reverse: in 2001 it sent a signal through each user to a receiver in their chair, so it knew who touched where [12].

## 2. Five checks, all required

Five checks run at once, and every piece feeds at least two of them, so faking or stealing one piece breaks another check.

| Check | Question | How | Stops | Does not stop |
|---|---|---|---|---|
| Same voice | Did the wearer's own throat produce this speech? | Each voiced 20–40 ms piece the earbud mic hears must also show up as skull vibration in the same earbud | Loudspeakers, AI voice clones, injected audio | The owner speaking under coercion |
| Same hands | Did hands attached to the earbud wearer press these keys? | Each signed key-down must match a fingertip landing on that key and arrive carrying the earbuds' body code | AI agents, malware, injected USB devices, another person typing | Someone touching the owner while typing, since the code passes through touch |
| Same person | Is this the owner? | Ear canal in speech pauses, IR face, fingerprint key | Another person wearing the earbuds | A coerced owner |
| Custody | Has anything changed since the owner last proved who they are? | Earbuds in, body code unbroken, one person in view, one pair of hands | Gear handed over mid-session; a second person joining | — |
| Same chain | Does every agent action trace to a verified command? | Hub-signed roots, tokens that only narrow, a gateway that checks every call | Prompt-injected or rogue agents acting on their own | A verified command that was itself a mistake |

Each attack fails a different check. A voice clone fails *same voice*. An agent or a malicious USB cable fails *same hands*. Stolen earbuds fail *same person*. A swap mid-session fails *custody*. An agent tricked by a web page fails *same chain*. Only a coerced owner passes all five, which is why the fingerprint key also takes a duress finger.

## 3. Dictation: the same-voice check

AirPods already ship a "speech-detecting accelerometer" [13]. Apple's patent describes it as an in-canal sensor sampled at 2–6 kHz, used for noise suppression and closed to developers [14]. Research turns the same signal into a security check. VAuth accepted 97% of genuine commands with 0.09% false positives across 18 users. Airborne sound could fool it only from within about 30 cm at 90 dB [15]. AirBone reached a 1.1% equal error rate for liveness and 4.0–4.5% against replay and impersonation, with 31 users [16].

The check runs on the earbud itself (proposal). The skull sensor and inner mic share the earbud's clock and are signed by it. The physical lag between the two paths is under 1 ms, since the skull carries sound across the head in about 0.4 ms [17]. Every 20–40 ms of voiced speech must line up within ±5 ms, and only matching audio reaches transcription. Words get ±50 ms of slack, because even the best aligner places only about 73% of word boundaries within 25 ms [18]. Dictated commands become signed roots only from this verified audio.

Three limits remain:
- **What vs when.** The skull signal proves *when* you spoke with high confidence, but *what* you said only roughly. The best ear-worn systems recognize about 95% of words from a 100-word vocabulary [19]. Unvoiced sounds such as *s*, *f* and *t* barely reach the skull sensor [14].
- **Sensor forging.** Loud sound at a sensor's resonant frequency biased 75% of 20 tested accelerometer models [20]. The earbud must sign its data and filter out-of-band vibration.
- **Untested attacks.** No one has tested modern AI voice clones against this check, or speech injected while the owner is talking [15]. Jaw movement also changes the ear canal's shape, so ear-canal ID runs in speech pauses [19].

## 4. Typing without wristbands: the same-hands check

Two signals replace the wristbands. The **hands tracker** watches your fingers from above. Vault doesn't need it to read what you type, because the keyboard already reports the key. It only asks yes or no: did a fingertip land on that key at that moment? Cameras already do the harder job well. Headset cameras detected touches at an F1 score of 0.99 and named the finger at 0.96, within 6.3 mm [21]. Phone video recovered typed text at a 0.3–1.1% character error rate from 0.8–3 m [22]. The weak spot is off-the-shelf fingertip tracking. Keys sit less than 1 cm apart, and one general-purpose tracker missed 7–10% of keystrokes [22]. So Vault judges windows of keys, not single keys (proposal).

The **body code** ties those hands to the earbuds. The earbuds send a faint coded signal at roughly 100 kHz–1 MHz, which spreads over the skin and is received by the keycaps or palm rest on every touch [23]. The current is a few microamps, about 2,000 times below the contact current where pain begins [24, 25]. Earlier security prototypes ran at 0.5–1 kb/s and needed touches over 300 ms to deliver a full 128-bit code [26]. Vault needs at least 10–100 kb/s, which body-network chips advertise [3]. The signal mostly stays on the body: an Oxford prototype told the body channel from fakes 99.3% of the time [27].

The honest limit is that the code proves the key was pressed by a body *in contact with* the earbud wearer, not by the wearer specifically. Anyone holding the owner's hand carries it too, and a live relay through a second person cannot be stopped by timing [28]. That's why the hands tracker also requires exactly one pair of hands, and the face camera exactly one person (proposal). Mimicking the owner's typing near a wrist-sensor check kept 40–45% of attackers logged in [29], which is why the hub, not the attacker's input, decides when comparisons run.

## 5. Commands and agents

Everything the verified owner says or types becomes a hub-signed command. A master agent plans only from those commands. It reads web pages, email and files through a quarantined reader that has no tools, and it hands sub-agents tokens that can only narrow [9, 10]. A gateway outside any AI model checks every action against its chain. It asks the owner when an action is consequential or was shaped by untrusted data, and logs everything, including refusals. The full design is on [the command chain page](agents.html).

## 6. If a piece is missing

Missing data lets trust fade for a few seconds. Contradicting data locks at once: a different face, a key with no fingertip or body code, speech with no skull vibration (proposal).

| Piece off or failing | What goes blind | What Vault does (proposal) |
|---|---|---|
| Earbuds out | Voice, ear identity, body code | Typing and dictation stop reaching the computer at once. When the earbuds go back in, the fingerprint key and face re-anchor |
| Hands tracker blocked | Same hands | Short gaps are tolerated. After a few seconds, keys stop reaching vault actions until the view is back |
| Face out of view | Face identity | Nothing for short gaps, while the ear check carries identity. Vault actions wait for the face |
| A second person in view or touching the keyboard | Custody | Vault actions pause until the owner confirms with the fingerprint key |
| Unknown keyboard or USB device | Signed input | Its input is blocked |
| Hub unplugged | Everything | Keys expire within seconds; the computer locks |

## 7. The options, scored

| Option | Verdict | Why |
|---|---|---|
| Wired earbuds | **Must-have** | Voice binding for dictation, all-day ear identity, and the carrier of the body code. The cable rules out radio relay |
| Signed keyboard with fingerprint key | **Must-have** | Every key event signed at the switch. Identity on demand, the confirm button and a duress finger |
| Hands tracker (new) | **Must-have** | Replaces the wristbands. Checks that a finger landed on each reported key |
| Body-signal keycaps (new) | **Must-have, to be proven** | Ties each key to the body wearing the earbuds |
| IR face camera on an attested path | **Must-have** | The owner's face whenever they face the screen, over a path software cannot feed [8] |
| Master agent and gateway | **Must-have** | Every agent action traced to a verified command |
| sEMG wristbands | **In reserve** | The strongest per-key evidence, since muscles fire about 150 ms before a key bottoms out [30]. Use them only if the hands tracker and body code fail testing |
| Chest or microneedle patch | **Optional** | A single-use custody seal for the highest-stakes sessions [31] |
| Heartbeat timing check | **In reserve** | Needed only if Vault must accept ordinary webcams; see section 8 |
| Ring, watch, Apple Watch ranging | **Drop** | Wrist pulse fails as identity in real use [32]. Watch ranging proves a token is near, not who is typing [33] |
| Nymi-style ECG band | **Drop** | Replayed ECG fooled it 81% of the time [34] |
| RGB webcam face | **Demote** | Never identity, because virtual cameras and injected frames can feed it [35, 36] |
| DNA or metabolome | **Drop** | Rapid DNA takes about 90 minutes [37]; metabolic profiles re-identify only about 40% of people after 7 years [38] |

## 8. In reserve: muscle and heartbeat timing

These two checks were the earlier answer to "is a human typing?" and "is that face real?". They stay in reserve.

**Muscle to keystroke.** Forearm muscles fire about 150 ms before a key bottoms out, and a detector can place a keystroke to within about 21 ms [30]. Even a decoder trained on its owner misreads 7–11% of characters, so decisions run over 20–50 keys [39]. This is the strongest evidence that a specific hand pressed a key, but it requires wristbands.

**Heartbeat timing.** After each heartbeat, the pulse reaches the ear about 120–200 ms later and the finger about 200–270 ms later [40, 41]. Successive beats differ by about 42 ms, so a forger can't predict them [42]. A live deepfake's face pulse comes from the attacker and arrives late, because rendering adds at least ~43 ms per frame [35, 43]. With a camera that signs its frames, this check is redundant.

## 9. What is not proven yet

- **None of the three new checks has been measured.** That covers skull-versus-mic matching against modern voice clones, a hands tracker matched to signed key events, and ear-to-fingertip body signalling. Every number above comes from a separate lab study.
- **Two parts do not exist as products.** Wired earbuds with a skull sensor, inner mic and body-signal transmitter, and keycaps or a palm rest that receive the signal.
- **Touch passes the body code.** A second person touching the owner carries it, and a live relay cannot be timed out. The one-person and one-pair-of-hands rules carry that risk.
- **All-day earbuds.** Sealed earbuds bring pressure, heat and the muffled sound of your own voice. No study of consumer earbuds worn for 8+ hours was found.
- **Coercion.** All five checks pass for a coerced owner. The duress finger, delays and second approvers handle that; see the [full report](report.html).
- **The agent chain's open problems.** No planner design has been tested against adaptive attackers, and turning speech into permissions is itself a trust boundary; see [the command chain](agents.html).

## 10. Sources

1. [OpenEarable 2.0: open-source earphone platform (University of Bath research portal)](https://researchportal.bath.ac.uk/en/publications/openearable-20-open-source-earphone-platform-for-physiological-ea/). *Research platform.*
2. ["Who's Wearing? Ear Canal Biometric Key Extraction" (EarID, arXiv 2510.02563, 2025)](https://arxiv.org/abs/2510.02563). *Preprint.*
3. [Ixana, Wi-R body-area network technology](https://www.ixana.ai/technology/wi-r-ban). *Vendor page; figures are vendor claims.*
4. [Wooting 80HE product page](https://wooting.io/wooting-80he). *Vendor page; figures are vendor claims.*
5. [Apple Platform Security, "Magic Keyboard with Touch ID"](https://support.apple.com/guide/security/magic-keyboard-with-touch-id-secf60513daa/web). *Vendor documentation.*
6. [Ultraleap Leap Motion Controller 2 datasheet](https://www.ultraleap.com/datasheets/leap-motion-controller-2-datasheet_issue13.pdf). *Vendor datasheet.*
7. [Ultraleap documentation, "Getting started" (mounting modes)](https://docs.ultraleap.com/hand-tracking/getting-started.html). *Vendor documentation.*
8. [Microsoft Learn, "Windows Hello Enhanced Sign-in Security"](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/windows-hello-enhanced-sign-in-security). *Vendor documentation.*
9. [Niyikiza, "Attenuating Authorization Tokens for Agentic Delegation Chains" (IETF individual draft, June 2026)](https://www.ietf.org/archive/id/draft-niyikiza-oauth-attenuating-agent-tokens-01.html). *IETF individual draft.*
10. [Debenedetti et al., "Defeating Prompt Injections by Design" (CaMeL, 2025)](https://arxiv.org/html/2503.18813v2). *Research paper.*
11. [NCC Group, "BLE proximity authentication vulnerable to relay attacks" (2022)](https://www.nccgroup.com/research/technical-advisory-ble-proximity-authentication-vulnerable-to-relay-attacks/). *Security research advisory.*
12. [Dietz and Leigh, "DiamondTouch: A Multi-User Touch Technology" (UIST 2001)](https://resenv.media.mit.edu/classarchive/MAS965/readings/DiamondTouch.pdf). *Peer-reviewed.*
13. [Apple, AirPods comparison ("speech-detecting accelerometer")](https://apple.com/uk/airpods/compare). *Vendor page.*
14. [Apple patent US9313572, accelerometer-based voice activity detection in earbuds](https://patents.google.com/patent/US9313572). *Patent.*
15. [Feng, Fawaz and Shin, "Continuous Authentication for Voice Assistants" (VAuth, MobiCom 2017)](https://ar5iv.labs.arxiv.org/html/1701.04507). *Peer-reviewed; 18 users.*
16. [AirBone: air- and bone-conducted speech for liveness and authentication (arXiv 2309.15203)](https://ar5iv.arxiv.org/html/2309.15203). *Research paper; 31 users.*
17. [Bone-conduction wave propagation in the human skull (Hearing Research, 2017)](https://pubmed.ncbi.nlm.nih.gov/28964568/). *Peer-reviewed.*
18. [Rousso et al., word-level forced-alignment accuracy (arXiv 2406.19363)](https://arxiv.org/pdf/2406.19363). *Research paper.*
19. [Earable authentication and sensing survey (arXiv 2506.05720, 2025)](https://arxiv.org/pdf/2506.05720). *Survey; secondary for individual system figures.*
20. [University of Michigan, "Sonic cyber attacks show security holes in ubiquitous sensors" (WALNUT, EuroS&P 2017)](https://micl.engin.umich.edu/stories/sonic-cyber-attacks-show-security-holes-in-ubiquitous-sensors). *University summary of peer-reviewed research.*
21. [TouchInsight: touch detection from headset cameras (UIST 2024, arXiv 2410.05940)](https://arxiv.org/abs/2410.05940). *Peer-reviewed.*
22. [Yang et al., keystroke inference from video (USENIX Security 2023)](https://www.usenix.org/system/files/usenixsecurity23-yang-zhuolin.pdf). *Peer-reviewed; 16-user study.*
23. [Das et al., "Enabling Covert Body Area Network using Electro-Quasistatic Human Body Communication" (Scientific Reports, 2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6411898/). *Peer-reviewed.*
24. [Maity et al., safety of capacitive body-channel communication (2020)](https://par.nsf.gov/servlets/purl/10249173). *Peer-reviewed.*
25. [ICNIRP, Guidelines for limiting exposure to electromagnetic fields (2020)](https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf). *International guidelines.*
26. [BGComm: body-guided communication for touch authentication (MobiCom 2018)](https://www.winlab.rutgers.edu/~gruteser/papers/2018%20BGComm_Viet.pdf). *Peer-reviewed.*
27. [Roeschlin, Martinovic and Rasmussen, device pairing through the body (NDSS 2018)](https://www.cs.ox.ac.uk/files/9833/pairing.pdf). *Peer-reviewed.*
28. [OneTouch: body-channel touch authentication (USENIX Security 2025)](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-351-yan-yihui.pdf). *Peer-reviewed.*
29. [Huhta et al., "Pitfalls in Designing Zero-Effort Deauthentication" (NDSS 2016)](https://arxiv.org/abs/1505.05779). *Peer-reviewed.*
30. [Gazzari et al., "My(o) Armband Leaks Passwords" (IMWUT, 2021)](https://ar5iv.labs.arxiv.org/html/2112.02382). *Peer-reviewed; cites Dennerlein et al. 1998 for keystroke EMG timing.*
31. [FDA De Novo decision summary DEN240080, Biolinq Shine ("cannot be re-applied if it falls off")](https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN240080.pdf). *Regulatory document.*
32. [Alecci et al., "What the Heart Can(not) Tell" (Sensors, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12736706/). *Peer-reviewed; 44 subjects over 13 weeks.*
33. [Apple Platform Security, "Automatically unlock Apple devices"](https://support.apple.com/guide/security/automatically-unlock-apple-devices-sec6ab47ebfc/web). *Vendor documentation.*
34. [Eberz et al., "Broken Hearted: How To Attack ECG Biometrics" (NDSS 2017)](https://www.ndss-symposium.org/ndss2017/ndss-2017-programme/broken-hearted-how-attack-ecg-biometrics/). *Peer-reviewed.*
35. [Seibold et al., "High-quality deepfakes have a heart!" (Frontiers in Imaging, 2025)](https://www.frontiersin.org/journals/imaging/articles/10.3389/fimag.2025.1504551/full). *Peer-reviewed.*
36. [The Record, "Windows Hello bypassed using infrared image" (CyberArk, CVE-2021-34466)](https://therecord.media/windows-hello-bypassed-using-infrared-image/). *News coverage of security research.*
37. [BioSpace / Thermo Fisher, FBI approval of Rapid DNA for booking stations](https://www.biospace.com/fbi-approves-thermo-fisher-scientific-s-rapid-dna-solution-for-use-in-law-enforcement-booking-stations). *Vendor release.*
38. [Metabotype conservation and individual identification in the KORA cohort (Metabolomics, 2014)](https://link.springer.com/doi/10.1007/s11306-014-0629-y). *Peer-reviewed.*
39. [Sivakumar et al., "emg2qwerty" (NeurIPS 2024)](https://arxiv.org/html/2410.20081v1). *Peer-reviewed; 108 users.*
40. [Obata et al., pulse arrival time at ear, finger and toe (Frontiers in Physiology, 2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5292563). *Peer-reviewed; 11 subjects.*
41. [Zheng, Allen and Murray, ear and finger pulse timing (Computers in Cardiology, 2006)](https://www.cinc.org/old/Proceedings/2006/pdf/0289.pdf). *Peer-reviewed.*
42. [Shaffer and Ginsberg, "An Overview of Heart Rate Variability Metrics and Norms" (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624990/). *Peer-reviewed review.*
43. [Mittal, Hegde and Memon, "GOTCHA" (EuroS&P 2024)](https://arxiv.org/html/2210.06186v4). *Peer-reviewed.*
