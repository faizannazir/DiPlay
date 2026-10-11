package com.shilapi.xcertplay.compat

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
            bluetoothManager?.adapter
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
