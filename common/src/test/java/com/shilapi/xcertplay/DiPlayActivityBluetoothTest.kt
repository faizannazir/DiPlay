package com.shilapi.xcertplay

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.os.Looper
import com.shilapi.xcertplay.host.R
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import org.robolectric.shadows.ShadowAlertDialog

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [29], manifest = Config.NONE)
class DiPlayActivityBluetoothTest {

    private fun callChoosePhone(activity: DiPlayActivity) {
        val method = DiPlayActivity::class.java.getDeclaredMethod("choosePhone")
        method.isAccessible = true
        method.invoke(activity)
        shadowOf(Looper.getMainLooper()).idle()
    }

    @Test
    fun disabledBluetoothAdapterShowsTurnOnBluetoothDialog() {
        val adapter = BluetoothAdapter.getDefaultAdapter()
        assertNotNull(adapter)
        shadowOf(adapter).setState(BluetoothAdapter.STATE_OFF)

        val activity = Robolectric.buildActivity(DiPlayActivity::class.java).create().get()
        callChoosePhone(activity)

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNotNull(dialog)
        val shadowDialog = shadowOf(dialog)
        assertEquals(activity.getString(R.string.turn_on_bluetooth), shadowDialog.title)
        assertEquals(activity.getString(R.string.enable_the_car_s_bluetooth_and_pair_your_iphone_first), shadowDialog.message)
    }

    @Test
    fun enabledBluetoothAdapterWithNoPairedDevicesShowsPairIphoneDialog() {
        val adapter = BluetoothAdapter.getDefaultAdapter()
        assertNotNull(adapter)
        shadowOf(adapter).setState(BluetoothAdapter.STATE_ON)
        shadowOf(adapter).setBondedDevices(emptySet())

        val activity = Robolectric.buildActivity(DiPlayActivity::class.java).create().get()
        callChoosePhone(activity)

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNotNull(dialog)
        val shadowDialog = shadowOf(dialog)
        assertEquals(activity.getString(R.string.pair_your_iphone), shadowDialog.title)
        assertEquals(activity.getString(R.string.on_your_iphone_open_settings_bluetooth_and_pair_with_the_c), shadowDialog.message)
    }

    @Test
    fun enabledBluetoothAdapterWithPairedDevicesShowsChooseIphoneDialog() {
        val adapter = BluetoothAdapter.getDefaultAdapter()
        assertNotNull(adapter)
        shadowOf(adapter).setState(BluetoothAdapter.STATE_ON)
        val device = adapter.getRemoteDevice("11:22:33:44:55:66")
        shadowOf(adapter).setBondedDevices(setOf(device))

        val activity = Robolectric.buildActivity(DiPlayActivity::class.java).create().get()
        callChoosePhone(activity)

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNotNull(dialog)
        val shadowDialog = shadowOf(dialog)
        assertEquals(activity.getString(R.string.choose_your_iphone), shadowDialog.title)
    }

    @Test
    @Config(shadows = [NullBluetoothAdapterShadow::class])
    fun missingBluetoothAdapterShowsUnusableGuidance() {
        val activity = Robolectric.buildActivity(DiPlayActivity::class.java).create().get()

        callChoosePhone(activity)

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNotNull(dialog)
        val shadowDialog = shadowOf(dialog)
        assertEquals(activity.getString(R.string.turn_on_bluetooth), shadowDialog.title)
        assertEquals(activity.getString(R.string.connection_help_bluetooth_unusable), shadowDialog.message)
    }

    @Test
    @Config(sdk = [31])
    fun bluetoothConnectPermissionRequestedOnAndroid12WhenNotGranted() {
        val activity = Robolectric.buildActivity(DiPlayActivity::class.java).create().get()
        shadowOf(activity).denyPermissions(Manifest.permission.BLUETOOTH_CONNECT)

        callChoosePhone(activity)

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        assertNull(dialog)
    }

    @Implements(BluetoothAdapter::class)
    class NullBluetoothAdapterShadow {
        companion object {
            @JvmStatic
            @Implementation
            fun getDefaultAdapter(): BluetoothAdapter? = null
        }
    }
}
