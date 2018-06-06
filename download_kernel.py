#!/usr/bin/env python3
def main():
    parser = argparse.ArgumentParser(description="Download kernel from mainline PPA.")
    parser.add_argument("--version", help="Kernel version")
    parser.add_argument("--list_versions", help="List available versions", action='store_true')
    parser.add_argument("--type", help="Kernel type", default="generic", choices=["generic", "lowlatency", "lpae","snapdragon"])
    parser.add_argument("--cpu", help="CPU type", choices=["amd64", "i386","armhf","arm64","ppc64el","s390x"])

    args = parser.parse_args()

    version = args.version
    list_versions = args.list_versions
    type = args.type
    cpu = args.cpu


    if cpu == None:
        args = ["dpkg","--print-architecture"]
        cpu = sp.check_output(args).decode("utf-8").strip()

    if list_versions:
        available_versions()
        exit(1)

    if version == None:
        version = get_latest_stable_version()

    if type == "lowlatency" and cpu in ["armhf","arm64","ppc64el","s390x"]:
        print("There is no lowlatency kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)
    elif type == "lpae" and cpu != "armhf":
        print("There is no lpae kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)
    elif type == "snapdragon" and cpu != "arm64":
        print("There is no snapdragon kernel for cpu architecture \"%s\"" % (cpu))
        exit(1)

    urllist = get_urls(version)

    filtered_set = filter_urls(urllist, type, cpu)

    if len(filtered_set) != 0 and len(filtered_set) > 2:
       download_kernel(filtered_set)
    else:
       print("Something went wrong. Please check Mainline-PPA if all deb-files are available for download!")


def filter_urls(urllist, type, cpu):
    pattern = re.compile(".*"+type+".*"+cpu+".deb")

    filtered_set = set()

    for url in urllist:
        if "_all.deb" in url:
            filtered_set.add(url)

        if pattern.match(url):
            filtered_set.add(url)

    return filtered_set


def available_versions():
    print("Available kernel versions on \"kernel.ubuntu.com\":\n")

    r = requests.get("https://www.kernel.org")
    html_string = r.content.decode("UTF-8")
    parser = etree.HTMLParser()
    root = etree.parse(StringIO(html_string), parser)

    version_path = root.xpath("/html/body/aside/article/table[3]//tr")

    for element in version_path:
        if len(element[1][0]):
             eol_status = "EOL"
        else:
             eol_status = ""

        type = element[0].text
        version = element[1][0].text
        if check_availability(version):
            print(type, version , eol_status)

def check_availability(version):
    mainline_url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/v"+version
    r = requests.get(mainline_url)

    if r.status_code == 200:
        return True
    else:
        return False


def get_latest_stable_version():
    r = requests.get("https://www.kernel.org")

    html_string = r.content.decode("UTF-8")
    parser = etree.HTMLParser()
    root = etree.parse(StringIO(html_string), parser)

    return root.find('.//*[@id="latest_link"]')[0].text


def get_urls(version):
    mainline_url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/v" + version

    urllist = list()

    r = requests.get(mainline_url)
    html_string = r.content.decode("UTF-8")
    parser = etree.HTMLParser()
    root = etree.parse(StringIO(html_string), parser)

    if len(root.findall(".//body//a")) != 0:
        for child in root.findall(".//body//a"):
            filename = child.text
            pattern = re.compile("^linux.*.deb")
            if pattern.match(filename):
                urllist.append(mainline_url + "/" + filename)

    return urllist


def download_kernel(urlset):
    for url in urlset:
        args = ["wget","-c","-q","--show-progress","--progress=bar:noscroll",url]
        sp.call(args)


if __name__ == "__main__":
    import requests
    from lxml import etree
    from io import StringIO

    import argparse, re
    import subprocess as sp

    main()
