package com.shilapi.xcertplay.capabilities

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
    fun detection_missingUsbHostService_handlesSafely() {
        `when`(mockPackageManager.hasSystemFeature(PackageManager.FEATURE_USB_HOST)).thenReturn(false)
        `when`(mockContext.getSystemService(Context.USB_SERVICE)).thenReturn(null)

        val caps = HeadUnitCapabilityDetector.detect(mockContext)
        assertFalse(caps.transport.supportsUsbHost)
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
