import os


all_dockers = os.listdir("dockerfiles")

black_list = ["rhel7_elrepo", "rhel8_elrepo", "rhel6"]

all_vms = []

default_path = "/ko_output/."
destination = "./output"

for each_dockers in all_dockers:
    each_dockers = each_dockers.replace("Dockerfile.", "")
    if each_dockers not in black_list:
        all_vms.append("kulukami/elkeid_driver_" + each_dockers
                       + ":latest")

print("mkdir output")
counter = 0
for each in all_vms:
    print(
        "docker cp $(docker create {image}):/{path} {destination}".format(image=each, path=default_path, destination=destination))
    counter += 1
    if counter % 7 == 0:
        print(
            '''docker rmi  $(docker images | grep "kulukami/elkeid_driver" | awk '{print $3}') # 清理磁盘''')


if counter % 7 != 0:
    print(
        '''docker rmi  $(docker images | grep "kulukami/elkeid_driver" | awk '{print $3}') # 清理磁盘''')
