# Five devices, one hub, every signal signed

Vault makes five devices: wired earbuds, two muscle-sensing wristbands, a keyboard, a camera module and a hub. Every device carries its own secure element and clock. It timestamps every sample, signs what it sends, and pairs only with its owner's hub through mutual attestation. Raw biometric signals go only to the hub, never to the computer. The earbuds, keyboard and camera are cabled to the hub. Only the wristbands use radio, one Bluetooth link per band. The parts below are candidates checked against datasheets, not final selections. Each device has a prototype path that starts with hardware on sale today.

*Figures come from datasheets and vendor pages. Power and bandwidth numbers marked "estimate" are this spec's own arithmetic. "Proposal" marks design choices made for Vault.*

## 1. Shared rules: what every device does

| Rule | What every Vault device does |
|---|---|
| Identity | A secure element holds a device key, provisioned at the factory, with a certificate from a Vault certificate authority. Pairing is mutual attestation between device and hub, followed by an encrypted session, the way Apple's Touch ID keyboard pairs with a Mac [1]. A standard for authenticating USB devices exists, but no hub, host controller or operating system was found that supports it, so Vault runs its own [2] |
| Signing | Every data frame carries a message authentication code (MAC) under the session key, and the device signs a checkpoint every second (proposal). Signing each keystroke or audio frame individually may be too slow for a secure element; per-signature timing was not found |
| Time | Every sample is timestamped on the device. The hub disciplines all clocks to within 1 ms, because the voice check needs ±5 ms and the keystroke check ±50 ms (proposal). The hub's reference is a temperature-compensated oscillator accurate to ±0.1 ppm [3] |
| Firmware | Secure boot, signed updates, a rollback counter, and debug ports disabled after manufacturing (proposal) |
| Data | Raw audio, muscle signals and camera frames go only to the hub, encrypted. The computer receives keystrokes, transcribed text and check results, never raw streams |
| Links | Cables wherever possible, because Bluetooth relays survive encryption and add only about 8 ms [4]. The wristbands are the only radio devices |

## 2. Earbuds

| Function | Spec | Candidate parts |
|---|---|---|
| Skull-vibration sensor | 8 or 16 kHz on the same audio bus and clock as the microphones, so the voice check is sample-locked by design | ST LSM6DSV16BX: bone channel over TDM, 30 µg/√Hz noise, plus a motion sensor [5]. Second source: Bosch BMA580, up to 6.4 kHz on its own clock [6] |
| Microphones | One inner and one outer per earbud, 48 kHz | Infineon IM69D129F: 69 dB(A) SNR, 450 µA [7]. TDK T5848 for the inner mic, with 133 dB SPL overload next to the speaker [8] |
| Speaker | Normal audio, plus inaudible ear-canal probes in speech pauses for identity [9] | Balanced-armature or dynamic driver |
| In-ear detection | Contact and motion from the sensor above, plus a capacitive pad (proposal) | Built into the motion sensor; capacitive pad on the shell |
| Body-code transmitter | Electro-quasistatic signal in the skin at 100–500 kHz. Lower carriers leak less: under 10 cm at 100 kHz against about 40 cm at 1 MHz [10]. Coherent modulation at 10–100 kb/s or more. Current of a few microamps [11] | Discrete DAC and electrode driver; Microchip shipped a discrete 125 kHz body-coupling kit in 2013 [12]. Ixana's Wi-R chip advertises 100 kb/s–5 Mb/s, but its carrier is unpublished [13] |
| Security | Device key, per-frame MAC, checkpoint signatures | Microchip ATECC608B: P-256, 2×3 mm, under 150 nA asleep [14] |
| Link and power | USB-C to the hub: USB audio plus data. The cable also carries a shared ground that closes the body-code loop | Bus-powered with no battery: under about 150 mW against 2.5 W available (estimate) |

The skull-versus-mic matching runs in the hub, on signed streams that left the earbud on one clock, so the earbud itself stays simple (proposal). The cable carries four 48 kHz microphone channels plus the skull channel, roughly 3 Mb/s of raw 16-bit audio (estimate), well within USB 2.0.

**Prototype path.**
1. Prove skull-versus-mic matching on OpenEarable 2.0, an open research earbud with a bone sensor and inner and outer mics [15].
2. Bench-test the body code: a signal generator and electrode at the ear, receivers at the wrist and on a keycap, measuring signal level and leakage at 100, 250 and 500 kHz.
3. Build a first wired earbud on a USB audio board with the LSM6DSV16BX and two mics.

## 3. Wristbands

| Function | Spec | Candidate parts |
|---|---|---|
| Electrodes | 16 bipolar channels from dry gold-plated electrodes (48 pins in Meta's design) | Meta's research band used about 10 pF in parallel with 10 TΩ input impedance, built from discrete parts in each electrode pod [16] |
| Front end | 16 channels at 2 kHz, noise near 2.5 µVrms | Intan RHD2216: 16 differential channels, 2.4 µVrms, about 3.5 mW for 16 channels at 2 kS/s [17]. Fallback: two TI ADS1298, about 1.1 mW per channel [18]. Avoid the ADS1299 for all-day wear, at about 4.9 mW per channel [19] |
| Resolution | About 11 effective bits, since Meta's chain had about 65.5 dB of dynamic range [16]. Pack samples to 12 bits: 384 kb/s per band (estimate) | — |
| Motion | 6-axis inertial sensor for context and the "wrist moved" cue | LSM6DSV16BX-class part [5] |
| Body-code receiver | A separate high-impedance electrode, an ADC and a digital correlator that hears the earbuds' code all the time (proposal) | Same front-end approach as the keycaps (section 4) |
| Skin contact | Electrode-impedance checks detect removal (proposal) | — |
| Radio and compute | Bluetooth LE 2M, one link per band, about 1.3–1.4 Mb/s at best [20] | Nordic nRF54L15: 2.45×2.25 mm, 4.8/3.4 mA transmit/receive at 0 dBm, TrustZone and a hardware key store for Ed25519 and P-256 [21] |
| Security | Device key and per-packet MAC | The nRF54L15's key store, or an NXP SE050 (EAL6+, Ed25519) for a separate certified chip [22] |
| Battery | About 12–22 mW average with the RHD2216 and nRF54L15 streaming, so 18 hours needs about 75–140 mAh (estimate) | 150–250 mAh pouch cell; a 150 mAh cell is about 20×26×3.8 mm [23] |

Meta's research band ran about 4 hours per charge [16], and its consumer Neural Band about 18 hours [24]. Vault's target is a full working day, with a second pair swapping in during a fingerprint touch. The RHD2216's input impedance is about 13 MΩ at 1 kHz, far below the input stage of Meta's research band [17, 16]. Dry electrodes will probably need a buffer at each electrode, which is the main analog design risk.

**Prototype path.**
1. Develop the muscle-to-keystroke pairing on two MindRove armbands (8 channels at 500 Hz) [25] and an analog keyboard.
2. Build a tethered 16-channel band: an RHD2216 evaluation board with a dry-electrode strap.
3. Build the wireless band with the nRF54L15 and a 150–250 mAh cell.

## 4. Keyboard

| Function | Spec | Candidate parts |
|---|---|---|
| Switches | Analog Hall-effect switches, every key scanned at 8 kHz, actuation set in 0.1 mm steps; the Wooting 80HE ships this today [26] | TI TMAG5253 Hall sensor: 15 kHz bandwidth, 2 mA active [27]. Firmware base: libhmk, open source, 8 kHz [28] |
| Timestamps | Taken at actuation on the keyboard's own clock, before USB | Keyboard microcontroller |
| Electrode keycaps | Conductive keycap tops on spring contacts. When a key's Hall sensor shows travel, its electrode is routed to one of a few receive channels, so only pressed keys are listened to (proposal) | Per-key buffer: TI OPA320, 0.9 pA bias [29]. Low-capacitance mux: ADI ADG1208, 1 pF [30]. Correlator on an ST STM32G474 with five 4 Msps ADCs [31]. DiamondTouch used 100 kHz bursts and synchronous demodulation [32] |
| Fingerprint key | Encrypted link to the keyboard's secure element; matching for identity, confirmations and a duress finger | Fingerprint Cards FPC2534 AllKey Pro: AES-GCM host link, Ø11 mm, 508 dpi, false-accept rate 1 in 100,000, identification in 160–2,050 ms [33]. The development kit lists at $170, restock estimated January 2027 [34] |
| Security | Device key; MAC on every key event; signed checkpoints | NXP SE051: EAL6+ (AVA_VAN.5), about $2.88 at 1,000 units [35, 36] |
| Link | USB-C to the hub only, never directly to the computer. The hub presents an ordinary keyboard to the computer once the checks pass | Keyboard microcontroller with USB device mode |

The fingerprint key needs its own trust design. Windows Enhanced Sign-in Security accepts only match-on-sensor parts certified with Microsoft at manufacture, which a small builder can't realistically get [37]. In 2023, researchers bypassed shipping laptop fingerprint sensors where the secure channel was misconfigured or missing [38]. The FPC2534 has an encrypted link but no attestation, and its lockout resets with its firmware [33]. So the keyboard pairs the sensor at the factory, keeps its own attempt counter, and attests to the hub, Apple-style (proposal) [1].

**Prototype path.**
1. Wooting 80HE plus its analog SDK, for key timing [26].
2. One hand-made copper-foil electrode keycap on a bench receiver, to measure body-code detection per press.
3. A custom keyboard PCB on libhmk with electrode keycaps, an SE051 and an FPC2534 fingerprint key.

## 5. Camera module

| Function | Spec | Candidate parts |
|---|---|---|
| Image sensor | Monochrome global shutter, about 1 MP, 60–120 fps | OmniVision OV9282: 1280×800 at 120 fps, 2-lane MIPI, in volume production [39]. ams OSRAM Mira220: 1600×1400 at 90 fps, quantum efficiency 56% at 850 nm and 36% at 940 nm [40] |
| Illumination | Its own 850 or 940 nm light, so it works in the dark, pulsed in a random pattern per frame as a liveness challenge (proposal) | VCSEL emitter classified eye-safe (Class 1) under IEC 60825-1 [41] |
| Depth for liveness | A coarse 3D check that rejects flat images | ST VL53L8CX: 8×8 zones at 60 Hz, 940 nm, Class 1 [42]. For full depth, Infineon IRS2976C time-of-flight, which passed Google's strongest face-unlock class [43] |
| Processor | Detects and crops the face, counts people in view, MACs every frame under the hub session key and signs checkpoints, with a DICE-derived device identity (proposal) | ST STM32N6: MIPI camera input, image signal processor, 600 GOPS NPU [44] |
| Bandwidth | Full frames at 120 fps are about 983 Mb/s, beyond USB 2.0 (estimate), so the module sends the cropped face region or uses USB 3 | — |
| Link | USB-C to the hub; frames never reach the computer | — |

A custom module is needed because Windows Enhanced Sign-in Security doesn't support external cameras [37]. MIPI has published camera security specifications, but they are members-only, and no sensor advertising them was found [45]. The signing therefore happens in the module's processor rather than in the sensor itself.

**Prototype path.**
1. A USB infrared camera on a single-board computer standing in for the module.
2. An STM32N6 development kit with an OV9282 sensor, to prove frame signing and on-module cropping.

## 6. Hub

| Function | Spec | Candidate parts |
|---|---|---|
| Processor | Runs voice matching, keystroke decoding and face matching in an isolated environment | NXP i.MX 93, NPU of about 0.5 TOPS [46]; or i.MX 95, about 2 TOPS and a 10–15-year supply program [47]. Both include NXP's EdgeLock secure enclave with tamper support |
| Secure element | Root keys, device certificates, signatures on the trace log | NXP SE051, EAL6+ (AVA_VAN.5) [35] |
| Radios | One Bluetooth receiver per wristband, so two bands never share a link | Nordic nRF54L15 [21] |
| Ports | USB-C downstream to the earbuds, keyboard and camera; USB-C upstream to the computer, which sees an ordinary keyboard and audio device only once the checks pass | — |
| Clock | Disciplines every device to within 1 ms | SiTime SiT5356 temperature-compensated oscillator, ±0.1 ppm [3]; RV-3032-C7 real-time clock, ±1.5 ppm [48] |
| Tamper | Opening the case erases the keys | Enclosure mesh plus ADI DS3645 battery-backed key memory with mesh inputs [49] |
| Trusted display and speaker | Shows or reads the exact action to confirm, driven only by the hub's secure side; see [the command chain](agents.html) | Small display and speaker (parts not yet selected) |
| Trace log | Append-only Merkle log in encrypted flash, with checkpoints witnessed by the owner's phone | — |
| Power | USB-C Power Delivery from the wall | — |

**Prototype path.**
1. Raspberry Pi Compute Module 5, from $67.50 [50], with the AI HAT+ 2 (40 TOPS INT4, $130) [51] and an SE051 evaluation board. The Pi has no trusted execution environment, so this stage proves the checks, not the security.
2. An i.MX 93 evaluation board with its secure enclave, the SE051 and the nRF54L15 receivers.

## 7. Links, clocks and keys

Three cables and two radio links reach the hub. The body code travels separately, through the skin, from the earbuds to the wristbands and the keycaps.

| Device | Link to hub | Data | Clock sync (proposal) | Keys |
|---|---|---|---|---|
| Earbuds | USB-C cable | 4 mics at 48 kHz plus skull channel, about 3 Mb/s raw (estimate) | USB frame timing | ATECC608B device key; session MAC |
| Wristbands | Bluetooth LE 2M, one receiver per band | 16 channels × 2 kHz × 12 bits = 384 kb/s per band (estimate) | Hub time beacon at each connection event | nRF54L15 key store |
| Keyboard | USB-C cable | Key events with depth and keycap body-code results; encrypted fingerprint data | USB frame timing | SE051 device key; MAC per key event |
| Camera module | USB-C cable (USB 3, or cropped frames) | Cropped face region at 60–120 fps | USB frame timing | DICE identity in the STM32N6 |
| Hub to computer | USB-C upstream | Keyboard and audio only after checks pass | — | — |

## 8. Prototype path

| Phase | Build | What it proves | Pass mark (proposal) |
|---|---|---|---|
| P0, bench | OpenEarable 2.0, two MindRove bands, a Wooting 80HE, a copper-foil electrode keycap, a signal-generator body code, and a Raspberry Pi hub; the [bench plan](bench.html) prices and wires the build | The three core checks work at all | Dictation from the wearer accepted at least 97% of the time with loudspeaker playback rejected, as in VAuth [52]; at least 95% of keys paired in 20-key windows [53]; body code detected on at least 99% of presses at a few microamps |
| P1, device boards | Wired earbud board; tethered RHD2216 band; keyboard PCB with electrode keycaps, SE051 and FPC2534; STM32N6 camera; i.MX 93 hub | Each device signs its data and pairs with the hub | Every injected frame, key or audio packet rejected; clocks within 1 ms |
| P2, alpha | Wireless bands with nRF54L15 and 150–250 mAh cells; enclosures; tamper; trace log; trusted display | A full working day of use | A full day on one charge; false lockouts rare enough to keep working (to be measured) |

## 9. Open questions

- **Skin current.** Body-channel currents of a few microamps sit about 2,000 times below the contact current where pain begins [11, 54]. Continuous all-day injection still needs a medical-safety review, including for people with pacemakers.
- **Dry electrodes on the RHD2216.** Its input impedance is far below Meta's front end, so per-electrode buffers may be needed [17, 16].
- **Signing speed.** How long a secure element takes per signature decides whether every event can be signed or only MAC'd with periodic signed checkpoints.
- **Body-channel chips.** Ixana publishes no carrier frequency or price, and reported 100,000-unit minimum orders in 2023 [13, 55]. A discrete transmitter and receiver is the safer plan.
- **Shared ground.** Wired earbuds and the keyboard share the hub's ground, which changes body-code signal strength and leakage compared with the battery-powered setups studied. An Oxford prototype told the body channel from fakes 99.3% of the time, but on battery power [56]. Measure on the bench.
- **Fingerprint supply.** The FPC2534 development kit is out of stock until about January 2027 [34].

## 10. Sources

1. [Apple Platform Security, "Magic Keyboard with Touch ID"](https://support.apple.com/guide/security/magic-keyboard-with-touch-id-secf60513daa/web). *Vendor documentation.*
2. [USB-IF, USB Type-C Authentication program](https://design-reuse.com/news/45346/usb-type-c-authentication-program.html). *Industry announcement via trade press.*
3. [SiTime SiT5356 Super-TCXO](https://www.sitime.com/products/super-tcxo/sit5356). *Vendor product page.*
4. [NCC Group, "BLE proximity authentication vulnerable to relay attacks" (2022)](https://www.nccgroup.com/research/technical-advisory-ble-proximity-authentication-vulnerable-to-relay-attacks/). *Security research advisory.*
5. [ST LSM6DSV16BX datasheet](https://www.mouser.com/datasheet/2/389/lsm6dsv16bx-3006819.pdf). *Vendor datasheet (distributor copy); some figures from ST page summaries.*
6. [Bosch Sensortec BMA580](https://www.bosch-sensortec.com/products/motion-sensors/accelerometers/bma580/). *Vendor product page.*
7. [Infineon IM69D129F MEMS microphone datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-im69d129f-datasheet-en.pdf). *Vendor datasheet.*
8. [TDK InvenSense T5848 microphone](https://invensense.tdk.com/products/digital/t5848/). *Vendor product page.*
9. ["Who's Wearing? Ear Canal Biometric Key Extraction" (EarID, arXiv 2510.02563, 2025)](https://arxiv.org/abs/2510.02563). *Preprint.*
10. [Maity, Modak and Sen, sub-microwatt body-channel communication node (IEEE JSSC 56(3), 2021)](https://doi.org/10.1109/JSSC.2020.3041874). *Peer-reviewed.*
11. [Maity et al., safety of capacitive body-channel communication (2020)](https://par.nsf.gov/servlets/purl/10249173). *Peer-reviewed.*
12. [Microchip, BodyCom body-coupled communication (2013)](https://ir.microchip.com/news-events/press-releases/detail/789/microchips-bodycom-technology-is-worlds-first-to-use-human-body-as-a-secure-low-power-communication-channel). *Vendor press release.*
13. [Ixana Wi-R body-area-network chip](https://www.ixana.ai/products/chips/wi-r-ban). *Vendor page; figures are vendor claims.*
14. [Microchip ATECC608B summary datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/ATECC608B-CryptoAuthentication-Device-Summary-Data-Sheet-DS40002239A.pdf). *Vendor datasheet.*
15. [OpenEarable 2.0: open-source earphone platform (University of Bath research portal)](https://researchportal.bath.ac.uk/en/publications/openearable-20-open-source-earphone-platform-for-physiological-ea/). *Research platform.*
16. [CTRL-labs at Reality Labs, generic neuromotor interface preprint (bioRxiv, 2024; Nature 2025)](https://www.biorxiv.org/content/10.1101/2024.02.23.581779.full.pdf). *Preprint of a peer-reviewed paper.*
17. [Intan RHD2000 series datasheet](https://intantech.com/files/Intan_RHD2000_series_datasheet.pdf). *Vendor datasheet.*
18. [TI ADS1294/6/8 datasheet](https://www.ti.com/lit/ds/symlink/ads1298.pdf). *Vendor datasheet.*
19. [TI ADS1299 datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf). *Vendor datasheet.*
20. [Novel Bits, "Bluetooth 5 speed: maximum throughput"](https://novelbits.io/bluetooth-5-speed-maximum-throughput/). *Engineering explainer.*
21. [Nordic Semiconductor nRF54L15](https://www.nordicsemi.com/nrf54L15). *Vendor product page.*
22. [NXP SE050 datasheet](https://www.nxp.com/docs/en/data-sheet/SE050-DATASHEET.pdf). *Vendor datasheet.*
23. [Adafruit, 150 mAh lithium-ion polymer battery (product 1317)](https://www.adafruit.com/product/1317). *Retail listing.*
24. [Android Authority, Meta Ray-Ban Display and Neural Band](https://www.androidauthority.com/meta-ray-ban-display-3598809/). *Trade press (vendor figures).*
25. [MindRove armband product page](https://mindrove.com/armband/). *Vendor page.*
26. [Wooting 80HE product page](https://wooting.io/wooting-80he). *Vendor page; figures are vendor claims.*
27. [TI TMAG5253 Hall-effect sensor](https://www.ti.com/product/TMAG5253). *Vendor product page.*
28. [libhmk, open-source Hall-effect keyboard firmware (GitHub)](https://github.com/peppapighs/libhmk). *Open-source project.*
29. [TI OPA320 operational amplifier](https://www.ti.com/product/OPA320). *Vendor product page.*
30. [Analog Devices ADG1208 multiplexer](https://www.analog.com/en/products/ADG1208.html). *Vendor product page.*
31. [ST STM32G474RC microcontroller](https://www.st.com/en/microcontrollers-microprocessors/stm32g474rc.html). *Vendor product page.*
32. [Dietz and Leigh, "DiamondTouch" (MERL TR2003-125)](https://www.merl.com/publications/docs/TR2003-125.pdf). *Technical report.*
33. [Fingerprint Cards FPC2534 AllKey Pro supplement](https://www.fpc.com/media/p4za3l5q/spc27387-3-fpc2534-allkey-pro-supplement.pdf). *Vendor document.*
34. [DigiKey, FPC2534 development kit listing](https://punchouttest.digikey.com.mx/en/products/detail/fingerprint-cards-ab/100026232/25649788). *Distributor listing.*
35. [NXP SE051 secure element](https://www.nxp.com/products/SE051). *Vendor product page.*
36. [DigiKey, NXP SE051 listing](https://www.digikey.com/es/products/detail/nxp-usa-inc/SE051C2HQ1-Z01XDZ/18712817). *Distributor listing.*
37. [Microsoft Learn, "Windows Hello Enhanced Sign-in Security"](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/windows-hello-enhanced-sign-in-security). *Vendor documentation.*
38. [Blackwing Intelligence, "A Touch of Pwn, Part I" (2023)](https://blackwinghq.com/blog/posts/a-touch-of-pwn-part-i/). *Security research.*
39. [OmniVision OV9282 global-shutter sensor](https://www.ovt.com/products/ov9282/). *Vendor product page.*
40. [ams OSRAM Mira220 NIR global-shutter sensor datasheet](https://look.ams-osram.com/m/7591efdbe4af32dc/original/Mira220-1-2-7-2-2-MP-NIR-enhanced-global-shutter-image-sensor.pdf). *Vendor datasheet.*
41. [940 nm VCSEL emitter datasheet (IEC 60825-1 classification example)](https://www.mouser.lt/datasheet/3/5912/1/PLPVYL1_940A_E_EN.pdf). *Vendor datasheet (distributor copy).*
42. [ST VL53L8CX time-of-flight sensor](https://www.st.com/en/product/vl53l8cx). *Vendor product page.*
43. [Mouser, Infineon IRS2976C time-of-flight sensor](https://www.mouser.se/new/infineon/infineon-irs2976c-tof-sensor). *Distributor page with vendor claims.*
44. [ST STM32N6 flyer](https://www.st.com.cn/resource/en/flyer/flstm32n6.pdf). *Vendor flyer.*
45. [MIPI Alliance blog, camera security specifications (CCISE)](https://www.mipi.org/blog/whats-new-in-mipi-security-mipi-ccise-and-security-for-debug). *Standards body.*
46. [Digi, i.MX 93 NPU documentation](https://docs.digi.com/resources/documentation/digidocs/embedded/dey/5.0/cc93/bsp-npu_r_93.html). *Vendor documentation.*
47. [NXP i.MX 95 applications processor](https://www.nxp.com/products/i.MX95). *Vendor product page.*
48. [Micro Crystal RV-3032-C7 real-time clock datasheet](https://cdn.sparkfun.com/assets/c/d/6/3/1/RV-3032-C7_Datasheet.pdf). *Vendor datasheet (distributor copy).*
49. [Analog Devices DS3645 tamper-detection key manager](https://analog.com/en/products/ds3645). *Vendor product page.*
50. [Raspberry Pi Compute Module 5](https://www.raspberrypi.com/products/compute-module-5/). *Vendor product page.*
51. [Raspberry Pi AI HAT+ 2 coverage (Tecnoblog)](https://tecnoblog.net/noticias/raspberry-pi-anuncia-placa-ai-hat-2-com-40-tops-para-ia-preco-e-alto/). *Trade press.*
52. [Feng, Fawaz and Shin, "Continuous Authentication for Voice Assistants" (VAuth, MobiCom 2017)](https://ar5iv.labs.arxiv.org/html/1701.04507). *Peer-reviewed; 18 users.*
53. [Gazzari et al., "My(o) Armband Leaks Passwords" (IMWUT, 2021)](https://ar5iv.labs.arxiv.org/html/2112.02382). *Peer-reviewed.*
54. [ICNIRP, Guidelines for limiting exposure to electromagnetic fields (2020)](https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf). *International guidelines.*
55. [Hackster.io on Ixana Wi-R (2023)](https://www.hackster.io/news/ixana-s-wi-r-wire-like-wireless-aims-to-put-you-in-touch-with-your-tech-s-comms-literally-e2979cbb1d3e). *Trade press.*
56. [Roeschlin, Martinovic and Rasmussen, device pairing through the body (NDSS 2018)](https://www.cs.ox.ac.uk/files/9833/pairing.pdf). *Peer-reviewed.*
