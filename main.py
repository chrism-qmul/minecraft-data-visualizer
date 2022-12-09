import data
from app import App
import argparse
import random

block_types = {"cwc_minecraft_green_rn": (0,1,0,1),
    "cwc_minecraft_red_rn": (1,0,0,1),
    "cwc_minecraft_blue_rn": (0,0,1,1),
    "cwc_minecraft_yellow_rn": (1, 1, 0, 1),
    "cwc_minecraft_orange_rn": (1,0.5,0,1),
    "cwc_minecraft_purple_rn": (0.5,0,0.5,1)}

def block_type_to_color(block_type):
    if block_type not in block_types:
        print("warning, no color for: ", block_type)
    return block_types.get(block_type, (0.5,0.5,0.5,1))

def convert_point(point):
    x = point.get("BuilderPosition").get("X")
    y = point.get("BuilderPosition").get("Y")+0.55
    z = point.get("BuilderPosition").get("Z")
    yaw = point.get("BuilderPosition").get("Yaw")+90
    pitch = point.get("BuilderPosition").get("Pitch")*-1
    world = [((xyz['X'], xyz['Y']-1, xyz['Z']),block_type_to_color(block_type)) for xyz,block_type in [(p['AbsoluteCoordinates'],p['Type']) for p in point['BlocksInGrid']]]
    return {"builder_position": {"x": x, "y": y, "z": z, "yaw": yaw, "pitch": pitch}, "world": world, "view": point.get("builder_view")}

def is_valid_point(point):
    return point.get("BuilderPosition") and point.get

#    test_point = [{"builder_position": {"x": 0, "y": 2, "z":10, "yaw": -90.0, "pitch": -10}, "world": [(0,0,0),(1,1,0),(2,2,0),(1,3,0),(0,4,0),(0,2,0)]}]

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog = 'MinecraftViz',
                        description = 'visualize minecraft experiment data')
    parser.add_argument('--path', type=str, default=".",
                    help='path to experiment data')
    parser.add_argument('--experiment', type=str,
                    help='experiment id')
    parser.add_argument('--step', type=int, default=0,
                    help='starting dialog step')
    parser.add_argument('--export', action="store_true",
                    help='export screenshot only')
    parser.add_argument('--exportall', action="store_true",
                    help='export all screenshots')
    args = parser.parse_args()
    if args.experiment:
        experiment_id = args.experiment
    else:
        print("No experiment specified, picking a random one")
        experiment_id = random.choice(data.experiments(".."))
    points = [convert_point(p) for p in data.load(experiment_id, args.path) if is_valid_point(p)]
    app = App(points, args.step)
    if args.export:
        filename = "{}_{}.png".format(experiment_id, app.current_step)
        app.run_to_file(filename)
    elif args.exportall:
        while True:
            filename = "{}_{}.png".format(experiment_id, app.current_step)
            print("exporting {}".format(filename))
            app.run_to_file(filename)
            if not app.next_dialog_step():
                break
    else:
        app.run()
