from constants import PLANNERS_FOLDER, SCRIPTS_FOLDER, LOG_FOLDER, RESULTS_FOLDER
import os


def main():
    if not os.path.isdir(PLANNERS_FOLDER):
        os.mkdir(PLANNERS_FOLDER)

    if not os.path.isdir(SCRIPTS_FOLDER):
        os.mkdir(SCRIPTS_FOLDER)

    if not os.path.isdir(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)

    if not os.path.isdir(RESULTS_FOLDER):
        os.mkdir(RESULTS_FOLDER)

    print('Operation Successful!')


if __name__ == '__main__':
    main()
