package com.shilapi.xcertplay.media

import android.media.AudioTrack
import android.os.Process
import com.shilapi.xcertplay.airplay.AudioCodecKind
import com.shilapi.xcertplay.airplay.AudioFormat
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import org.robolectric.annotation.Config
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [AudioThreadPriorityTest.ShadowAudioTrackPriority::class])
class AudioThreadPriorityTest {

    @Implements(AudioTrack::class)
    class ShadowAudioTrackPriority {
        @Implementation
        protected fun getMinBufferSize(sampleRateInHz: Int, channelConfig: Int, audioFormat: Int): Int {
            return 4096
        }
    }

    @Test
    fun audioRendererWorkerSetsAudioThreadPriority() {
        val prioritySetLatch = CountDownLatch(1)
        val observedPriority = AtomicInteger(Int.MIN_VALUE)

        val format = AudioFormat(
            payloadType = 120,
            sampleRate = 44100,
            channels = 2,
            audioType = "media",
            codec = AudioCodecKind.LPCM,
        )

        val coordinator = AudioFocusCoordinator(null, enabled = false)
        val sink = AndroidMediaSink()

        val rendererClass = Class.forName("com.shilapi.xcertplay.media.AudioRenderer")
        val constructor = rendererClass.getDeclaredConstructors().first().apply { isAccessible = true }

        val report: (String) -> Unit = { msg ->
            if (msg.contains("Audio: starting")) {
                observedPriority.set(Process.getThreadPriority(Process.myTid()))
                prioritySetLatch.countDown()
            }
        }

        val renderer = constructor.newInstance(
            format,
            false, // advancedAudioChannelMapping
            false, // audioFocusEnabled
            0,     // mediaChannel
            0,     // navigationChannel
            coordinator,
            3,     // navigationStreamType
            300,   // mediaBufferMillis
            report,
            0L,    // ambientSinkToken
            false, // speakerphoneCall
            null,  // echoReference
            false  // voiceFilter
        ) as AutoCloseable

        val startMethod = rendererClass.getDeclaredMethod("start").apply { isAccessible = true }
        startMethod.invoke(renderer)

        val priorityWasObserved = prioritySetLatch.await(3, TimeUnit.SECONDS)
        renderer.close()
        sink.close()

        assertEquals("Expected priority latch to count down", true, priorityWasObserved)
        assertEquals("Expected thread priority THREAD_PRIORITY_AUDIO", Process.THREAD_PRIORITY_AUDIO, observedPriority.get())
    }
}
