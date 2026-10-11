package com.shilapi.xcertplay.compat

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
