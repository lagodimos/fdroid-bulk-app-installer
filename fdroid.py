import os
import json
import requests
import hashlib
import copy

from arch import Arch
from root_domain import root_domain

class FDroidRepoDB:
    def __init__(self, repos_directory: str):
        self.__repos = []
        self.__repos_dir = repos_directory

    def get_repo(self, url: str):
        """
        If the repository doesn't exist in the database it
        creates it, otherwise returns the existing one.

        Checks if a repository is the same as another
        only based on their domains.
        """

        repo = next(
            (repo for repo in self.__repos if repo.domain == root_domain(url)),
            FDroidRepo(url, self.__repos_dir)
        )

        return repo

class FDroidRepo:
    def __init__(self, url: str, repos_directory: str):
        self.__url = url                # https://f-droid.org/repo
        self.__domain = ""              # f-droid.org
        self.__repo_dir = ""            # ./repos/f-droid.org/
        self.__index_file = ""          # /index-v2.json
        self.__index = {}

        if self.__url.endswith("/"):
            self.__url = self.__url[:-1]

        self.__domain = root_domain(self.__url)

        self.__repo_dir = repos_directory + "/" + self.__domain
        if not os.path.exists(self.__repo_dir):
            os.makedirs(self.__repo_dir)

        self.__load_index()

    @property
    def url(self):
        return self.__url

    @property
    def domain(self):
        return self.__domain

    def __load_index(self):
        response = requests.get(self.__url + "/entry.json")
        entry = response.json()
        self.__index_file = entry.get("index").get("name")

        update_index = True

        if os.path.isfile(self.__repo_dir + self.__index_file):
            with open(self.__repo_dir + self.__index_file, 'rb') as f:
                if hashlib.sha256(f.read()).hexdigest() == entry.get("index").get("sha256"):
                    f.seek(0)
                    self.__index = json.load(f)
                    update_index = False

        if update_index:
            print("Updating repository index...")
            response = requests.get(self.__url + self.__index_file)
            self.__index = response.json()

            with open(self.__repo_dir + self.__index_file, "wb") as f:
                f.write(response.content)

    def __get_arch_str(self, arch: str):
        arch_str = None

        match arch:
            case Arch.ARMv8_A:
                arch_str = "arm64-v8a"
            case Arch.ARMv7_A:
                arch_str = "armeabi-v7a"

        return arch_str

    def download_app(self, app_id: str, arch: Arch, directory: str) -> str:
        """
        Returns the path of the downloaded apk
        """

        app_index = self.__index.get("packages").get(app_id)
        apk_path = None

        if app_index is not None:
            version = self.__get_latest_app_version(app_id, arch)
            file_name = app_index.get("versions").get(version).get("file").get("name")
            url = self.__url + file_name
            apk_path = directory + "/" + url.split("/")[-1]

            if not os.path.exists(apk_path):
                r = requests.get(url)

                with open(apk_path, 'wb') as f:
                    f.write(r.content)
        else:
            print("App not found in the given repo.")

        return apk_path

    def __get_latest_app_version(self, app_id: str, arch: Arch):
        app_index = self.__index.get("packages").get(app_id)
        arch_str = self.__get_arch_str(arch)

        for version in app_index.get("versions").keys():
            nativecode = app_index.get("versions").get(version).get("manifest").get("nativecode")

            if nativecode == None or arch_str in nativecode:
                return version

        print(f"{app_id} apk not available for this architecture")
