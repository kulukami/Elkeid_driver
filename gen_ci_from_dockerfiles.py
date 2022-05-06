import yaml
import os
from collections import OrderedDict


all_dockers = os.listdir("dockerfiles")

black_list = ["rhel7_elrepo", "rhel8_elrepo"]

all_vms = []

jobs = []


def gen_job(vmname):
    some_data = OrderedDict(
        {
            "runs-on": "ubuntu-latest",
            "steps": [
                OrderedDict({
                    "uses": "actions/checkout@v2",
                    "with": {
                        "submodules": "recursive"
                    }
                }),
                OrderedDict({
                    "name": "Login to Docker Hub",
                    "uses": "docker/login-action@v1",
                    "with": {
                        "username": "${{secrets.DOCKERHUB_USERNAME}}",
                        "password": "${{secrets.DOCKERHUB_TOKEN}}"
                    }
                }),
                OrderedDict({
                    "name": "Set up Docker Buildx "+vmname,
                    "uses": "docker/setup-buildx-action@v1"
                }),

                OrderedDict({
                    "name": "Build "+vmname,
                    "uses": "docker/build-push-action@v2",
                    "with": {
                        "file": "dockerfiles/Dockerfile."+vmname,
                        "push": True,
                        "tags": "kulukami/elkeid_driver_"+vmname+":latest"
                    }
                }),
                OrderedDict({
                    "name": "Extract "+vmname,
                    "id": "extract-"+vmname,
                    "uses": "shrink/actions-docker-extract@v1",
                    "with": {
                        "image": "kulukami/elkeid_driver_"+vmname+":latest",
                        "path": "/ko_output/."
                    }
                }),
                OrderedDict({
                    "name": "Upload "+vmname,
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "path": "${{steps.extract-"+vmname+".outputs.destination}}",
                        "name": "elkeid_driver_"+vmname
                    }
                })
            ]

        }
    )
    return some_data


for each_dockers in all_dockers:
    all_vms.append(each_dockers.replace("Dockerfile.", ""))

yaml_cfg = OrderedDict(
    {
        "name": "Elkeid_driver",
        "on": {
            "push": {
                "branches": [
                    "main",
                    "'releases/**'"
                ]
            },
            "schedule": ["cron : '0 3 * * *'"]
        }
    }
)

create_release_job = OrderedDict(
    {
        "runs-on": "ubuntu-latest",
        "permissions": "write-all",
        "steps": [
            OrderedDict({
                "name": "Create Release",
                "id": "create_release",
                "uses": "actions/create-release@v1",
                "env": {
                        "GITHUB_TOKEN": "${{secrets.GITHUB_TOKEN}}"
                },
                "with": {
                    "tag_name": "${{github.ref}}",
                    "release_name": "Release ${{github.ref}}",
                    "draft": False,
                    "prerelease": False,
                }
            }),
            OrderedDict({
                "uses": "actions/download-artifact@v3",
                "with": {
                    "path": "/all_elkeid_drivers"
                }
            }),
            OrderedDict({
                "name": "Pack artifact ",
                "run": "zip --junk-paths -r elkeid_driver.zip /all_elkeid_drivers"
            }),

            OrderedDict({
                "name": "Upload Release Asset ",
                "id": "upload-release-asset",
                "uses": "actions/upload-release-asset@v1",
                "env": {
                        "GITHUB_TOKEN": "${{secrets.GITHUB_TOKEN}}"
                },
                "with": {
                    "upload_url": "${{steps.create_release.outputs.upload_url}}",
                    "asset_path": "./elkeid_driver.zip",
                    "asset_name": "elkeid_driver.zip",
                    "asset_content_type": "application/zip"
                },
            })
        ]
    }
)

total_jobs_list = []
for each in all_vms:
    if each not in black_list:
        total_jobs_list.append("build_"+each)
create_release_job.update({"needs": total_jobs_list})

total_jobs = OrderedDict({})

all_vms.sort()

for each in all_vms:
    if each not in black_list:
        tmp_job = gen_job(each)
        total_jobs.update({"build_"+each: tmp_job})

total_jobs.update({"release_all": create_release_job})


yaml_cfg.update({"jobs": total_jobs})


def represent_dictionary_order(self, dict_data):
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    yaml.add_representer(OrderedDict, represent_dictionary_order)


setup_yaml()
config_data = yaml.dump(yaml_cfg, default_flow_style=False)
config_data = config_data.replace("'", "")

with open(".github/workflows/Elkeid.yml", "w") as f:
    f.write(config_data)
