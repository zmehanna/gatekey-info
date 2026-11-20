#!/usr/bin/env python3
"""Fail-closed verifier for offline PrivateGateKey cloud-demo APKs.

Uses only the Python standard library and parses the compiled binary AndroidManifest
(not the source manifest). This must run BEFORE uploading any APK to Appetize.
"""
import struct
import sys
import zipfile

DEMO_PACKAGE = "com.klmehanna.privategatekey.demo"
INTERNET = "android.permission.INTERNET"
INVALID = 0xFFFFFFFF


def u16(data, p):
    return struct.unpack_from("<H", data, p)[0]


def u32(data, p):
    return struct.unpack_from("<I", data, p)[0]


def utf8_length(data, p):
    first = data[p]
    if first & 0x80:
        return ((first & 0x7F) << 8) | data[p + 1], p + 2
    return first, p + 1


def utf16_length(data, p):
    first = u16(data, p)
    if first & 0x8000:
        return ((first & 0x7FFF) << 16) | u16(data, p + 2), p + 4
    return first, p + 2


def read_string_pool(data, p, size, header):
    count = u32(data, p + 8)
    flags = u32(data, p + 16)
    strings_start = u32(data, p + 20)
    if count > 100000 or header < 28 or strings_start >= size:
        raise ValueError("Invalid Android XML string pool")
    result = []
    for i in range(count):
        off = u32(data, p + header + 4 * i)
        start = p + strings_start + off
        if start >= p + size:
            raise ValueError("Android string offset out of range")
        if flags & 0x100:  # UTF-8
            _, k = utf8_length(data, start)
            length, k = utf8_length(data, k)
            result.append(data[k:k + length].decode("utf-8", "strict"))
        else:
            length, k = utf16_length(data, start)
            result.append(data[k:k + 2 * length].decode("utf-16le", "strict"))
    return result


def inspect_manifest(data):
    if len(data) < 8 or u16(data, 0) != 0x0003 or u32(data, 4) != len(data):
        raise ValueError("Not a valid binary AndroidManifest.xml")
    strings = None
    root_attributes = None
    permissions = set()
    position = u16(data, 2)
    while position + 8 <= len(data):
        chunk_type = u16(data, position)
        header = u16(data, position + 2)
        size = u32(data, position + 4)
        if header < 8 or size < header or position + size > len(data):
            raise ValueError("Malformed Android XML chunk")
        if chunk_type == 0x0001:
            strings = read_string_pool(data, position, size, header)
        elif chunk_type == 0x0102:
            if strings is None or header < 16:
                raise ValueError("Android XML start element before string pool")
            name_id = u32(data, position + 20)
            if name_id >= len(strings):
                raise ValueError("Unknown Android XML tag")
            tag = strings[name_id]
            attr_offset = u16(data, position + 24)
            attr_size = u16(data, position + 26)
            attr_count = u16(data, position + 28)
            start = position + 16 + attr_offset
            if attr_size < 20 or start + attr_count * attr_size > position + size:
                raise ValueError("Malformed Android XML attributes")
            attrs = {}
            for i in range(attr_count):
                k = start + i * attr_size
                name_idx = u32(data, k + 4)
                raw_idx = u32(data, k + 8)
                kind = data[k + 15]
                value_idx = u32(data, k + 16)
                if name_idx >= len(strings):
                    raise ValueError("Malformed Android attribute name")
                if raw_idx != INVALID:
                    value = strings[raw_idx]
                elif kind == 0x03 and value_idx < len(strings):
                    value = strings[value_idx]
                else:
                    value = None
                attrs[strings[name_idx]] = value
            if tag == "manifest":
                if root_attributes is not None:
                    raise ValueError("Duplicate manifest root")
                root_attributes = attrs
            if tag.startswith("uses-permission"):
                permissions.add(attrs.get("name"))
        position += size
    if position != len(data) or strings is None or root_attributes is None:
        raise ValueError("Incomplete AndroidManifest.xml")
    return root_attributes, permissions, strings


def main():
    if len(sys.argv) != 3:
        raise ValueError("Usage: verify_preview_apk.py <app-preview.apk> <version>")
    apk_path, version = sys.argv[1:]
    with zipfile.ZipFile(apk_path) as apk:
        manifest = apk.read("AndroidManifest.xml")
    attributes, permissions, strings = inspect_manifest(manifest)
    if attributes.get("package") != DEMO_PACKAGE:
        raise ValueError("Non-demo package: refused")
    if attributes.get("versionName") != version + "-demo":
        raise ValueError("Outdated or mismatched demo version: refused")
    if INTERNET in permissions or INTERNET in strings:
        raise ValueError("APK declares/references INTERNET permission: refused")
    print("Verified isolated offline-only APK:", DEMO_PACKAGE, version)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("REFUSED:", exc, file=sys.stderr)
        sys.exit(1)
