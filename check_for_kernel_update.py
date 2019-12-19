#!/usr/bin/env python3
def main():
    cu = CheckMainlineKernelUpdate()
    new_version = cu.check_for_update()

    if new_version is not None:
        notify2.init("Kernel update check")
        message = notify2.Notification("Found new kernel version!", "Kernel " + new_version + " is available!",
                                       "gtk-dialog-info")
        message.show()


class CheckMainlineKernelUpdate:
    def __init__(self):
        self._version_string = sp.check_output(["uname", "-r"]).decode("UTF-8").rstrip()
        self._new_version = self._generate_new_version_string()

    def check_for_update(self):
        if self._new_version == self._get_latest_version() and self._check_availability():
            return self._new_version

    def _generate_new_version_string(self):
        version_pattern = re.compile(r"(\d{1,2}).(\d{1,2}).(\d{1,2})-\d{6}(rc\d{1,2})?")
        rc_pattern = re.compile(r"rc(\d{1,2})")
        m = version_pattern.match(self._version_string)
        if m is not None:
            main_version, minor_version, patch_level_string, rc_string = m.groups()
            patch_level = int(patch_level_string)

            if rc_string is not None:
                rc_version = int(rc_pattern.match(rc_string).group(1))
                rc_version += 1
                return "{:}.{:}.{:}rc{:}".format(main_version, minor_version, patch_level_string, rc_version)
            else:
                patch_level += 1
                return "{:}.{:}.{:}".format(main_version, minor_version, patch_level)
        else:
            return None

    def _check_availability(self):
        mainline_url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/v" + self._new_version
        r = requests.get(mainline_url)
        r.close()

        if r.status_code == 200:
            return True
        else:
            return False

    def _get_latest_version(self):
        r = requests.get("https://www.kernel.org")
        html_string = r.content.decode("UTF-8")
        r.close()
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(html_string), parser)

        return root.find('.//*[@id="latest_link"]')[0].text


if __name__ == "__main__":
    import requests
    import notify2
    import re
    from lxml import etree
    from io import StringIO
    import subprocess as sp

    main()
