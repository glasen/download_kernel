#!/usr/bin/env python3
def main():
    parser = argparse.ArgumentParser(description="Download kernel from mainline PPA.")
    parser.add_argument("--version", help="Kernel version")
    parser.add_argument("--type", help="Kernel type", default="generic", choices=["generic", "lowlatency", "lpae","snapdragon"])
    parser.add_argument("--cpu", help="CPU type", default="amd64", choices=["amd64", "i386","armhf","arm64","ppc64el","s390x"])

    args = parser.parse_args()

    version = args.version
    type = args.type
    cpu = args.cpu
    
    if type == "lowlatency" and cpu != "amd64" or "i386":
        print("There is no lowlatency kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)
    elif type == "lpae" and cpu != "armhf":
        print("There is no lpae kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)
    elif type == "snapdragon" and cpu != "arm64":
        print("There is no snapdragon kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)

    if version == None:
        version = get_latest_stable_version()

    urllist = get_urls(version)

    checked_set = check_urls(urllist, type, cpu)

    if len(checked_set) != 0 and len(checked_set) > 2:
        download_kernel(checked_set)
    else:
        print("Something went wrong. Please check Mainline-PPA if all deb-files are available for download!")


def check_urls(urllist, type, cpu):
    checked_set = set()

    for url in urllist:
        filename = url.split("/")[-1]

        if "_all.deb" in filename:
            checked_set.add(url)

        if type in filename and cpu in filename:
            checked_set.add(url)

    return checked_set


def get_latest_stable_version():
    http = urllib3.PoolManager()
    r = http.request("GET", "https://www.kernel.org")
    root = parse(r.data)
    version_path = root.xpath("/html/body/aside/article/table[2]/tbody/tr[2]/td[2]/a")
    return version_path[0].text


def get_urls(version):
    mainline_url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/v" + version

    urllist = list()

    http = urllib3.PoolManager()
    r = http.request("GET", mainline_url)
    root = parse(r.data)

    if root.xpath("/html/body/h1")[0].text != "Not Found":

        pattern = re.compile("^linux.*.deb")
        path = "/html/body/code/a"
        filenames = root.xpath(path)

        for filename in filenames:
            if pattern.match(filename.text):
                urllist.append(mainline_url + "/" + filename.text)

    return urllist


def download_kernel(urlset):
    for url in urlset:
        print("Downloading file \"%s\"" % url)
        wget.download(url)
        print()


if __name__ == "__main__":
    try:
        import urllib3
    except ImportError:
        raise ImportError("This script needs the python module \"urllib3\"")

    try:
        from html5_parser import parse
    except ImportError:
        raise ImportError("This script needs the python module \"html5_parser\"")

    try:
        import wget
    except ImportError:
        raise ImportError("This script needs the python module \"wget\"")

    import argparse, re

    main()
