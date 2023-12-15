import os
from os import path
import subprocess
import shutil

def apptainer_folder_manage(folder_path: str):
     if not path.isdir(folder_path):
        os.makedirs(folder_path)

def is_file_in_project(project_path: str, file_name: str):
    for root, dirs, files in os.walk(project_path):
        if file_name in files:
            return os.path.join(root,file_name)
    return None


def apptainer_planner_manage(project_path: str, planner_path: str,planner_sif: str, planner_sif_install_str: str, folder_path: str): 
    apptainer_folder_manage(folder_path) 
    sif_path = is_file_in_project(project_path, planner_sif)
    if sif_path is None:
        apptainer_planner_install(folder_path,planner_sif_install_str)
    else: 
        try:
            destination_path = os.path.join(folder_path,planner_sif)
            shutil.move(sif_path, destination_path )
        except FileNotFoundError:
            print("file non trovato")
        except Exception as e:
            print ("errore durante lo spostamento")
# 
# planner_sif è ad esempio enshp.sif
# planner_sif_install_str è ad esempio enshp.sif docker:ecc
# planner_path è ad esempio /examples/apptainer_planner/enshp.sif
#w folder_path è ad esempio /examples/apptainer_planner
#  
def apptainer_planner_install(folder_path :str, planner_sif_install_str: str):
    command = f"apptainer build {folder_path}/{planner_sif_install_str}"
    print(command)
    try:
        subprocess.run(command, shell=True, check=True)
        print("planner installed sucefully")
    except subprocess.CalledProcessError as e:
        print(f"Error during the installation with apptainer: {e}")

# esempio call apptainer_planner_manage(project_path, planner_path, "enhsp.sif", "enhsp.sif docker://enricos83/enhsp:latest",folder_path)
# ove project_path = "/Users/mattiatanchis/TESI/planning-experiments", 
# planner_path = "/Users/mattiatanchis/TESI/planning-experiments/apptainer_planner/enshp.sif"
# floder_path = "/Users/mattiatanchis/TESI/planning-experiments/apptainer_planner"

def main():
    project_path = os.path.dirname(os.getcwd())
    file_name = "enhsp.sif"
    folder_path = os.path.join(project_path,"apptainer_planner") 
    planner_path= os.path.join(folder_path,file_name)
    print(planner_path)
    apptainer_planner_manage(project_path,planner_path,file_name,"enhsp.sif docker://enricos83/enhsp:latest",folder_path)

if __name__ == "__main__":
    main()
