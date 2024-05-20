import csv
import os
import subprocess
import sys
import json
import time

def get_mid_dir(path):
    path_components = path.split(os.path.sep)
    filename = path_components[-1]
    # remove file extension
    path_components[-1] = filename.split(".")[0]
    joined_path = os.path.sep.join(path_components[-2:])
    return joined_path

def run_elysium(path, contract, outdir, stderr_file, stdout_file):
    command = f"python3 elysium/elysium.py -s {path} -c {contract} -O {outdir} --cfg"

    start_time = time.time()
    with open(stdout_file, 'w') as stdout_f, open(stderr_file, 'w') as stderr_f:
        try:
            result = subprocess.run(command, shell=True, stdout=stdout_f, stderr=stderr_f, timeout=60*30)
        except subprocess.TimeoutExpired:
            return -1, -1

    elapsed_time = time.time() - start_time
    return result.returncode, elapsed_time

def use_solc(version):
    components = version.split(".")
    if eval(components[1]) <= 4 and eval(components[2]) < 12:
        version = '0.4.12'
    install = f"solc-select install {version}"
    use = f"solc-select use {version}"
    try:
        process = subprocess.run(install, shell=True, check=True)
        process = subprocess.run(use, shell=True, check=True)

        return process.returncode == 0
    except:
        return False

def process_entry(path, contract, outdir, version):

    mid = get_mid_dir(path)
    results_dir = outdir
    outdir = os.path.join(outdir, mid)
    os.makedirs(outdir, exist_ok=True)
    ret = use_solc(version)
    if not ret:
        print("Failed to install or use Solidity version", version)
        return_code = -1
        elapsed_time = -1
    else:
        filename = path.split("/")[-1]
        stderr_file = os.path.join(outdir, filename.replace(".sol", ".log"))
        stdout_file = os.path.join(outdir, filename.replace(".sol", ".out"))

        return_code, elapsed_time = run_elysium(path, contract, outdir, stderr_file, stdout_file)

    csv_file = os.path.join(results_dir, 'results.csv')
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['path', 'contract', 'return_code']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
                'path': path,
                'contract': contract,
                # 'elapsed_time': elapsed_time,
                'return_code': return_code
            })

def main():

    if len(sys.argv) != 3:
        print("Usage: python run_on_smartbugs.py <smartbugs_directory> <output_directory>")
        sys.exit(1)

    smartbugs_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Load JSON file
    vuln_json = smartbugs_dir + "/vulnerabilities.json"
    with open(vuln_json, 'r') as file:
        data = json.load(file)

    # Iterate over entries and call npm run dev
    for entry in data:
        path = smartbugs_dir + "/" + entry.get('path')
        contract = entry.get('contract_names')[0]
        version = entry.get('pragma')
        if path and contract:
            process_entry(path, contract, output_dir, version)
        else:
            print("Invalid entry in JSON:", entry)
        

if __name__ == "__main__":
    main()