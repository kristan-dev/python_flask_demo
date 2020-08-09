#%%
import logging
import yaml
import os

#if you want to utilize a config file try this.

def parse_config():
    config_path = "conf/config.yml"
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, config_path)) as file:
        cfg = yaml.load(file, Loader=yaml.FullLoader)

    return cfg

cfg = parse_config()

#db_config = {"registry": cfg["databases"]["registry"]}
