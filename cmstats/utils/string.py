import re


def parse_modversion(modversion):
    # Ignore KANG versions.
    if "KANG" in modversion:
        return None
    if "UNOFFICIAL" in modversion:
        return None

    # Determine RC Version
    match_rc = re.match(r"^(CyanogenMod-)*(\d+\.\d\.\d\.?\d?)-RC(\d+)-.*$", modversion)
    match_stable = re.match(r"^(CyanogenMod-)*(\d+\.\d\.\d\.?\d?)-.*$", modversion)
    match_nightly = re.match(r"^(CyanogenMod-)*(\d+\.?\d?)-\d{8}-NIGHTLY-.*$", modversion)
    match_installer_snap = re.match(r"^(\d+\.?\d?)-\d{8}-SNAPSHOT-Installer.*$", modversion)
    match_m_snap = re.match(r"^(\d+\.?\d?)-\d{8}-SNAPSHOT-M(\d+)-.*$", modversion)
    match_old_m_snap = re.match(r"^(\d+\.?\d?)-\d{8}-EXPERIMENTAL-(.+)-M(\d+)$", modversion)

    if match_rc:
        return "%s-RC%s" % (match_rc.group(2), match_rc.group(3))

    elif match_nightly:
        return "Nightly-%s" % (match_nightly.group(2))

    elif match_installer_snap:
        return "Installer-%s" % (match_installer_snap.group(1))

    elif match_m_snap:
        return "M-Snapshot-%s" % (match_m_snap.group(1))

    elif match_old_m_snap:
        return "M-Snapshot-%s" % (match_old_m_snap.group(1))

    elif match_stable:
        return match_stable.group(2)

def clean_unicode(s):
    return s.decode('utf8', 'ignore')
