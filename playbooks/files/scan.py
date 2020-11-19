import os

import yaml


def scan():
    output = {}
    for root, dirs, files in os.walk("../orgs"):
        for file in files:
            a_yaml_file = open(os.path.join(root, file))
            parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
            parent = os.path.basename(os.path.abspath(os.path.join(root, os.pardir)))
            if parent in output:
                output[parent].update({os.path.basename(root): parsed_yaml_file})
            else:
                output.update({parent: {os.path.basename(root): parsed_yaml_file}})
    return print(output)


if __name__ == '__main__':
    scan()
