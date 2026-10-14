package com.shilapi.xcertplay

import android.app.Application
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import com.shilapi.xcertplay.host.R
import com.shilapi.xcertplay.update.UpdateAvailability
import com.shilapi.xcertplay.update.UpdateRelease
import org.junit.After
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

    @Test fun settingsAboutDisplaysUpToDateMessageWhenNoNewerVersion() {
        val controller = Robolectric.buildActivity(DiPlayActivity::class.java).setup()
        val activity = controller.get()

        openAboutCategory(activity)

        ReflectionHelpers.setField(activity, "updateMessage", activity.getString(R.string.update_up_to_date))
        ReflectionHelpers.callInstanceMethod<Unit>(activity, "render")

        val views = descendants(activity.window.decorView).filterIsInstance<TextView>().toList()
        assertTrue(views.any { it.text == activity.getString(R.string.update_up_to_date) })
        assertTrue(views.any { it.text == activity.getString(R.string.update_check) })

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
