import sys


def main(args):
    cfg = args[1]
    name = cfg.NAME
    path_to_domains = cfg.PATH_TO_DOMAINS
    path_to_results = cfg.PATH_TO_RESULTS
    planners_x_domains = cfg.PLANNERS_X_DOMAINS
    print(name)


if __name__ == '__main__':
    main(sys.argv)