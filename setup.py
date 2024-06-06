#!/usr/bin/env python3

import os
import yaml
from ppadb.client import Client as AdbClient

from fdroid import *
from arch import Arch

def main():
    apks_folder = "apks"

    client = AdbClient()
    if client.devices():
        device = client.devices()[0]
        # device = client.devices("<device-dsn>")
    else:
        print("\nNo devices available")
        exit(-1)

    arch = device.shell("getprop ro.product.cpu.abilist")
    if "arm64-v8a" in arch:
        arch = Arch.ARMv8_A
    elif "armeabi-v7a" in arch:
        arch = Arch.ARMv7_A

    repo_db = FDroidRepoDB("./repos")

    with open("apps.yml", 'r') as stream:
        try:
            apps_list = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
            exit()

    for app in apps_list:
        if app.get("source") == "fdroid":
            app_id = app.get("app-id")
            repo_url = app.get("repo")
            repo = None

            if not device.is_installed(app_id):
                print(f"Installing {app_id}")
                repo = repo_db.get_repo(repo_url)
                device.install(repo.download_app(app_id, arch, apks_folder))
            else:
                print(f"App already installed: {app_id}")

if __name__ == "__main__":
    main()
