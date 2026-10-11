# DiPlay Legacy Android Compatibility Audit & Feasibility Assessment

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
                      |     ConnectionStateMachine       |
                      |  & CarPlay Orchestration Logic   |
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

1. **Shared State & Business Logic**: All connection state, AirPlay socket handling, audio/video pipelines, and HUD integrations remain in `:shared` and `:common` state holders (`ConnectionStateMachine`, `HeadUnitCapabilities`, `PlatformCompat`).
2. **UI Abstraction Interface**: Introduce a `UiRenderer` interface exposing `renderState(state: ConnectionState)` and `onAction(action: UiAction)`.
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
