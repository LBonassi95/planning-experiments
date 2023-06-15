import sys
import json
import fcntl

def main(argv):
    assert len(argv) == 4, 'Usage: python save_results.py <results_file> <system> <domain> <instance>'
    results_file = argv[0]
    system = argv[1]
    domain = argv[2]
    instance = argv[3]

    file = open(results_file, "r+")

    fcntl.flock(file, fcntl.LOCK_EX)

    json_data = json.load(file)

    stdo_path = json_data[system][domain][instance]['stdo']
    stde_path = json_data[system][domain][instance]['stde']

    stdo_str = open(stdo_path, 'r').read()
    stde_str = open(stde_path, 'r').read()

    json_data[system][domain][instance]['stdo'] = stdo_str
    json_data[system][domain][instance]['stde'] = stde_str

    
    file.seek(0)
    file.truncate()
    json.dump(json_data, file, indent=4)

    fcntl.flock(file, fcntl.LOCK_UN)

    file.close()
    

if __name__ == '__main__':
    main(sys.argv[1:])