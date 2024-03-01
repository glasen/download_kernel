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
        self._kernel_url = "https://www.kernel.org"
        self._mainline_url = "https://kernel.ubuntu.com/mainline/"
        self._version_string = sp.check_output(["uname", "-r"]).decode("UTF-8").rstrip()
        self._new_version = self._generate_new_version_string()

    def check_for_update(self):
        if self._new_version == self._get_latest_version() and self._check_availability():
            return self._new_version

    def _generate_new_version_string(self):
        version_pattern = re.compile(r"(\d{1,2}).(\d{1,2}).(\d{1,2})-\d{6}(rc\d{1,2})?")
        rc_pattern = re.compile(r"rc(\d{1,2})")
        if version_pattern.match(self._version_string):
            main_version, minor_version, patch_level_string, rc_string = version_pattern.findall(self._version_string)[0]
            patch_level = int(patch_level_string)

            if rc_string != "":
                rc_version = int(rc_pattern.findall(rc_string)[0])
                rc_version += 1
                return f"{main_version}.{minor_version}.{patch_level_string}rc{rc_version}"
            else:
                patch_level += 1
                return f"{main_version}.{minor_version}.{patch_level}"
        else:
            return None

    def _check_availability(self):
        complete_url = "/".join([self._mainline_url, "v" + self._new_version])
        r = requests.get(complete_url)
        r.close()

        if r.status_code == 200:
            return True
        else:
            return False

    def _get_latest_version(self):
        r = requests.get(self._kernel_url)
        html_string = r.content.decode("UTF-8")
        r.close()
        parser = etree.HTMLParser()
        latest_version = etree.parse(StringIO(html_string), parser).find('.//*[@id="latest_link"]')[0].text

        return latest_version


if __name__ == "__main__":
    import requests
    import notify2
    import re
    from lxml import etree
    from io import StringIO
    import subprocess as sp

    main()
