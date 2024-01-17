import os
from os import path
import subprocess
import shutil
class ApptainerManager:

    def __init__(self,planner_name: str, recipe_name: str) -> None:
     self.project_path = self.found_project_path()
     self.folder_path = self.project_path+"/apptainer_planner"
     self.planner_name = planner_name
     self.planner_path = self.folder_path+""+self.planner_name
     self.recipe_name = recipe_name
     self.recipe_path = self.is_file_in_project(self.project_path,recipe_name)
     self.planner_str = planner_name +" "+self.recipe_path
# project_path sarà il percorso radice del progetto in cui sono contenuti tutti i file
# folder_path sarà il percorso dove vengono salvati i planner apptainer
# planner_name sarà il nome del planner --> es: enhsp
#
#
     
    def found_project_path(self):
        input_string = os.path.abspath("planning-experiments")
        last_dash_index = input_string.rfind("/")
        result = input_string[:last_dash_index]
        return result
    
# Specifica il nome della cartella radice del progetto 
    def apptainer_folder_manage(self, folder_path: str):
        if not path.isdir(folder_path):
            os.makedirs(folder_path)

    def is_dir_in_project(self, project_path: str, file_name: str):
        for root, dirs, files in os.walk(project_path):
            if file_name in dirs:
                return os.path.join(root,file_name)
        return None
    
    def is_file_in_project(self, project_path: str, file_name: str):
        for root, dirs, files in os.walk(project_path):
            if file_name in files:
                return os.path.join(root,file_name)
        return None


    def apptainer_planner_manage(self): 
        self.apptainer_folder_manage(self.folder_path) 
        sandbox_path = self.is_dir_in_project(self.project_path, self.planner_name)
        if sandbox_path is None:
            self.apptainer_planner_install(self.folder_path,self.planner_str)
        else: 
            try:
                destination_path = os.path.join(self.folder_path,self.planner_name)
                shutil.move(sandbox_path, destination_path )
            except FileNotFoundError:
                print("file non trovato")
            except Exception as e:
                print ("errore durante lo spostamento")
    # 
    # planner_sif è ad esempio enshp.sif
    # planner_sif_install_str è ad esempio enshp.sif docker:ecc
    # planner_path è ad esempio /examples/apptainer_planner/enshp.sif
    # folder_path è ad esempio /examples/apptainer_planner
    #  
    def apptainer_planner_install(self,folder_path :str, planner_sif_install_str: str):
        command = f"apptainer build --sandbox {folder_path}/{planner_sif_install_str} "
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
    test = ApptainerManager("enhsp","Apptainer.enhsp")
    test.apptainer_planner_manage()
if __name__ == "__main__":
    main()