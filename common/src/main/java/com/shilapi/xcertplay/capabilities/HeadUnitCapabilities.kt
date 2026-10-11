package com.shilapi.xcertplay.capabilities

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
        val isAutomotive = packageManager.hasSystemFeature(PackageManager.FEATURE_AUTOMOTIVE)

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

        // Hardware feature checks with system feature guard & service availability check
        val hasUsbFeature = packageManager.hasSystemFeature(PackageManager.FEATURE_USB_HOST)
        val usbManager = try { context.getSystemService(Context.USB_SERVICE) as? UsbManager } catch (_: Exception) { null }
        val hasUsbHost = hasUsbFeature || (usbManager != null)

        val hasWifiP2pFeature = packageManager.hasSystemFeature(PackageManager.FEATURE_WIFI_DIRECT)
        val wifiP2pManager = try { context.getSystemService(Context.WIFI_P2P_SERVICE) as? WifiP2pManager } catch (_: Exception) { null }
        val hasWifiP2p = hasWifiP2pFeature || (wifiP2pManager != null)

        val hasTouchscreen = packageManager.hasSystemFeature(PackageManager.FEATURE_TOUCHSCREEN) ||
            packageManager.hasSystemFeature(PackageManager.FEATURE_FAKETOUCH)

        val hasBluetoothFeature = packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH)
        var isBtEnabled = false
        if (hasBluetoothFeature) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    val btManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
                    isBtEnabled = btManager?.adapter?.isEnabled == true
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

        val supportsMultiWindow = Build.VERSION.SDK_INT >= Build.VERSION_CODES.N &&
            (!isAutomotive || packageManager.hasSystemFeature(PackageManager.FEATURE_FREEFORM_WINDOW_MANAGEMENT) ||
             packageManager.hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE))

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
                isUsbHostVerified = hasUsbFeature && usbManager != null,
                isWifiDirectVerified = hasWifiP2pFeature && wifiP2pManager != null
            ),
            supportsSteeringWheelKeys = vendor == HeadUnitVendor.GEELY_LYNK || vendor == HeadUnitVendor.BYD,
            supportsVehicleNavigationIntegration = vendor == HeadUnitVendor.BYD
        )
    }
}
