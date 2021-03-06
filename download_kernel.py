#!/usr/bin/env python3
def main():
    parser = argparse.ArgumentParser(description="Download kernel from mainline PPA.")
    parser.add_argument("--version", "-v", help="Kernel version")
    parser.add_argument("--list_versions", "-l", help="List available versions", action='store_true')
    parser.add_argument("--type", "-t", help="Kernel type", default="generic",
                        choices=["generic", "lowlatency", "lpae"])
    parser.add_argument("--cpu", "-c", help="CPU type", choices=["amd64", "i386", "armhf", "arm64", "ppc64el", "s390x"])

    args = parser.parse_args()

    cpu = args.cpu
    kernel_type = args.type
    version = args.version
    list_versions = args.list_versions

    dk = DownloadKernel(cpu, kernel_type, version)

    if list_versions:
        dk.list_available_versions()
    else:
        status = dk.check_status()
        if status == 0:
            dk.download_kernel()
        elif status == 2:
            print("This kernel-version is not available because of some compile error!")
        else:
            print("This kernel-version is not available because of an unknown reason!")


class DownloadKernel:
    def __init__(self, cpu, kernel_type, version):
        self._kernel_url = "https://www.kernel.org"
        self._mainline_url = "https://kernel.ubuntu.com/~kernel-ppa/mainline"

        self._type_combinations = {"generic": ["amd64", "i386", "armhf", "arm64", "ppc64el", "s390x"],
                                   "lowlatency": ["amd64", "i386"],
                                   "lpae": ["armhf"]}

        self._kernel_tree = self._get_html_tree(self._kernel_url)

        if cpu is None:
            args = ["dpkg", "--print-architecture"]
            self._cpu = sp.check_output(args).decode("utf-8").strip()
        else:
            self._cpu = cpu

        if version is None:
            self._version = self._get_latest_stable_version()
        else:
            self._version = version

        self._kernel_type = kernel_type

        if self._cpu not in self._type_combinations[self._kernel_type]:
            print("There is no \"%s\" kernel for cpu architecture \"%s\"" % (self._kernel_type, self._cpu))
            exit(1)

    def check_status(self):
        status_url = "/".join([self._mainline_url, "v" + self._version, self._cpu, "status"])
        r = requests.get(status_url)
        return int(r.content.strip())

    def list_available_versions(self):
        print("Available kernel versions on \"%s\":\n" % self._kernel_url)

        version_path = self._kernel_tree.xpath("/html/body/aside/article/table[3]//tr")
        mainline_versions = self._check_availability()

        for element in version_path:
            if len(element[1][0]):
                eol_status = "EOL"
            else:
                eol_status = ""

            support_type = element[0].text
            version = element[1][0].text

            if version in mainline_versions:
                print(support_type, version, eol_status)

    def download_kernel(self):
        url_list = self._get_urls()
        url_set = self._filter_urls(url_list)

        number_of_packages = len(url_set)

        if number_of_packages == 4:
            for url in url_set:
                print(f"Downloading file \"{url}\" ...")
                args = ["curl", "-O", url]
                sp.call(args)
                print()
        else:
            print(f"There are only {number_of_packages} packages available. Please try again later!")

    def _check_availability(self):
        available_versions = list()
        mainline_tree = self._get_html_tree(self._mainline_url)

        version_path = mainline_tree.xpath("/html/body/table//tr/td/a")
        for element in version_path:
            version = element.text
            if version.startswith("v"):
                available_versions.append(version[1:-1])

        return available_versions

    def _get_latest_stable_version(self):
        return self._kernel_tree.find('.//*[@id="latest_link"]')[0].text

    def _get_urls(self):
        url_list = list()

        file_url = "/".join([self._mainline_url, "v" + self._version])
        root = self._get_html_tree(file_url)

        if len(root.findall(".//body//a")) != 0:
            for child in root.findall(".//body//a"):
                filename = child.text
                pattern = re.compile("^("+self._cpu+"\/)?linux.*.deb")
                if pattern.match(filename):
                    url_list.append("/".join([file_url, filename]))

        return url_list

    def _filter_urls(self, urllist):
        pattern = re.compile(".*" + self._kernel_type + ".*" + self._cpu + ".deb")

        filtered_set = set()

        for url in urllist:
            if "_all.deb" in url:
                filtered_set.add(url)

            if pattern.match(url):
                filtered_set.add(url)

        return filtered_set

    @staticmethod
    def _get_html_tree(url):
        r = requests.get(url)
        html_string = r.content.decode("UTF-8")
        r.close()

        parser = etree.HTMLParser()
        return etree.parse(StringIO(html_string), parser)


if __name__ == "__main__":
    import requests
    from lxml import etree
    from io import StringIO

    import argparse
    import re
    import subprocess as sp

    main()
