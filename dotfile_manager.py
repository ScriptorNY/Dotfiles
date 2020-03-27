import sys
import os
import argparse
import json
import pathlib
import subprocess
import git
import stat
from pathlib import Path
from shutil import copyfile

def init_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--operation', action='store', choices=['save', 'deploy'], required=True)
    parser.add_argument('config_file', nargs='?', default="dotfile_manager_config.json")
    return parser

def save_files(config_files_dict):
    for git_path, local_path in config_files_dict.items():
        if os.path.isfile(local_path):
            git_dir = os.path.dirname(git_path)
            if not os.path.exists(git_dir):
                os.makedirs(git_dir)
            copyfile(local_path, git_path)
        else:
            print("File " + local_path + " not found!", file = sys.stderr)

def deploy_files(config_files_dict):
    for git_path, local_path in config_files_dict.items():
        local_path_tilde = os.path.expanduser(local_path)
        abs_path = pathlib.Path(local_path_tilde).parent.absolute()
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        copyfile(git_path, local_path_tilde)
        if Path(local_path).suffix == ".sh":
            st = os.stat(local_path)
            os.chmod(local_path, st.st_mode | stat.S_IEXEC)

def iterate_through_json_data(json_data, path = os.path.dirname(os.path.realpath(__file__))):
    ret = dict()
    for key in json_data:
        if type(json_data[key]) is dict:
            ret.update(iterate_through_json_data(json_data[key], path + "/" + key))
        elif type(json_data[key]) is str:
            abs_local_path = os.path.expanduser(json_data[key])
            ret[path + "/" + key] = abs_local_path
    return ret

def parse_arguments():
    parser = init_argument_parser()
    args = parser.parse_args()

    return args

def install_yay():
    cwd = os.getcwd()
    yay_git_url = "https://github.com/Jguer/yay"
    yay_clone_path = "/tmp/yay.git"
    
    yay_repo = git.repo.base.Repo(yay_git_url)
    yay_repo.clone(yay_clone_path)
    os.chdir(yay_clone_path)
    subprocess.run(["sudo", "makepkg", "-si"])
    os.chdir(cwd)
    os.rmdir(yay_clone_path)

def install_packages(packages_array):
    cmd = ["sysinstall"]
    for package in packages_array:
        cmd.append(package)
    subprocess.run(cmd)

def configure_xorg():
    subprocess.run(["sudo", "Xorg", ":0", "-configure"])
    subprocess.run(["sudo", "mkdir", "-p", "/etc/X11"])
    subprocess.run(["sudo", "cp", "/root/xorg.conf.new", "/etc/X11/xorg.conf"])
    subprocess.run(["sudo", "setxkbmap", "-layout", "de"])

def run(args):
    config_file = args.config_file
    data = None

    with open(config_file) as f:
        data = json.load(f)
    
    if (not data is None):
        data_files = data["files"]
        json_dict = iterate_through_json_data(data_files)

        if args.operation == "save":
            save_files(json_dict)

        elif args.operation == "deploy":
            data_packages = data["packages"]

            configure_xorg()
            install_yay()
            deploy_files(json_dict)
            install_packages(data_packages)
    else:
        print("ERROR! Config file " + config_file + " not found", file=sys.stderr)

def main():
    args = parse_arguments()
    run(args)

if __name__ == "__main__":
    main()