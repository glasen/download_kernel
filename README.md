# Description
Small python script checks www.kernel.org for the latest stable version and downloads needed Debian packages from Ubuntu mainline kernel PPA.

# Requirements
The script needs three additional python modules which are normally not in a typical Ubuntu or Debian installation. The modules can be installed with the following command:

```sudo apt install python3-wget python3-html5-parser python3-urllib3```

# Usage

```
usage: download_kernel.py [-h] [--version VERSION] [--list_versions]
                          [--type {generic,lowlatency,lpae,snapdragon}]
                          [--cpu {amd64,i386,armhf,arm64,ppc64el,s390x}]

Download kernel from mainline PPA.

optional arguments:
  -h, --help            show this help message and exit
  --version VERSION     Kernel version
  --list_versions       List available versions
  --type {generic,lowlatency,lpae,snapdragon}
                        Kernel type
  --cpu {amd64,i386,armhf,arm64,ppc64el,s390x}
                        CPU type
```