import json
import os
import argparse
import random
import glob
import pprint

def experiments(prefix=".."):
    return [os.path.split(x)[-1] for x in glob.glob(os.path.join(prefix, "data-3-30/logs/*"))]

def paths_from_id(experiment_id, prefix=".."):
    log_path = "data-3-30/logs/{}/aligned-observations.json".format(experiment_id)
    screenshot_path = "data-3-30/screenshots/{}/".format(experiment_id)
    return os.path.join(prefix, log_path), os.path.join(prefix, screenshot_path)

def load(experiment_id, prefix):
    log_path, screenshot_path = paths_from_id(experiment_id, prefix)
    print("Loading data from: {}", log_path)
    with open(log_path,"rb") as fh:
        data = json.loads(fh.read())
        last_blocks = set()
        last_chat_history_length = 0
        for world_state in data['WorldStates']:
            #print(world_state['BuilderPosition'])
            if world_state['Screenshots']['Builder']:
                world_state['builder_view'] = screenshot_path + world_state['Screenshots']['Builder']
            #print(world_state['Screenshots'])
            if world_state['Screenshots']['Architect']:
                world_state['architect_view'] = screenshot_path + world_state['Screenshots']['Architect']
            #print(world_state['ChatHistory'][last_chat_history_length:])
            last_chat_history_length = len(world_state['ChatHistory'])
            blocks = set([((position['X'], position['Y'], position['Z']),color) for position,color in [(block['AbsoluteCoordinates'], block['Type']) for block in world_state['BlocksInGrid']]])
            added_blocks = blocks - last_blocks
            removed_blocks = last_blocks - blocks
            world_state['blocks_added'] =added_blocks
            world_state['blocks_removed'] = removed_blocks
            last_blocks = blocks
            yield world_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'MinecraftViz',
                        description = 'visualize minecraft experiment data')
    parser.add_argument('--path', type=str, default=".",
                    help='path to experiment data')
    parser.add_argument('--experiment', type=str,
                    help='experiment id')
    parser.add_argument('--step', type=int, default=0,
                    help='starting dialog step')
    args = parser.parse_args()
    if args.experiment:
        experiment_id = args.experiment
    else:
        print("No experiment specified, picking a random one")
        experiment_id = random.choice(experiments(".."))
    points = [p for p in load(experiment_id, args.path)]
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(points)
