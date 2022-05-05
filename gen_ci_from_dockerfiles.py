import yaml
import os
from collections import OrderedDict


all_dockers = os.listdir("dockerfiles")

black_list = []

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
                    "name": "Set up Docker Buildx "+vmname,
                    "uses": "docker/setup-buildx-action@v1"
                }),
                OrderedDict({
                    "name": "Build "+vmname,
                    "uses": "docker/build-push-action@v2",
                    "with": {
                        "file": "dockerfiles/Dockerfile."+vmname,
                        "load": True,
                        "tags": "elkeid_driver/"+vmname+":latest"
                    }
                }),
                OrderedDict({
                    "name": "Extract "+vmname,
                    "id": "extract-"+vmname,
                    "uses": "shrink/actions-docker-extract@v1",
                    "with": {
                        "image": "elkeid_driver/"+vmname+":latest",
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
                "branches": "[ main ]"
            }
        }
    }
)

total_jobs = OrderedDict({})

all_vms.sort()

for each in all_vms:
    if each not in black_list:
        tmp_job = gen_job(each)
        total_jobs.update({"build_"+each: tmp_job})


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
