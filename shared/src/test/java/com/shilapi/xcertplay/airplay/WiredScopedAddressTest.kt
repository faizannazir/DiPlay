package com.shilapi.xcertplay.airplay

import java.net.Inet4Address
import java.net.Inet6Address
import java.net.InetAddress
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class WiredScopedAddressTest {

    @Test fun nullRemoteAddressReturnsNull() {
        assertNull(ScopedAddressCompat.scopeRemoteAddress(null, null))
    }

    @Test fun ipv4RemoteAddressIsUnchanged() {
        val ipv4 = InetAddress.getByName("192.168.1.100")
        val scoped = ScopedAddressCompat.scopeRemoteAddress(ipv4, null)
        assertEquals(ipv4, scoped)
    }

    @Test fun scopedIpv6RemoteAddressIsUnchanged() {
        val ipv6Bytes = byteArrayOf(0xfe.toByte(), 0x80.toByte(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        val scopedIpv6 = Inet6Address.getByAddress(null, ipv6Bytes, 5)
        val result = ScopedAddressCompat.scopeRemoteAddress(scopedIpv6, null)
        assertEquals(5, (result as Inet6Address).scopeId)
    }

    @Test fun unscopedLinkLocalIpv6RemoteAddressInheritsLocalScopeId() {
        val ipv6Bytes = byteArrayOf(0xfe.toByte(), 0x80.toByte(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        val localBytes = byteArrayOf(0xfe.toByte(), 0x80.toByte(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2)
        val unscopedRemote = InetAddress.getByAddress(ipv6Bytes)
        val scopedLocal = Inet6Address.getByAddress(null, localBytes, 12)

        val result = ScopedAddressCompat.scopeRemoteAddress(unscopedRemote, scopedLocal)
        assertEquals(12, (result as Inet6Address).scopeId)
    }

    @Test fun globalIpv6RemoteAddressIsUnchanged() {
        val globalBytes = byteArrayOf(0x20, 0x01, 0x0d, 0xb8.toByte(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        val remote = InetAddress.getByAddress(globalBytes)
        val result = ScopedAddressCompat.scopeRemoteAddress(remote, null)
        assertEquals(remote, result)
    }
}
