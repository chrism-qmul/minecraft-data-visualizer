import json
#experiment_id = "B1-A3-C2-1522434666266"
experiment_id = "B3-A2-C14-1522444981929"
log_path = "../data-3-30/logs/{}/aligned-observations.json".format(experiment_id)
screenshot_path = "../data-3-30/screenshots/{}/".format(experiment_id)


def load(log_path):
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
            blocks = set([(block['X'], block['Y'], block['Z']) for block in [block['AbsoluteCoordinates'] for block in world_state['BlocksInGrid']]])
            added_blocks = blocks - last_blocks
            removed_blocks = last_blocks - blocks
            world_state['blocks_added'] =added_blocks
            world_state['blocks_removed'] = removed_blocks
            last_blocks = blocks
            yield world_state
