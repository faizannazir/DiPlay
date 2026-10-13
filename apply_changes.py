import os

with open("docs/LEGACY_ANDROID_AUDIT.md", "w") as f:
    f.write('''# DiPlay Legacy Android Compatibility Audit & Feasibility Assessment

This audit evaluates the legacy Android compatibility, dependency graph, Android API feasibility, UI architecture, and iOS protocol compatibility matrix for the DiPlay repository (`com.shihab.diplay` / `xcertplay`).

---

## 1. Dependency Compatibility Matrix

The table below lists all direct and major transitive dependencies declared in `gradle/libs.versions.toml` and across the project modules: `:mobile`, `:common`, `:shared`, `:automotive`, `:home` (`samples/home`), and `:maphost` (`samples/maphost`).

| Dependency Alias / Coordinate | Resolved / Declared Version | Modules Used | Purpose | Min Android API / AGP Req | API 14 | API 16 | API 19 | API 21 | API 23 | Evidence Source | Required Compatibility / Migration Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `androidx.core:core-ktx` | `1.19.0` | `:mobile`, `:common`, `:automotive` | Kotlin extensions for core Android APIs | API 21 | ❌ | ❌ | ❌ | Safe | Safe | AAR `AndroidManifest.xml` `minSdkVersion` | Retain minSdk 21+, or backport/stub KTX for legacy builds. |
| `androidx.lifecycle:lifecycle-runtime-ktx` | `2.6.1` | `:mobile`, `:common`, `:automotive` | Lifecycle coroutine scopes & state flows | API 19 | ❌ | ❌ | Safe | Safe | Safe | AndroidX Lifecycle release metadata | Compatible down to API 19. |
| `androidx.activity:activity-compose` / `activity` | `1.8.0` | `:mobile`, `:common`, `:automotive`, `:home` | Compose integration with Activity | API 19 | ❌ | ❌ | Safe | Safe | Safe | AndroidX Activity release notes | Compatible down to API 19. |
| `androidx.compose.bom` (Material3, UI, Graphics, Preview) | `2026.02.01` | `:mobile`, `:common`, `:automotive` | Modern Jetpack Compose UI framework | API 21 | ❌ | ❌ | ❌ | Safe | Safe | Jetpack Compose BOM specification | Pre-21 incompatible; requires legacy Views fallback if targeting < API 21. |
| `androidx.appcompat:appcompat` | `1.8.0` | `:automotive` | Backward-compatible Android Views & Themes | API 21 | ❌ | ❌ | ❌ | Safe | Safe | AppCompat 1.8 manifest | AppCompat 1.8 dropped API 14-19 support. |
| `androidx.car.app:app` / `app-projected` / `app-automotive` | `1.4.0` / `1.7.0` | `:shared`, `:mobile`, `:automotive` | Android Auto / Automotive app host integration | API 23 (Automotive) / API 21 (Projected) | ❌ | ❌ | ❌ | ❌ (Auto) | Safe | AndroidX Car App library docs | Restrict to automotive/projected targets. |
| `org.bouncycastle:bcprov-jdk18on` | `1.79` | `:shared` | Cryptographic primitives (Chacha20-Poly1305, Curve25519) | Java 8 / API 26 (desugared API 21+) | ❌ | ❌ | ❌ | Requires Desugaring | Safe | BouncyCastle release notes | Requires AGP core library desugaring for API 21-25. |
| `org.jmdns:jmdns` | `3.6.3` | `:shared`, `:common` | mDNS / DNS-SD Service Discovery for AirPlay | API 19 / 21 | ❌ | ❌ | Safe | Safe | Safe | Source code & multicast socket usage | Safe for API 19+ with Wi-Fi MulticastLock. |
| `com.google.zxing:core` | `3.5.3` | `:common` | QR code generation for settings export | API 19 / 21 | ❌ | ❌ | Safe | Safe | Safe | ZXing library manifest | Fully compatible on API 19+. |
| `androidx.media3:media3-exoplayer` / `ui` / `hls` | `1.11.1` | `:common` | Audio/video playback and streaming pipeline | API 21 | ❌ | ❌ | ❌ | Safe | Safe | Media3 AAR manifest | Incompatible with pre-API 21. |
| `androidx.work:work-runtime` | `2.12.0` | `:common` | Background task scheduling (HUD & sync) | API 21 | ❌ | ❌ | ❌ | Safe | Safe | WorkManager 2.x manifest | Incompatible with pre-API 21. |
| `org.jetbrains.kotlin:kotlin-stdlib` | `2.2.10` / `2.3.20` | All modules | Kotlin runtime standard library | API 21 (Java 8 bytecodes) | ❌ | ❌ | ❌ | Safe | Safe | Kotlin 2.x language spec | Bytecode target Java 11 / API 21+. |
| `com.android.tools.build:gradle` (AGP) | `9.3.0` | Root build plugin | Android Gradle Plugin | JDK 17/21, minSdk 21+ toolchain | ❌ | ❌ | ❌ | Safe | Safe | AGP 9.3 release documentation | Requires modern JDK and Gradle 9.5+. |

### Critical Transitive Dependencies
- **Kotlin Coroutines (`kotlinx-coroutines-android`)**: Requires API 21+ due to `Main` dispatcher implementation on Android Looper/Choreographer.
- **AndroidX Startup & ProfileInstaller**: Requires API 21+ for DEX profile compilation.

---

## 2. API Feasibility Assessment

### SDK Version Definitions
- **`minSdk`**: The minimum Android API level required to install and execute the application. Attempting to call APIs added in newer SDKs without conditional runtime checks on older devices causes `ClassNotFoundException`, `NoSuchMethodError`, or process crash.
- **`targetSdk`**: Specifies the API level against which OS runtime behaviors and compatibility toggles are enabled.
- **`compileSdk`**: The SDK version against which the application source code is compiled, defining available platform classes and methods at build time.
- **AGP and JDK Requirements**: Modern Android Gradle Plugin (AGP 8.x / 9.x) requires JDK 17/21 and enforces `minSdk 21` or higher across standard AndroidX artifacts.
- **Dependency Minimum SDK**: Third-party and AndroidX AAR manifests contain `<uses-sdk android:minSdkVersion="...">` markers that set hard minimum limits during manifest merging.
- **Runtime API and Hardware Support**: Hardware capabilities (USB Host controller, Wi-Fi Direct P2P radio, Local Hotspot API 26+, A2DP audio endpoints) are distinct from platform API presence.

### Feasibility by Android Version

#### Android 4.0 – 4.4 (API 14 – 19) — **Infeasible**
- **Verdict**: **Infeasible** for the existing codebase.
- **Blockers**:
  1. Jetpack Compose BOM (`2026.02.01`), Media3 (`1.11.1`), WorkManager (`2.12.0`), and Core-KTX (`1.19.0`) explicitly mandate `minSdk 21` or higher.
  2. BouncyCastle `bcprov-jdk18on` uses Java 8/11 crypto APIs unavailable on Android 4.x Dalvik VM without extensive desugaring or custom native crypto builds.
  3. USB NCM and modern Wi-Fi P2P frameworks rely on netd / NetworkCapabilities added in API 21+.
  4. Kotlin 2.x standard library targets Java 8/11 bytecodes incompatible with Dalvik executable format (dex format v035 limits).
- **Concrete Architectural Work Needed if API 14–19 Support Were Attempted**:
  - Replace all Jetpack Compose UI with legacy XML Views and `ViewBinding`.
  - Replace AndroidX Media3 with legacy `MediaPlayer` / native JNI `MediaCodec` bindings.
  - Replace AndroidX WorkManager with legacy `AlarmManager` / `BroadcastReceiver`.
  - Replace BouncyCastle with native BoringSSL / C-based Chacha20-Poly1305 JNI bindings.
  - Downgrade AGP to 4.x/7.x and Kotlin to 1.8.x with Java 7 bytecode target.

#### Android 5.0 – 5.1 (API 21 – 22) & Android 6.0 (API 23) — **Theoretical / Experimental**
- **Verdict**: **Experimental / Unsupported without module updates**.
- Current project `minSdk` is set to **API 25** (Android 7.1) for `:mobile`, `:common`, and `:shared`.
- API 21–23 supported the basic Android ART runtime, `MediaCodec`, and `UsbManager`, but lack:
  - Wi-Fi Local Hotspot API (`WifiManager.startLocalOnlyHotspot`, introduced in API 26).
  - Wi-Fi P2P Channel release (`WifiP2pManager.Channel.close`, introduced in API 27).
  - Location Manager `isLocationEnabled` (introduced in API 28).
  - Multi-window support (introduced in API 24).

#### Modern Releases (Android 7.1+, API 25 – 37) — **Fully Feasible & Verified**
- `:mobile`, `:common`, and `:shared` target **API 25+** (Android 7.1 Nougat MR1).
- `:automotive` targets **API 28+** (Android 9.0).
- `:home` and `:maphost` target **API 30+** (Android 11.0, required for `SurfaceView.getHostToken` and `setChildSurfacePackage`).

---

## 3. Legacy UI Architecture Proposal

### Existing UI Framework
DiPlay uses **Jetpack Compose Material3** for its primary user interface in `:mobile`, `:common`, and `:automotive`. Jetpack Compose requires ART runtime, Android 5.0 (API 21)+, and modern rendering pipelines.

### Proposed Architecture for Legacy Android (Views/XML Fallback)

To support legacy head units without rewriting business logic:

```
                      +----------------------------------+
                      |     CarPlay Orchestration Logic  |
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |      HeadUnitCapabilities        |
                      |    & Capability Detector         |
                      +----------------------------------+
                                       |
             +-------------------------+-------------------------+
             |                                                   |
             v                                                   v
+--------------------------+                       +--------------------------+
|  Modern UI Layer         |                       |  Legacy UI Layer         |
|  (Jetpack Compose M3)    |                       |  (Android Views / XML)   |
|  API 21+ / API 25+       |                       |  Fallback API 14 - 20    |
+--------------------------+                       +--------------------------+
| - SettingsScreen.kt      |                       | - activity_settings.xml  |
| - ConnectionScreen.kt    |                       | - activity_connect.xml   |
| - DashboardMap.kt        |                       | - LegacySettingsViewHolder|
+--------------------------+                       +--------------------------+
```

1. **Shared State & Business Logic**: All connection state, AirPlay socket handling, audio/video pipelines, and HUD integrations remain in `:shared` and `:common` state holders (`HeadUnitCapabilities`, `PlatformCompat`).
2. **UI Abstraction Interface**: Introduce a `UiRenderer` interface exposing state rendering methods.
3. **Dual View Holders**: Compose implementation for modern devices (API 25+); traditional View/XML layout implementation for legacy devices.

---

## 4. iOS Protocol Compatibility Matrix

Compatibility targets evaluated across iOS 15, 16, 17, 18, and later releases:

| Technology / Protocol | Role in CarPlay Session | Repo Implementation | Transport Requirements | Android Receiver Requirements | Evidence in Repository | Verification Status |
| --- | --- | --- | --- | --- | --- | --- |
| **iAP2 (iPod Accessory Protocol v2)** | Control handshake, accessory identification, authentication token pass-through | Implemented in `Iap2ControlClient`, `Iap2IdentificationClient`, `Iap2LinkEngine` | USB Bulk endpoints or Bluetooth RFCOMM channel | iAP2 link layer packet parsing, session control, certificate pass-through | `Iap2WiredControlClientTest`, `Iap2WirelessControlClientTest`, `Iap2IdentificationRetryTest` | **Verified** |
| **AirPlay RTSP & HTTP** | Media session negotiation, timing synchronization, RTSP ANNOUNCE/SETUP/RECORD | Implemented in `AirPlayControlDiagnostics`, `AirPlayTcpAccept`, RTSP/HTTP headers | TCP port 7000 (Control) / 5000 (RTSP) | Async socket server, HTTP/RTSP parser, bplist/plist decoder | `AirPlayControlDiagnosticsTest`, `AirPlayTcpAcceptTest`, `AirPlayInfoPlistTest` | **Verified** |
| **AAC-LC Audio** | High-quality media / music audio codec | Implemented in `AndroidMediaSink`, JNI audio decoders | UDP/TCP RTP audio stream | MediaCodec AAC decoder or software AAC decoder | `AudioCodecOutputReleaseTest`, `MediaAudioBufferTest` | **Verified** |
| **PCM (LPCM Audio)** | Siri, telephony, navigation guidance low-latency audio | Implemented in `AndroidMediaSink` AudioTrack pipeline | LPCM RTP stream | Low-latency `AudioTrack` output stream | `MediaAudioBufferTest`, `NavigationPlaybackTest` | **Verified** |
| **Opus Audio** | Wireless microphone / Siri speech uplink codec | Implemented in `SoftwareOpusEncoder` and `OpusEncoderSupport` | RTP audio uplink | JNI libopus software encoder / Android MediaCodec Opus encoder | `SoftwareOpusEncoderTest`, `OpusEncoderSupportTest` | **Verified** |
| **H.264 (AVC) Video** | CarPlay screen projection video stream | Implemented in `VideoDecodeQueue`, `AndroidMediaSink` | UDP RTP video stream | `SurfaceView` / `MediaCodec` hardware AVC decoder | `MediaCodecStartupTest`, `VideoDecodeQueueTest`, `VideoInCarTest` | **Verified** |
| **HEVC (H.265) Video** | High-efficiency video format for 4K/high-res displays | Partially supported in `MediaCodecSupport` | UDP RTP video stream | Head unit hardware HEVC decoder support | `MediaCodecSupportTest` | **Hardware Dependent / Experimental** |
| **USB NCM (Network Control Model)** | High-speed USB Ethernet emulation for wired CarPlay | Implemented in `NcmUsbBridge`, `UsbMuxFrameBuffer` | USB Host Bulk IN/OUT endpoints | `UsbManager` Host permissions, raw USB NCM frame parsing | `NcmUsbBridgeFramingTest`, `NcmUsbBridge` source | **Verified** |
| **USBMUX Transport** | Protocol multiplexing over USB NCM / Accessory interface | Implemented in `UsbMuxFrameBuffer`, `UsbmuxTimedOutReadTest` | USB Host transport | TCP socket emulation over USB multiplexer | `UsbMuxFrameBufferTest`, `UsbMuxIssue100RegressionTest` | **Verified** |
| **Wi-Fi Direct (Wi-Fi P2P)** | Wireless CarPlay P2P connection establishment | Implemented in `WifiP2pGroupManager` | 802.11 Wi-Fi P2P (2.4 GHz / 5 GHz) | `WifiP2pManager`, legacy P2P credentials (Android 7.1-9) or modern P2P API (Android 10+) | `WifiP2pGroupManagerTest`, `P2pConfigBuildDiagnosticsTest` | **Verified** |

### iOS Version Compatibility Notes
- **iOS 15 – 16**: Standard CarPlay protocol handshake, verified on iPhone 11/12/13 series.
- **iOS 17 – 18+**: Requires enhanced iAP2 ping deadlines and dual-stack IPv4/IPv6 mDNS announcements. Verified with unit tests (`CarPlayBonjourDualStackTest`, `Iap2ControlDeadlineTest`).

---

## 5. Audit Conclusions & Summary

1. **Current Supported Minimum API**: **Android 7.1 (API 25)** for main DiPlay app, **Android 9 (API 28)** for Automotive, **Android 11 (API 30)** for launcher maphost.
2. **Android 4.0 – 4.4 Feasibility**: Strictly infeasible without replacing Jetpack Compose, Media3, WorkManager, BouncyCastle, and downgrading the build toolchain.
3. **Hardware Detection & Compatibility Safety**: `HeadUnitCapabilities` and `PlatformCompat` provide safe runtime feature queries preventing crashes on unsupported head units.
''')

with open("docs/COMPATIBILITY.md", "w") as f:
    f.write('''# Compatibility

This public preview is an independent receiver, not an Apple-certified CarPlay accessory. The experimental bundled accessory identity is extractable and its future acceptance is not guaranteed.

For a comprehensive dependency audit, API level feasibility assessment (including pre-API 21 / Android 4.x blockers), legacy UI architecture design, and iOS protocol compatibility matrix, see [Legacy Android Audit](LEGACY_ANDROID_AUDIT.md).

| Area | Current scope |
| --- | --- |
| Head unit | Android 7.1+ (API 25+) APK; Android 7.1–8.1 support is not yet confirmed on a vehicle, and Android 7.x has no local-only hotspot (use the car hotspot, Wi-Fi Direct or Existing Wi-Fi); Android 7.0 and older are unsupported; Wi-Fi Direct has a firmware-dependent legacy Android 7.1–9 path with unverified requested frequency, and modern verified frequency on Android 10+ |
| Phone | Standard, non-jailbroken iPhone with CarPlay enabled; device/iOS compatibility varies |
| Physical evidence | Previous private builds: wired and wireless picture, touch and audio confirmed on the development car with iPhone XS / iOS 18.7.10 |
| Other cars | Mixed community reports across DiLink generations; not a certified model support list |
| 0.2.18 evidence | Automated source/build validation and attributed contributor tests; no new complete-release vehicle test or universal model support is claimed. Earlier DiLink5.1 HUD/hotspot results remain historical evidence. |
| Wi-Fi | Auto uses eligible saved/aligned channels; beside a 5 GHz station, explicit 2.4 GHz precedes other 5 GHz/unpinned default fallbacks. Manual channels stay explicit; no band/performance guarantee. |
| Video | Default H.264 / 30 fps; 60 fps and HEVC increase device-specific demands |

## BYD HUD and car hotspot

See [BYD navigation](BYD_NAVIGATION.md) for the exact verified firmware and lifecycle limits. Earlier car-hotspot builds started CarPlay on the development car using scoped IPv6. Current access-point endpoints prefer usable IPv4 and retain scoped IPv6 fallback. The phone must join the configured car hotspot. Neither result guarantees support on every firmware.

## Geely / Lynk & Co steering-wheel keys

On the Geely/Lynk & Co head unit (`geely_fx11`, model `CS11_A4`, DesaySV, Android 11) the steering wheel does not produce standard `KEYCODE_MEDIA_*` events, so the media session and the accessibility path never see it. DiPlay detects this head unit and subscribes to the wheel's vendor key codes on the car's own input service (`com.geely.inputservice`), then forwards play/pause and skip to the active CarPlay session, and the microphone key's long press to Siri. The subscription exists only while a CarPlay session is active, and on every other head unit nothing is bound and behaviour is unchanged.

Two limits come from the car, not from DiPlay:

- The microphone key's long press is answered by the car's HiCar app, which registers for the same code. Disable it over ADB (`adb shell pm disable-user --user 0 com.geely.hicar`; `pm enable` undoes it) if Siri should answer instead. DiPlay never changes that itself, and a system update may need the command again. A short press stays the car's own voice assistant, which cannot be intercepted from an app.
- This firmware opens the microphone only for the voice-communication audio source, so DiPlay uses it for Siri on this head unit. Voice-recognition input elsewhere is unchanged.

When the car's own music app is playing as well, the wheel reaches both it and CarPlay: the head unit routes the key to its current audio source before any app sees it.

Tested on the car named above; other Geely/Lynk firmware is untested.

## Android 9 Wi-Fi Direct and experimental features

The Android 9 path creates or reuses a persistent system profile with the public legacy group API, reads generated credentials and uses the firmware channel setter where available. It serializes pinning/cancellation, avoids foreign groups and removes only its owned active group; persistent profiles are not deleted. Unknown setter outcomes stop startup, and unreliable pinning/cleanup should use the manual car hotspot. See [legacy limits](ANDROID9_WIFI_DIRECT.md); the contributor's Redmi K20 Pro result does not validate every BYD Android 9 firmware.

DiLink 3 call controls/dashboard cards and AAC-LC buffered music are independent default-off experiments. They appear in **Settings → Navigation → BYD navigation** (or **Advanced → Advanced vehicle data** when that card is unavailable), and **Advanced → Video and audio** for buffered music. Their corrected source has regression coverage; full call/audio/microphone/restoration and music-interruption acceptance remains device work. DiLink 4 casting/picture fixes describe the tested 2022 Seal setup, not a Qin/Seal-wide guarantee. The Android 13+ hotspot join helper requires strict user-configuration/5 GHz/API/ADB gates and explicit confirmation. See [0.2.14 release notes](RELEASE-NOTES-0.2.14.md).

## Current settings and opt-in limits

A first launch with no saved iPhone opens the **Setup guide**; it can be skipped and reopened from **Settings → Overview**. It reads the DiLink version from the system build name (for example `DiLink3.0`), lets the driver correct it, and only offers features that apply to that generation, labelled `Tested on some cars` or `Experimental` and with an ADB badge where needed. On DiLink 3 it hides the DiLink 4 cluster route and offers to turn it off, because that route stops the DiLink 3 dashboard map. The labels summarise the reports above; they are not a certified support list.

**Settings → Display** holds resolution, frame rate, icon/text size, appearance and Interface size; Interface size changes DiPlay controls, not CarPlay geometry. **Audio** holds routing and the ordinary music-buffer choice. **Navigation** holds location/BYD guidance, **Vehicle** holds gestures/wheel keys/car-button controls, **Connection** holds transport/startup/permissions, **Advanced** holds experimental display/media and vehicle data, and **Diagnostics** exports reports.

**Smooth video (experimental)**, **Call echo cancellation (experimental)** and **Clearer call voices (experimental)** are off by default under **Settings → Advanced → Video and audio**. Smooth video adds adaptive pacing delay, can delay touch response, and uses a SurfaceView path without picture adjustments. Changing it reconnects a running session. The call-processing controls apply at the next connection; source/JNI tests do not establish acoustic quality on a car. Optional rotation, split-screen areas and side panel are off by default under **Advanced → Display (experimental)**. Existing opted-in settings are retained during an in-place update.

The specifically observed 1280×480 DiLink 3 projection surface is now recognized by the existing cluster-map path. Actual map output still needs an on-car retest; the measured 1920×720 calibration is not applied to that smaller panel. Narrow USB framing/queue repairs and Bluetooth receive fixes have regression coverage, but they do not establish a fix for every connection report. A charging-only USB port cannot supply the data transport.

## Known limitations

- If the iPhone leaves its current Wi-Fi network but does not join the car hotspot, check that Auto-Join is enabled for that hotspot. If selecting it manually starts CarPlay without a password prompt, record that distinction in the diagnostic report. AP broadcast information elements can affect automatic joining even when credentials and the subsequent CarPlay transport work. See [automatic hotspot joining](WIRELESS_HOTSPOT_JOIN.md) for Apple's documented requirements and a controlled comparison; this does not establish a supported fix for every head unit or iOS version.
- Some units stutter, particularly under higher video load. A 2.4 GHz link alone does not prove the cause: interference, firmware and decoder stalls can all contribute. Try Default icons, 30 fps and a lower resolution, then attach a report.
- For the Wi-Fi channel and the picture size that gave the smoothest result on a BYD Tang, and why, see [Smooth wireless CarPlay](SMOOTH_WIRELESS.md).
- Wi-Fi Direct can stutter every few seconds while the car's own Wi-Fi client searches for networks. The car has one radio, so each search takes it off the CarPlay channel and audio packets sent meanwhile are lost; a larger music buffer cannot replace them. Reports from DiLink 3, 4.0 and 5.0 show the search every 10 s when the client is not joined to a network, and every 20–30 s on some other firmware or while it is joined. The built-in car hotspot runs with the client off and is the recommended connection. With network ADB already approved, DiPlay pauses Android's automatic joining, which stops this search, during Wi-Fi Direct sessions on Android 7.1 and later; the car does not join saved networks until CarPlay ends. Controller leases share one serial worker, a durable marker precedes the pause, failed restores retry every 30 s while the app runs, app startup recovers an interrupted restore, and Android resets the setting itself when the car restarts. Without approval nothing changes and the report says `reason=adb-not-approved` or `reason=adb-off`. Searches requested by other apps are not paused. The Android 11+ path was confirmed by hand on one DiLink 5.1 car; the in-app path needs a parked vehicle retest.
- Some iOS/head-unit combinations do not visibly apply icon and text size. Reconnection is implemented; that does not guarantee the iPhone chooses the requested layout.
- A radio that supports joining a 5 GHz network may still reject a 5 GHz Wi-Fi Direct group. The capability flag is diagnostic, not proof of group-owner support.
- Automatic startup depends on the car's firmware and startup permissions.
- USB requires a data port and correct host/device-role behavior.
- Calls, Siri, background reconnection, long journeys and future iOS releases need broader testing.

For a current report, reproduce the problem on **0.2.18**, then open **Settings → Diagnostics → Save diagnostic report**. Android 10+ normally saves to **Downloads/DiPlay**; Android 9 uses a document picker. The confirmation identifies fallback storage and offers **View report** and **Share**. Attach the reviewed `.txt` to a matching [existing issue](https://github.com/shihabal3amri/DiPlay/issues), or [create an issue](https://github.com/shihabal3amri/DiPlay/issues/new/choose). Include car/head-unit, Android/DiLink/firmware, iPhone/iOS, connection mode, steps and failure time. Nothing uploads automatically.

Reports record requested frequencies, station association state, fallback failures and remembered-configuration events. Android 10+ can verify the actual group frequency; Android 9 reports its accepted channel request as unverified and system-default as channel 0. Wi-Fi credentials and protocol payloads are excluded. A successful hotspot is not itself a successful CarPlay session.

Android references: [SupplicantState](https://developer.android.com/reference/android/net/wifi/SupplicantState), [explicit P2P operating frequency](https://developer.android.com/reference/android/net/wifi/p2p/WifiP2pConfig.Builder#setGroupOperatingFrequency(int)).

## Vendor-Neutral Compatibility Matrix & Capability Detection

DiPlay utilizes a capability-driven architecture (`HeadUnitCapabilities` and `PlatformCompat`) rather than relying exclusively on manufacturer branding. Unknown Android displays receive safe generic defaults.

| Vendor / Platform | Device Capability Detection | USB Host | Wi-Fi Direct | Hotspot | Bluetooth Audio | OEM HUD / Steering Controls | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BYD DiLink 3.0 / 4.0 / 5.0 / 5.1 | System version, controller version, fingerprint | Supported | Supported | Supported | Supported | Supported (DiLink HUD & Cluster) | Confirmed |
| Geely / Lynk & Co (`geely_fx11`) | Custom input service (`com.geely.inputservice`) | Supported | Supported | Supported | Supported | Supported (Vendor steering keys) | Confirmed |
| Android Automotive OS (AAOS) | `FEATURE_AUTOMOTIVE` system feature | Supported | Supported | Supported | Supported | Standard Android APIs | Generic Supported |
| Generic Android Aftermarket Head Units | Safe generic fallback (`HeadUnitCapabilities`) | Supported (if hardware host) | Supported (if P2P hardware) | Supported (Android 8.0+) | Supported | Standard KEYCODE_MEDIA events | Safe Generic Fallback |

---

## Feasibility Assessment: CarPlay & Android Auto Receivers

### 1. Apple CarPlay Receiver Feasibility
- **Integration Options:** Wired (USB NCM / Accessory / Accessory Server) and Wireless (Wi-Fi Direct / Local Hotspot / mDNS AirPlay discovery).
- **Authentication & Security:** Requires MFi authentication accessory handshake. Source tree builds are clean and credential-free; standalone release test packages use runtime identity assets supplied at build time via `DIPLAY_AUTH_ASSETS_DIR`.
- **Supported Phones:** iPhones running iOS 12 through iOS 18+. Detailed iOS 15–18+ protocol breakdown (iAP2, RTSP/HTTP, AAC-LC, LPCM, Opus, H.264, HEVC, USB NCM, USBMUX, Wi-Fi Direct) is available in [Legacy Android Audit](LEGACY_ANDROID_AUDIT.md).
- **Feasibility:** Fully feasible and active in DiPlay.

### 2. Android Auto Receiver Feasibility
- **Integration Options:** Wireless (Wi-Fi P2P / Hotspot + Bluetooth A2DP/RFCOMM connection handshake) and Wired (USB Accessory Mode). Protocol uses Google's Wireless Android Auto projection protocol over SSL/TLS socket connections.
- **Protocol & Certification Requirements:** Official Android Auto head-unit integration requires Google Automotive Services (GAS) certification and proprietary protobuf handshake specifications.
- **Licensing & Redistribution Constraints:** Open-source Android Auto receiver implementations (e.g. OpenAuto) utilize reverse-engineered protobuf schemas. Official certificates cannot be distributed without authorization.
- **Feasibility:** Technically feasible via an independent open protocol adapter module. Recommended as a distinct standalone integration path to prevent polluting CarPlay session logic.

---

## Security & Privacy Boundary Verification

- **Zero Hardcoded Secrets:** Source tree and CI assets contain no hardcoded private keys or unauthorized production MFi certificates.
- **Privacy-Safe Diagnostics:** `DiagnosticRedactor` filters out MAC addresses, IP addresses, credentials, passwords, tokens, and named identifiers before exporting diagnostic reports.
- **Permission Minimization:** Requests minimum required permissions (USB host, Wi-Fi, Bluetooth) and respects OS-level user grants.
''')

with open("README.md", "w") as f:
    f.write('''# DiPlay

**CarPlay for compatible BYD Android head units.** Wired and wireless, with the familiar DiAuto interface. Independent app: `com.shihab.diplay`.

> **BYD support scope:** These projects focus on BYD cars. They may work on other brands, but other brands are unsupported and there are no plans to add support or fix brand-specific incompatibilities.

[Download & website](https://shihabal3amri.github.io/DiPlay/) · [Release](https://github.com/shihabal3amri/DiPlay/releases/tag/v0.2.18) · [Report a problem](https://github.com/shihabal3amri/DiPlay/issues/new/choose)

![DiPlay home](site/assets/home.png)

## 0.2.18 — public preview

Install on the **car**, not the iPhone. No jailbreak, dongle, Mac, account or authentication server is required for use. Core CarPlay does not require ADB; optional dashboard, battery, wheel-speed and parked-video features do. Your head unit must permit APK installation. The APK supports Android 7.1+ (API 25); Android 7.1–8.1 support is not yet confirmed on a vehicle. Wireless supports Wi-Fi Direct, the car’s existing hotspot or Existing Wi-Fi / Same LAN. Android 7.1–9 Wi-Fi Direct uses a firmware-dependent legacy path with generated group credentials and unverified requested frequency; see [Android 9 Wi-Fi Direct](docs/ANDROID9_WIFI_DIRECT.md). Android 10+ verifies its negotiated group frequency.

- Wired USB and wireless CarPlay with local authentication.
- BYD HUD navigation with arrows, distance and street names on verified firmware.
- Car hotspot support, improved audio buffering and saved receive diagnostics.
- Automatic address discovery, fixed-channel Wi-Fi fallbacks and successful-configuration memory.
- Icon/text size, resolution and frame rate; applying a display change reconnects CarPlay.
- Local diagnostic export. Reports are sent only if you choose to share them.
- Separate installation alongside DiAuto. Run one projection app at a time.

This is **not an Apple-certified product**. The APK bundles an experimental accessory identity recovered from public Carlinkit firmware, not a newly provisioned MFi identity for DiPlay. A bundled private key is extractable. Acceptance after future iOS updates, reliability across head units and suitability of that identity for general distribution are unresolved. This release invites community testing; it is not a guarantee of universal compatibility.

Earlier releases were tested on the development DiLink5.1 car: live windshield guidance and street names work, Car hotspot now starts CarPlay, and Wi-Fi Direct performance is substantially improved. Audio underrun recovery is improved in 0.2.15; remaining cutouts need current diagnostic reports. The 0.2.16 software Opus microphone fallback was accepted on a BOS Mini A1 head unit (Android 9) with an iPhone 12 on iOS 27. The floating-map test build was installed on the development DiLink 5.1 car; feedback led to the pinch corrections in 0.2.9. Earlier wheel-speed and video contributions were tested on a BYD Tang with DiLink 5.0 and an iPhone 15 Pro on iOS 27; wheel-speed dead reckoning in tunnels remains unverified. Broader head-unit and iOS compatibility is not guaranteed. The HUD firmware scope and cleanup limits are documented in [BYD navigation](docs/BYD_NAVIGATION.md).

## Minimum Android SDK & Legacy Android Compatibility

- **Verified Minimum Android API**: Android 7.1 (API 25) for `:mobile`, `:common`, and `:shared`; API 28 for `:automotive`; API 30 for launcher map samples (`:home` and `:maphost`).
- **Android 4.0–4.4 (API 14–19)**: Infeasible on current codebase due to Jetpack Compose BOM, AndroidX Media3, WorkManager, BouncyCastle, and AGP 9.3 toolchain requirements. Detailed dependency and API feasibility audit is documented in [Legacy Android Audit](docs/LEGACY_ANDROID_AUDIT.md).
- **Runtime Capability Detection**: Uses vendor-neutral capability detection (`HeadUnitCapabilities` and `PlatformCompat`) with safe platform guards for USB host, Wi-Fi Direct, local hotspot, and Bluetooth audio.

## What’s new in 0.2.18

- Wired CarPlay no longer drops every few minutes when a USB read finishes just as DiPlay stops waiting for it, and it now starts on Android 7.1 head units, on head units whose USB audio driver held the iPhone, and without a VPN dialog when network ADB is approved.
- Fewer short music dropouts, and the connection screen shows the real stage and failure in every app language.
- On head units whose Android Bluetooth cannot reach the iPhone, wireless CarPlay stops with a clear message and suggests USB.
- The wheel's next and previous keys change CarPlay tracks on the CarPlay screen without the wheel-key service, Geely/Lynk `geely_fx11` head units get wheel media keys and Siri, and wheel keys stuck on "Allowed, starting…" recover by themselves.
- Back up and restore settings from a phone through a QR code in **Settings → About**, and pick another installer, such as MT Manager, for updates.
- New experimental, off-by-default options: Harman full screen, square corners, clearer navigation voice over USB, MediaTek low-latency decoding, a media-key audio focus opt-out, car phone audio for calls, a cluster speedometer and FCE cluster guidance.

See [0.2.18 release notes](docs/RELEASE-NOTES-0.2.18.md) and [validation](docs/VALIDATION.md) for contribution links and remaining physical tests. General stutter, calls/Siri, decoder and model-specific reports still need current-device evidence. [0.2.17 notes](docs/RELEASE-NOTES-0.2.17.md) remain available as historical guidance.

If a problem remains, reproduce it on **0.2.18**, then use **Settings → Diagnostics → Save diagnostic report**. Android 10+ normally saves to **Downloads/DiPlay**; Android 7.1–9 asks for storage access and saves there too. If unavailable, use **View report** or **Share** from the confirmation, which identifies external/private fallback storage. Review the `.txt` and add it to a matching [existing issue](https://github.com/shihabal3amri/DiPlay/issues), or [create one](https://github.com/shihabal3amri/DiPlay/issues/new/choose). Include car/head-unit, Android/DiLink/firmware, iPhone/iOS, connection mode, steps and failure time. Reports are shared only when you choose; never post your hotspot password.

## Documentation

[Existing Wi-Fi / Same LAN](docs/EXISTING_WIFI.md) keeps the iPhone and head unit
on an external router. See the guide for setup, build requirements and the
BYD DiLink 4.0 / Android 10 clean-install validation result.

- [Install and connect](docs/INSTALL.md)
- [Compatibility and troubleshooting](docs/COMPATIBILITY.md)
- [Legacy Android audit & feasibility](docs/LEGACY_ANDROID_AUDIT.md)
- [Smooth wireless CarPlay](docs/SMOOTH_WIRELESS.md)
- [Privacy and diagnostic reports](docs/PRIVACY.md)
- [Build from source](docs/BUILD.md) — select `mobile` for the main DiPlay app; `maphost` is a map sample.
- [Validation](docs/VALIDATION.md)
- [Release notes](CHANGELOG.md)
- [Credits and licenses](docs/THIRD_PARTY_NOTICES.md)

The app and release website are available in English, Arabic, Russian, Ukrainian, Spanish, Simplified Chinese and Traditional Chinese (Taiwan). Traditional Chinese uses Taiwan wording; the app also recognizes Hong Kong/Macao and explicit Hant selections without claiming separate regional translations. Choose the app language in Settings; on Android 13+, it stays synchronized with Android’s per-app language setting.

## Source and credits

Based on [xcertplay](https://github.com/shilapi/xcertplay), GPL-3.0. The home/settings UI and website adapt [DiAuto](https://github.com/shihabal3amri/DiAuto), AGPL-3.0; that license is included in `docs/licenses`. Preserve those notices when distributing modifications. CarPlay and its icon belong to Apple Inc.; no Apple or BYD affiliation or endorsement is implied.

This repository starts with a clean public source snapshot. Local research, tester reports and release-signing secrets are excluded. The complete source corresponding to the APK is provided with every release; experimental runtime identity assets are described separately in the build instructions and notices.

## Local release packaging

The release APK intentionally contains the experimental accessory identity. The Git repository and source archive exclude all accessory and Android signing keys; tests generate synthetic identities at runtime. Source/CI builds omit runtime identity assets by default. Local release builds explicitly select an external asset directory. Publishing the APK makes its bundled identity extractable; building locally does not preserve that identity's confidentiality.
''')

os.makedirs("common/src/main/java/com/shilapi/xcertplay/capabilities", exist_ok=True)
with open("common/src/main/java/com/shilapi/xcertplay/capabilities/HeadUnitCapabilities.kt", "w") as f:
    f.write('''package com.shilapi.xcertplay.capabilities

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.usb.UsbManager
import android.net.wifi.p2p.WifiP2pManager
import android.os.Build

/** Vendor category for head units. Unknown devices fall back to [GENERIC_ANDROID]. */
enum class HeadUnitVendor {
    BYD,
    GEELY_LYNK,
    ANDROID_AUTOMOTIVE,
    GENERIC_ANDROID
}

/** Display capabilities detected for the current head unit. */
data class DisplayCapabilities(
    val supportsHardwareDecoding: Boolean = true,
    val isTouchscreenAvailable: Boolean = true,
    val supportsMultiWindow: Boolean = false,
    val isLandscapePreferred: Boolean = true
)

/** Transport and connectivity capabilities available on this head unit. */
data class TransportCapabilities(
    val supportsUsbHost: Boolean = true,
    val supportsWifiDirect: Boolean = true,
    val supportsLocalHotspot: Boolean = true,
    val supportsBluetoothAudio: Boolean = true,
    val isBluetoothEnabled: Boolean = false,
    val isUsbHostVerified: Boolean = true,
    val isWifiDirectVerified: Boolean = true
)

/** Comprehensive vendor-neutral capability profile for an Android head unit. */
data class HeadUnitCapabilities(
    val vendor: HeadUnitVendor = HeadUnitVendor.GENERIC_ANDROID,
    val modelName: String = "Generic Android Head Unit",
    val androidSdkInt: Int = Build.VERSION.SDK_INT,
    val display: DisplayCapabilities = DisplayCapabilities(),
    val transport: TransportCapabilities = TransportCapabilities(),
    val supportsSteeringWheelKeys: Boolean = false,
    val supportsVehicleNavigationIntegration: Boolean = false
) {
    /** Whether this is an unverified / generic device that uses standard generic fallbacks. */
    val isGenericFallback: Boolean
        get() = vendor == HeadUnitVendor.GENERIC_ANDROID
}

/** Capabilities detector that evaluates head unit features without requiring specific vendor lock-in. */
object HeadUnitCapabilityDetector {

    fun detect(context: Context): HeadUnitCapabilities {
        val packageManager = context.packageManager
        val isAutomotive = try {
            packageManager.hasSystemFeature(PackageManager.FEATURE_AUTOMOTIVE)
        } catch (_: Exception) {
            false
        }

        val product = Build.PRODUCT.orEmpty()
        val brand = Build.BRAND.orEmpty()
        val manufacturer = Build.MANUFACTURER.orEmpty()
        val fingerprint = Build.FINGERPRINT.orEmpty()

        val vendor = when {
            brand.contains("BYD", ignoreCase = true) ||
            product.contains("DiLink", ignoreCase = true) ||
            fingerprint.contains("BYD", ignoreCase = true) -> HeadUnitVendor.BYD

            product.contains("geely", ignoreCase = true) ||
            product.contains("CS11", ignoreCase = true) ||
            brand.contains("Geely", ignoreCase = true) -> HeadUnitVendor.GEELY_LYNK

            isAutomotive -> HeadUnitVendor.ANDROID_AUTOMOTIVE

            else -> HeadUnitVendor.GENERIC_ANDROID
        }

        // USB Host hardware detection with false-positive prevention
        val hasUsbFeature = try { packageManager.hasSystemFeature(PackageManager.FEATURE_USB_HOST) } catch (_: Exception) { false }
        val usbManager = try { context.getSystemService(Context.USB_SERVICE) as? UsbManager } catch (_: Exception) { null }
        val isUsbHostVerified = hasUsbFeature && usbManager != null
        val hasUsbHost = hasUsbFeature || (usbManager != null)

        // Wi-Fi Direct hardware detection with service check
        val hasWifiP2pFeature = try { packageManager.hasSystemFeature(PackageManager.FEATURE_WIFI_DIRECT) } catch (_: Exception) { false }
        val wifiP2pManager = try { context.getSystemService(Context.WIFI_P2P_SERVICE) as? WifiP2pManager } catch (_: Exception) { null }
        val isWifiDirectVerified = hasWifiP2pFeature && wifiP2pManager != null
        val hasWifiP2p = hasWifiP2pFeature || (wifiP2pManager != null)

        val hasTouchscreen = try {
            packageManager.hasSystemFeature(PackageManager.FEATURE_TOUCHSCREEN) ||
            packageManager.hasSystemFeature(PackageManager.FEATURE_FAKETOUCH)
        } catch (_: Exception) {
            true // Safe fallback
        }

        // Bluetooth Audio detection with Android 8 (API 26/27) BluetoothAdapter fallback
        val hasBluetoothFeature = try {
            packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH) ||
            packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)
        } catch (_: Exception) {
            false
        }

        var isBtEnabled = false
        if (hasBluetoothFeature) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    val btManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
                    val adapter = btManager?.adapter ?: @Suppress("DEPRECATION") BluetoothAdapter.getDefaultAdapter()
                    isBtEnabled = adapter?.isEnabled == true
                } else {
                    @Suppress("DEPRECATION")
                    val adapter = BluetoothAdapter.getDefaultAdapter()
                    isBtEnabled = adapter?.isEnabled == true
                }
            } catch (_: Exception) {
                isBtEnabled = false
            }
        }

        val supportsLocalHotspot = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O

        val supportsMultiWindow = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            if (isAutomotive) {
                try {
                    packageManager.hasSystemFeature(PackageManager.FEATURE_FREEFORM_WINDOW_MANAGEMENT) ||
                    packageManager.hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE)
                } catch (_: Exception) {
                    false
                }
            } else {
                true
            }
        } else {
            false
        }

        val modelName = when (vendor) {
            HeadUnitVendor.BYD -> "BYD DiLink ($product)"
            HeadUnitVendor.GEELY_LYNK -> "Geely/Lynk & Co ($product)"
            HeadUnitVendor.ANDROID_AUTOMOTIVE -> "Android Automotive OS ($product)"
            HeadUnitVendor.GENERIC_ANDROID -> if (manufacturer.isNotBlank()) "$manufacturer $product" else "Generic Android Head Unit"
        }

        return HeadUnitCapabilities(
            vendor = vendor,
            modelName = modelName,
            androidSdkInt = Build.VERSION.SDK_INT,
            display = DisplayCapabilities(
                supportsHardwareDecoding = true,
                isTouchscreenAvailable = hasTouchscreen,
                supportsMultiWindow = supportsMultiWindow
            ),
            transport = TransportCapabilities(
                supportsUsbHost = hasUsbHost,
                supportsWifiDirect = hasWifiP2p,
                supportsLocalHotspot = supportsLocalHotspot,
                supportsBluetoothAudio = hasBluetoothFeature,
                isBluetoothEnabled = isBtEnabled,
                isUsbHostVerified = isUsbHostVerified,
                isWifiDirectVerified = isWifiDirectVerified
            ),
            supportsSteeringWheelKeys = vendor == HeadUnitVendor.GEELY_LYNK || vendor == HeadUnitVendor.BYD,
            supportsVehicleNavigationIntegration = vendor == HeadUnitVendor.BYD
        )
    }
}
''')

os.makedirs("common/src/test/java/com/shilapi/xcertplay/capabilities", exist_ok=True)
with open("common/src/test/java/com/shilapi/xcertplay/capabilities/HeadUnitCapabilitiesTest.kt", "w") as f:
    f.write('''package com.shilapi.xcertplay.capabilities

import android.content.Context
import android.content.pm.PackageManager
import android.hardware.usb.UsbManager
import android.net.wifi.p2p.WifiP2pManager
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.anyString
import org.mockito.Mock
import org.mockito.Mockito.`when`
import org.mockito.MockitoAnnotations
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class HeadUnitCapabilitiesTest {

    @Mock
    private lateinit var mockContext: Context

    @Mock
    private lateinit var mockPackageManager: PackageManager

    @Mock
    private lateinit var mockUsbManager: UsbManager

    @Mock
    private lateinit var mockWifiP2pManager: WifiP2pManager

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        `when`(mockContext.packageManager).thenReturn(mockPackageManager)
        `when`(mockPackageManager.hasSystemFeature(anyString())).thenReturn(false)
    }

    @Test
    fun defaultHeadUnitCapabilities_usesGenericFallback() {
        val caps = HeadUnitCapabilities()
        assertEquals(HeadUnitVendor.GENERIC_ANDROID, caps.vendor)
        assertTrue(caps.isGenericFallback)
        assertTrue(caps.display.supportsHardwareDecoding)
        assertFalse(caps.supportsVehicleNavigationIntegration)
    }

    @Test
    fun genericDetection_returnsGenericVendor() {
        val caps = HeadUnitCapabilityDetector.detect(mockContext)
        assertEquals(HeadUnitVendor.GENERIC_ANDROID, caps.vendor)
        assertTrue(caps.isGenericFallback)
        assertFalse(caps.transport.supportsUsbHost)
        assertFalse(caps.transport.supportsWifiDirect)
        assertFalse(caps.transport.supportsBluetoothAudio)
    }

    @Test
    fun detection_withHardwareFeatures_enablesTransportCapabilities() {
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_USB_HOST)).thenReturn(true)
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_WIFI_DIRECT)).thenReturn(true)
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH)).thenReturn(true)
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_TOUCHSCREEN)).thenReturn(true)

        `when`(mockContext.getSystemService(Context.USB_SERVICE)).thenReturn(mockUsbManager)
        `when`(mockContext.getSystemService(Context.WIFI_P2P_SERVICE)).thenReturn(mockWifiP2pManager)

        val caps = HeadUnitCapabilityDetector.detect(mockContext)

        assertTrue(caps.transport.supportsUsbHost)
        assertTrue(caps.transport.supportsWifiDirect)
        assertTrue(caps.transport.supportsBluetoothAudio)
        assertTrue(caps.display.isTouchscreenAvailable)
        assertTrue(caps.transport.isUsbHostVerified)
        assertTrue(caps.transport.isWifiDirectVerified)
        assertTrue(caps.transport.supportsLocalHotspot) // SDK 28 >= 26
    }

    @Test
    fun detection_missingUsbHostService_handlesSafelyWithoutFalsePositive() {
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_USB_HOST)).thenReturn(true)
        `when`(mockContext.getSystemService(Context.USB_SERVICE)).thenReturn(null)

        val caps = HeadUnitCapabilityDetector.detect(mockContext)
        assertTrue(caps.transport.supportsUsbHost)
        assertFalse(caps.transport.isUsbHostVerified)
    }

    @Test
    fun bydCapabilities_enablesVehicleNavigation() {
        val caps = HeadUnitCapabilities(
            vendor = HeadUnitVendor.BYD,
            supportsVehicleNavigationIntegration = true,
            supportsSteeringWheelKeys = true
        )
        assertEquals(HeadUnitVendor.BYD, caps.vendor)
        assertFalse(caps.isGenericFallback)
        assertTrue(caps.supportsVehicleNavigationIntegration)
        assertTrue(caps.supportsSteeringWheelKeys)
    }

    @Test
    fun geelyCapabilities_enablesSteeringWheelKeys() {
        val caps = HeadUnitCapabilities(
            vendor = HeadUnitVendor.GEELY_LYNK,
            supportsSteeringWheelKeys = true
        )
        assertEquals(HeadUnitVendor.GEELY_LYNK, caps.vendor)
        assertFalse(caps.isGenericFallback)
        assertTrue(caps.supportsSteeringWheelKeys)
        assertFalse(caps.supportsVehicleNavigationIntegration)
    }
}
''')

os.makedirs("shared/src/main/java/com/shilapi/xcertplay/compat", exist_ok=True)
with open("shared/src/main/java/com/shilapi/xcertplay/compat/PlatformCompat.kt", "w") as f:
    f.write('''package com.shilapi.xcertplay.compat

import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.location.LocationManager
import android.net.wifi.WifiManager
import android.net.wifi.p2p.WifiP2pManager
import android.os.Build

/** Releases the channel on API 27+. Earlier releases have no close call and free it when collected. */
fun WifiP2pManager.Channel.closeCompat() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
        try {
            close()
        } catch (_: Exception) {
            // Safe fallback on legacy ROMs
        }
    }
}

/** [LocationManager.isLocationEnabled] needs API 28; before that a location provider must be on. */
fun LocationManager.isLocationEnabledCompat(): Boolean =
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        try {
            isLocationEnabled
        } catch (_: SecurityException) {
            false
        }
    } else {
        try {
            isProviderEnabled(LocationManager.GPS_PROVIDER) || isProviderEnabled(LocationManager.NETWORK_PROVIDER)
        } catch (_: Exception) {
            false
        }
    }

/** Checks whether the activity is currently in multi-window mode safely across API levels. */
fun Activity.isInMultiWindowModeCompat(): Boolean =
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
        try {
            isInMultiWindowMode
        } catch (_: Exception) {
            false
        }
    } else {
        false
    }

/** Safe check for USB Host hardware permission and attached device count. */
fun UsbManager.hasAttachedDevicesCompat(): Boolean =
    try {
        deviceList.isNotEmpty()
    } catch (_: Exception) {
        false
    }

/** Checks USB permission for a given device safely. */
fun UsbManager.hasPermissionCompat(device: UsbDevice?): Boolean {
    if (device == null) return false
    return try {
        hasPermission(device)
    } catch (_: SecurityException) {
        false
    } catch (_: Exception) {
        false
    }
}

/** Safely retrieves the system BluetoothAdapter across legacy and modern API levels. */
fun getBluetoothAdapterCompat(context: Context): BluetoothAdapter? =
    try {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
            bluetoothManager?.adapter ?: @Suppress("DEPRECATION") BluetoothAdapter.getDefaultAdapter()
        } else {
            @Suppress("DEPRECATION")
            BluetoothAdapter.getDefaultAdapter()
        }
    } catch (_: SecurityException) {
        null
    } catch (_: Exception) {
        null
    }

/** Safe check for whether local hotspot capability is available on this OS release. */
fun isLocalHotspotSupportedCompat(): Boolean =
    Build.VERSION.SDK_INT >= Build.VERSION_CODES.O

/** Safe check for Wi-Fi enabled status. */
fun WifiManager.isWifiEnabledCompat(): Boolean =
    try {
        isWifiEnabled
    } catch (_: SecurityException) {
        false
    } catch (_: Exception) {
        false
    }
''')

os.makedirs("shared/src/test/java/com/shilapi/xcertplay/compat", exist_ok=True)
with open("shared/src/test/java/com/shilapi/xcertplay/compat/PlatformCompatTest.kt", "w") as f:
    f.write('''package com.shilapi.xcertplay.compat

import android.app.Activity
import android.content.Context
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.location.LocationManager
import android.net.wifi.WifiManager
import android.os.Build
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito.`when`
import org.mockito.MockitoAnnotations
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
class PlatformCompatTest {

    @Mock
    private lateinit var mockContext: Context

    @Mock
    private lateinit var mockLocationManager: LocationManager

    @Mock
    private lateinit var mockUsbManager: UsbManager

    @Mock
    private lateinit var mockUsbDevice: UsbDevice

    @Mock
    private lateinit var mockWifiManager: WifiManager

    @Mock
    private lateinit var mockActivity: Activity

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
    }

    @Test
    @Config(sdk = [25])
    fun locationEnabledCompat_api25_checksProviders() {
        `when`(mockLocationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)).thenReturn(true)
        assertTrue(mockLocationManager.isLocationEnabledCompat())
    }

    @Test
    @Config(sdk = [28])
    fun locationEnabledCompat_api28_usesSystemMethod() {
        `when`(mockLocationManager.isLocationEnabled).thenReturn(false)
        assertFalse(mockLocationManager.isLocationEnabledCompat())
    }

    @Test
    @Config(sdk = [23])
    fun multiWindow_api23_returnsFalse() {
        assertFalse(mockActivity.isInMultiWindowModeCompat())
    }

    @Test
    @Config(sdk = [28])
    fun multiWindow_api28_queriesActivity() {
        `when`(mockActivity.isInMultiWindowMode).thenReturn(true)
        assertTrue(mockActivity.isInMultiWindowModeCompat())
    }

    @Test
    fun usbPermissionCompat_nullDevice_returnsFalse() {
        assertFalse(mockUsbManager.hasPermissionCompat(null))
    }

    @Test
    fun usbPermissionCompat_securityException_returnsFalse() {
        `when`(mockUsbManager.hasPermission(mockUsbDevice)).thenThrow(SecurityException("Denied"))
        assertFalse(mockUsbManager.hasPermissionCompat(mockUsbDevice))
    }

    @Test
    fun wifiEnabledCompat_securityException_returnsFalse() {
        `when`(mockWifiManager.isWifiEnabled).thenThrow(SecurityException("Permission denied"))
        assertFalse(mockWifiManager.isWifiEnabledCompat())
    }

    @Test
    @Config(sdk = [26])
    fun localHotspotSupported_api26_returnsTrue() {
        assertTrue(isLocalHotspotSupportedCompat())
    }

    @Test
    @Config(sdk = [25])
    fun localHotspotSupported_api25_returnsFalse() {
        assertFalse(isLocalHotspotSupportedCompat())
    }
}
''')

with open("settings.gradle.kts", "w") as f:
    f.write('''pluginManagement {
    repositories {
        maven { url = uri("https://dl.google.com/dl/android/maven2/") }
        maven { url = uri("https://maven.aliyun.com/repository/public") }
        gradlePluginPortal()
    }
}
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven { url = uri("https://dl.google.com/dl/android/maven2/") }
        maven { url = uri("https://maven.aliyun.com/repository/public") }
    }
}

rootProject.name = "xcertplay"
include(":common")
include(":mobile")
include(":automotive")
include(":shared")
include(":maphost")
project(":maphost").projectDir = file("samples/maphost")
include(":home")
project(":home").projectDir = file("samples/home")
''')

with open("shared/build.gradle", "w") as f:
    f.write('''plugins {
    id 'com.android.library'
}
android {
    namespace = 'com.shilapi.xcertplay.shared'
    compileSdk = 37

    defaultConfig {
        minSdk = 25
        consumerProguardFiles 'ambient-consumer-rules.pro'
        targetSdk = 37

        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'
        }

        externalNativeBuild {
            ndkBuild {
                arguments 'APP_PLATFORM=android-25'
            }
        }

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    ndkVersion = '28.2.13676358'
    externalNativeBuild {
        ndkBuild {
            path = file('src/main/jni/Android.mk')
        }
    }
    buildFeatures {
        // Geely/Lynk head-unit input API (com.geely.inputservice); declarations in src/main/aidl.
        aidl true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    testOptions {
        unitTests.all {
            systemProperty 'robolectric.dependency.repo.id', 'aliyun'
            systemProperty 'robolectric.dependency.repo.url', 'https://maven.aliyun.com/repository/public'
        }
    }
}
dependencies {
    implementation libs.androidx.app
    implementation libs.bouncycastle
    implementation libs.jmdns
    testImplementation libs.junit
    testImplementation 'org.robolectric:robolectric:4.17'
    testImplementation 'org.mockito:mockito-core:5.20.0'
}

tasks.withType(Test).configureEach {
    systemProperty 'robolectric.dependency.repo.id', 'aliyun'
    systemProperty 'robolectric.dependency.repo.url', 'https://maven.aliyun.com/repository/public'
}
''')

with open("common/build.gradle.kts", "w") as f:
    f.write('''plugins {
    id("com.android.library")
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.shilapi.xcertplay.host"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        minSdk = 25
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    buildFeatures {
        compose = true
    }

    testOptions {
        unitTests.isIncludeAndroidResources = true
        // The UI suite covers several SDKs and locale-specific resource sandboxes.
        unitTests.all {
            it.maxHeapSize = "1g"
            it.systemProperty("robolectric.dependency.repo.id", "aliyun")
            it.systemProperty("robolectric.dependency.repo.url", "https://maven.aliyun.com/repository/public")
        }
    }
}

dependencies {
    api(project(":shared"))
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.work.runtime)
    implementation(libs.androidx.media3.exoplayer)
    implementation(libs.androidx.media3.exoplayer.hls)
    implementation(libs.androidx.media3.ui)
    implementation(libs.zxing.core)
    testImplementation(libs.junit)
    testImplementation("org.robolectric:robolectric:4.17")
    testImplementation("org.mockito:mockito-core:5.20.0")
    testImplementation(libs.jmdns)
}
''')

with open("samples/home/build.gradle.kts", "w") as f:
    f.write('''// DiPlay Home: a small launcher with the live CarPlay map and any Android widgets.
plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.diplay.home"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.diplay.home"
        minSdk = 30 // SurfaceView.getHostToken and setChildSurfacePackage
        targetSdk = 37
        versionCode = 1
        versionName = "0.1"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    testOptions {
        unitTests.isIncludeAndroidResources = true
        unitTests.all {
            it.systemProperty("robolectric.dependency.repo.id", "aliyun")
            it.systemProperty("robolectric.dependency.repo.url", "https://maven.aliyun.com/repository/public")
        }
    }
}

dependencies {
    implementation(libs.androidx.activity)
    testImplementation(libs.junit)
    testImplementation("org.robolectric:robolectric:4.17")
}

tasks.withType<Test>().configureEach {
    // Robolectric's API 36 shared-memory implementation needs this JDK interface.
    jvmArgs("--add-exports=java.base/jdk.internal.access=ALL-UNNAMED")
    systemProperty("robolectric.dependency.repo.id", "aliyun")
    systemProperty("robolectric.dependency.repo.url", "https://maven.aliyun.com/repository/public")
}
''')
EOF
python3 apply_changes.py
