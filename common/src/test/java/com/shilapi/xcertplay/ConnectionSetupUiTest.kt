package com.shilapi.xcertplay

import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Looper
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import com.shilapi.xcertplay.host.R
import com.shilapi.xcertplay.orchestration.WirelessHotspotMode
import java.io.File
import java.util.Locale
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowAlertDialog

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [29], qualifiers = "en-w1000dp-h700dp-land")
class ConnectionSetupUiTest {
    private val context: Context = RuntimeEnvironment.getApplication()
    private var activity: DiPlayActivity? = null

    @Before
    fun setUp() {
        clearSettings()
    }

    @After
    fun tearDown() {
        activity?.finish()
        AppAppearanceRuntime.resetForTest()
        clearSettings()
    }

    private fun clearSettings() {
        context.getSharedPreferences("diplay", 0).edit().clear().commit()
        context.getSharedPreferences("xcertplay_airplay", 0).edit().clear().commit()
    }

    private fun openSetup(): DiPlayActivity = Robolectric.buildActivity(
        DiPlayActivity::class.java,
        Intent(context, DiPlayActivity::class.java).putExtra("page", "connection"),
    ).setup().get().also { activity = it }

    private fun texts(screen: DiPlayActivity): List<String> =
        descendants(screen.window.decorView).filterIsInstance<TextView>().map { it.text.toString() }.toList()

    private fun descendants(view: View): Sequence<View> = sequence {
        yield(view)
        if (view is ViewGroup) for (index in 0 until view.childCount) yieldAll(descendants(view.getChildAt(index)))
    }

    @Test
    fun selectingConnectionMethodUpdatesPersistenceAndRefreshesGuidedSteps() {
        val screen = openSetup()

        // Default mode is Hotspot (MANUAL)
        assertTrue(AirPlayPersistence.loadWirelessEnabled(context))
        assertEquals(WirelessHotspotMode.MANUAL, AirPlayPersistence.loadWirelessHotspotMode(context))

        // Select USB Cable
        val usbBtn = descendants(screen.window.decorView).filterIsInstance<Button>()
            .single { it.text.contains(screen.getString(R.string.settings_usb_connection_method)) }
        usbBtn.performClick()
        shadowOf(Looper.getMainLooper()).idle()

        assertFalse(AirPlayPersistence.loadWirelessEnabled(context))
        assertTrue(texts(screen).any { it.contains(screen.getString(R.string.review_app_permissions)) })

        // Select Wi-Fi Direct
        val p2pBtn = descendants(screen.window.decorView).filterIsInstance<Button>()
            .single { it.text.contains(screen.getString(R.string.wifi_direct)) }
        p2pBtn.performClick()
        shadowOf(Looper.getMainLooper()).idle()

        assertTrue(AirPlayPersistence.loadWirelessEnabled(context))
        assertEquals(WirelessHotspotMode.WIFI_P2P, AirPlayPersistence.loadWirelessHotspotMode(context))
        assertTrue(texts(screen).any { it.contains(screen.getString(R.string.wifi_direct)) })
    }

    @Test
    fun hotspotCredentialsMissingVsSavedStateAndPasswordIsHidden() {
        val screen = openSetup()
        val shownMissing = texts(screen)
        assertTrue(shownMissing.toString(), screen.getString(R.string.finish_setup_save_your_hotspot_details_to_use_this_mode) in shownMissing)

        // Save hotspot details
        AirPlayPersistence.saveManualHotspotSsid(context, "CarHotspot5G")
        AirPlayPersistence.saveManualHotspotPassphrase(context, "SecretPass123")

        Robolectric.buildActivity(
            DiPlayActivity::class.java,
            Intent(context, DiPlayActivity::class.java).putExtra("page", "connection"),
        ).setup().get().also {
            val shownSaved = texts(it)
            assertTrue(shownSaved.toString(), shownSaved.any { text -> text.contains("CarHotspot5G") })
            assertTrue(shownSaved.toString(), shownSaved.any { text -> text.startsWith(it.getString(R.string.edit_saved_hotspot_prefix)) })
            // Password must NOT be exposed on screen
            assertFalse(shownSaved.toString(), shownSaved.any { text -> text.contains("SecretPass123") })
            it.finish()
        }
    }

    @Test
    fun credentialValidationErrorsPreventSavingInDialog() {
        val screen = openSetup()
        val editBtn = descendants(screen.window.decorView).filterIsInstance<Button>()
            .first { it.text.contains(screen.getString(R.string.save_hotspot_details_and_use_this_mode)) }
        editBtn.performClick()
        shadowOf(Looper.getMainLooper()).idle()

        val dialog = ShadowAlertDialog.getLatestAlertDialog()
        val inputs = descendants(dialog.window!!.decorView).filterIsInstance<EditText>().toList()

        // Enter invalid short password (< 8 chars)
        inputs[0].setText("MyCarHotspot")
        inputs[1].setText("123") // too short
        dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).performClick()
        shadowOf(Looper.getMainLooper()).idle()

        // Dialog should remain showing due to validation error
        assertTrue(dialog.isShowing)

        // Enter valid password
        inputs[1].setText("12345678")
        dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).performClick()
        shadowOf(Looper.getMainLooper()).idle()

        assertFalse(dialog.isShowing)
        assertEquals("MyCarHotspot", AirPlayPersistence.loadManualHotspotSsid(context))
        assertEquals("12345678", AirPlayPersistence.loadManualHotspotPassphrase(context))
    }

    @Test
    fun backNavigationReturnsToPreviousPage() {
        val screen = openSetup()
        val backBtn = descendants(screen.window.decorView).filterIsInstance<Button>()
            .single { it.text == screen.getString(R.string.back) }
        backBtn.performClick()
        shadowOf(Looper.getMainLooper()).idle()

        // Returned to Home page
        assertEquals("home", org.robolectric.util.ReflectionHelpers.getField<String>(screen, "page"))
    }

    @Test
    fun capturesScreenshotsInCompactFullAndArabicRtlLayouts() {
        val dir = File("build/reports/connection-setup-ui").apply { mkdirs() }

        // 1. Compact layout
        val compactConfig = Configuration(context.resources.configuration).apply {
            screenWidthDp = 480
            screenHeightDp = 320
            densityDpi = 160
            fontScale = 1.0f
        }
        val compactContext = context.createConfigurationContext(compactConfig)
        val compactScreen = Robolectric.buildActivity(
            DiPlayActivity::class.java,
            Intent(compactContext, DiPlayActivity::class.java).putExtra("page", "connection"),
        ).setup().get()

        layoutAndCapture(compactScreen, File(dir, "compact_setup.png"))
        compactScreen.finish()

        // 2. Full layout with large font scale
        val fullConfig = Configuration(context.resources.configuration).apply {
            screenWidthDp = 1000
            screenHeightDp = 700
            fontScale = 1.3f
        }
        val fullContext = context.createConfigurationContext(fullConfig)
        val fullScreen = Robolectric.buildActivity(
            DiPlayActivity::class.java,
            Intent(fullContext, DiPlayActivity::class.java).putExtra("page", "connection"),
        ).setup().get()

        layoutAndCapture(fullScreen, File(dir, "full_setup_large_font.png"))
        fullScreen.finish()

        // 3. Arabic (RTL) layout
        val rtlConfig = Configuration(context.resources.configuration).apply {
            screenWidthDp = 900
            screenHeightDp = 600
            setLocale(Locale.forLanguageTag("ar"))
            fontScale = 1.1f
        }
        val rtlContext = context.createConfigurationContext(rtlConfig)
        val rtlScreen = Robolectric.buildActivity(
            DiPlayActivity::class.java,
            Intent(rtlContext, DiPlayActivity::class.java).putExtra("page", "connection"),
        ).setup().get()

        layoutAndCapture(rtlScreen, File(dir, "arabic_rtl_setup.png"))
        rtlScreen.finish()

        assertTrue(File(dir, "compact_setup.png").exists())
        assertTrue(File(dir, "full_setup_large_font.png").exists())
        assertTrue(File(dir, "arabic_rtl_setup.png").exists())
    }

    private fun layoutAndCapture(screen: DiPlayActivity, outputFile: File) {
        val root = screen.findViewById<ViewGroup>(android.R.id.content).getChildAt(0)
        root.measure(
            View.MeasureSpec.makeMeasureSpec(screen.resources.displayMetrics.widthPixels, View.MeasureSpec.EXACTLY),
            View.MeasureSpec.makeMeasureSpec(screen.resources.displayMetrics.heightPixels, View.MeasureSpec.EXACTLY),
        )
        root.layout(0, 0, root.measuredWidth, root.measuredHeight)
        val bitmap = Bitmap.createBitmap(root.width.coerceAtLeast(100), root.height.coerceAtLeast(100), Bitmap.Config.ARGB_8888)
        try {
            root.draw(Canvas(bitmap))
            outputFile.outputStream().use { stream ->
                assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream))
            }
        } finally {
            bitmap.recycle()
        }
    }
}
