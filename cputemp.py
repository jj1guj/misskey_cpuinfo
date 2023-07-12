import argparse
import datetime
import yaml
import json
import urllib3
import os

parser = argparse.ArgumentParser(description="post CPU temperature to misskey server.")
parser.add_argument("config_file", help="configure file path.")
args = parser.parse_args()

def get_cpu_temp():
    cpu_temp_file = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(cpu_temp_file):
            with open(cpu_temp_file, "r") as f:
                return str(int(f.readline())/1000)
    return None

# make requestbody
def requestbody(api_key, cpu_temp):
    dt_now = datetime.datetime.now().isoformat()
    return json.dumps({
        "i": api_key,
        "text": "{}\nCPU temp: {}".format(dt_now, cpu_temp)
    }).encode("utf-8")
    
# post CPU temperature
def post(api_key, server_host, cpu_temp):
    http = urllib3.PoolManager()
    resp = http.request(
        "POST",
        "https://{}/api/notes/create".format(server_host),
        body=requestbody(api_key, cpu_temp),
        headers={"Content-Type": "application/json"}
    )
    
    if resp.status == 200:
        return 0
    return 2

def main():
    if os.path.exists(args.config_file):
        # load config
        with open(args.config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # get CPU temp
        cpu_temp = get_cpu_temp()
        
        if not cpu_temp:
            return 1
        
        return post(config["api_key"], config["server_host"], cpu_temp)
    return -1

if __name__ == "__main__":
    main()