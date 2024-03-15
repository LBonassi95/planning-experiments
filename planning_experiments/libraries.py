##This code allows the installation of the necessary libraries
import subprocess
import sys

def install_library(library_name):
    try:
        #Check if the library is installed
        import_module = __import__(library_name)
        print(f"Library {library_name} is already installed")
    except ImportError:
        ##Library isn't installed, try to install it
        try:
            subprocess.check_call([sys.executable, "-m","pip","install",library_name])
            print(f"Installation of {library_name} completed successfully")
        except Exception as e:
            print(f"There is an error during the installation of {library_name} : {str(e)}")


# tqdm, tabulate, pandas, click