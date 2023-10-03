
import argparse
from AutoApplier import AutoApplier
import glob
import yaml
#====#

parser = argparse.ArgumentParser()
parser.add_argument("-l" , "--list", help="open links from list located in ./links/" , action="store_true", default=False)
args = parser.parse_args()

if __name__ == '__main__':
    config = yaml.safe_load(open("config.yml"))
    profile = yaml.safe_load(open("profile.yml"))

    autoapp = AutoApplier(config=config, profile=profile)
    
    link = ["https://boards.greenhouse.io/veeventures/jobs/4504805003"]
    autoapp.setup_firefox()
    autoapp.openLinks(link)
    autoapp.doApp(window_handle=autoapp.browser.window_handles[-1])
    
    
    