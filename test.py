
import argparse
from AutoApplier import AutoApplier
import glob
import yaml
#====#

parser = argparse.ArgumentParser()
#TODO: putting a pin in this for now, will come back to it later
parser.add_argument("-l" , "--list", help="open links from list located in ./links/ {CURRENTLY INACTIVE}" , action="store_true", default=False)
parser.add_argument("-u" , "--url", help="open links from url", default=False)
args = parser.parse_args()

if __name__ == '__main__':
    config = yaml.safe_load(open("config.yml"))
    profile = yaml.safe_load(open("profile.yml"))

    autoapp = AutoApplier(config=config, profile=profile)
    
    if args.list:
        links = glob.glob("./links/*.txt")
        autoapp.apply(links)
    elif args.url:
        url = args.url
        print(f"Applying to links from {url}")
        
        autoapp.apply(url=url)
        
        
    
    
    