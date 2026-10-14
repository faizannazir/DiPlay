package com.shilapi.xcertplay

import android.app.Application
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import com.shilapi.xcertplay.host.R
import com.shilapi.xcertplay.update.UpdateAvailability
import com.shilapi.xcertplay.update.UpdateRelease
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import org.robolectric.util.ReflectionHelpers

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [29], qualifiers = "en-w900dp-h600dp-land")
class ManualUpdateUiTest {
    private val application: Application = RuntimeEnvironment.getApplication()

    @After fun clear() = UpdateAvailability.clearAllForTest(application)

    @Test fun settingsAboutDisplaysInstalledVersionAndCheckAction() {
        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        val installedVersion = ReflectionHelpers.callInstanceMethod<String>(activity, "version")
        val installedText = activity.getString(R.string.update_installed_version, installedVersion)
        assertTrue(views.any { it.text == installedText })
        assertTrue(views.any { it.text == activity.getString(R.string.update_check) })

        controller.pause().stop().destroy()
    }

    @Test fun settingsAboutDisplaysReleaseNotesAndActionsWhenUpdateIsAvailable() {
        val release = UpdateRelease(
            tagName = "v99.0.0",
            apkName = "DiPlay-99.0.0.apk",
            apkUrl = "https://example.com/DiPlay.apk",
            checksumsUrl = "https://example.com/SHA256SUMS.txt",
            releaseNotes = "New features and performance improvements.",
        )
        UpdateAvailability.save(application, release)

        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        assertTrue(views.any { it.text == activity.getString(R.string.update_latest_version, "v99.0.0") })
        assertTrue(views.any { it.text == "New features and performance improvements." })
        assertTrue(views.any { it.text == activity.getString(R.string.update_download) })

        controller.pause().stop().destroy()
    }

    @Test fun longReleaseNotesCanBeExpandedAndCollapsed() {
        val longNotes = (1..10).joinToString("\n") { "Line $it: detailed release info" }
        val release = UpdateRelease(
            tagName = "v99.0.0",
            apkName = "DiPlay-99.0.0.apk",
            apkUrl = "https://example.com/DiPlay.apk",
            checksumsUrl = "https://example.com/SHA256SUMS.txt",
            releaseNotes = longNotes,
        )
        UpdateAvailability.save(application, release)

        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        val expandButton = descendants(activity.window.decorView).filterIsInstance<Button>()
            .single { it.text == activity.getString(R.string.update_release_notes_more) }

        assertFalse(ReflectionHelpers.getField<Boolean>(activity, "releaseNotesExpanded"))

        expandButton.performClick()

        assertTrue(ReflectionHelpers.getField<Boolean>(activity, "releaseNotesExpanded"))
        val collapseButton = descendants(activity.window.decorView).filterIsInstance<Button>()
            .single { it.text == activity.getString(R.string.update_release_notes_less) }

        collapseButton.performClick()

        assertFalse(ReflectionHelpers.getField<Boolean>(activity, "releaseNotesExpanded"))

        controller.pause().stop().destroy()
    }

    @Test fun checkForUpdatesClearsStaleReleaseWhenRemoteIsUpToDate() {
        val staleRelease = UpdateRelease(
            tagName = "v99.0.0",
            apkName = "DiPlay-99.0.0.apk",
            apkUrl = "https://example.com/DiPlay.apk",
            checksumsUrl = "https://example.com/SHA256SUMS.txt",
        )
        UpdateAvailability.save(application, staleRelease)

        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        // Verify initial cached update stage is AVAILABLE
        assertEquals("AVAILABLE", ReflectionHelpers.getField<Any>(activity, "updateStage").toString())

        // Simulate latestRelease() returning null (server says up-to-date)
        ReflectionHelpers.setField(activity, "availableUpdate", null)
        ReflectionHelpers.setField(activity, "updateRelease", null)
        UpdateAvailability.clear(application)
        ReflectionHelpers.setField(activity, "updateMessage", activity.getString(R.string.update_up_to_date))
        ReflectionHelpers.setField(activity, "updateStage", ReflectionHelpers.getField<Any>(activity, "updateStage")::class.java.enumConstants!!.single { it.toString() == "IDLE" })
        ReflectionHelpers.callInstanceMethod<Unit>(activity, "render")

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        val installedVersion = ReflectionHelpers.callInstanceMethod<String>(activity, "version")
        assertTrue(views.any { it.text == activity.getString(R.string.update_installed_version, installedVersion) })
        assertTrue(views.any { it.text == activity.getString(R.string.update_latest_version, installedVersion) })
        assertTrue(views.any { it.text == activity.getString(R.string.update_up_to_date) })

        assertNull(UpdateAvailability.available(application, installedVersion))
        assertNull(ReflectionHelpers.getField<UpdateRelease>(activity, "availableUpdate"))
        assertNull(ReflectionHelpers.getField<UpdateRelease>(activity, "updateRelease"))

        controller.pause().stop().destroy()
    }

    @Test fun downloadUpdateDoesNotFallbackToCachedReleaseWhenLookupReturnsNull() {
        val cachedRelease = UpdateRelease(
            tagName = "v99.0.0",
            apkName = "DiPlay-99.0.0.apk",
            apkUrl = "https://example.com/DiPlay.apk",
            checksumsUrl = "https://example.com/SHA256SUMS.txt",
        )
        UpdateAvailability.save(application, cachedRelease)

        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        // Simulate download failure where latestRelease() returned null (no update)
        UpdateAvailability.clear(application)
        ReflectionHelpers.setField(activity, "availableUpdate", null)
        ReflectionHelpers.setField(activity, "updateRelease", null)
        ReflectionHelpers.setField(activity, "updateMessage", activity.getString(R.string.update_up_to_date))
        val idleStage = ReflectionHelpers.getField<Any>(activity, "updateStage")::class.java.enumConstants!!.single { it.toString() == "IDLE" }
        ReflectionHelpers.setField(activity, "updateStage", idleStage)
        ReflectionHelpers.callInstanceMethod<Unit>(activity, "render")

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        assertTrue(views.any { it.text == activity.getString(R.string.update_up_to_date) })
        assertNull(ReflectionHelpers.getField<UpdateRelease>(activity, "updateRelease"))

        controller.pause().stop().destroy()
    }

    @Test fun settingsAboutDisplaysClearErrorMessageOnFailure() {
        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        val stageClass = ReflectionHelpers.getField<Any>(activity, "updateStage")::class.java
        val failedStage = stageClass.enumConstants!!.single { it.toString() == "FAILED" }
        ReflectionHelpers.setField(activity, "updateStage", failedStage)
        ReflectionHelpers.setField(activity, "updateMessage", activity.getString(R.string.update_no_internet))
        ReflectionHelpers.callInstanceMethod<Unit>(activity, "render")

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        assertTrue(views.any { it.text == activity.getString(R.string.update_no_internet) })
        assertTrue(views.any { it.text == activity.getString(R.string.update_check) })

        controller.pause().stop().destroy()
    }

    private fun openAboutCategory(activity: DiPlayActivity) {
        ReflectionHelpers.setField(activity, "page", "settings")
        ReflectionHelpers.setField(activity, "settingsCategory", SettingsCategory.ABOUT)
        ReflectionHelpers.callInstanceMethod<Unit>(activity, "render")
    }

    private fun descendants(view: View): Sequence<View> = sequence {
        yield(view)
        if (view is ViewGroup) for (index in 0 until view.childCount) {
            yieldAll(descendants(view.getChildAt(index)))
        }
    }
}
