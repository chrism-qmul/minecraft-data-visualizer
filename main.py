import data
from app import App
import argparse
import random

def convert_point(point):
    x = point.get("BuilderPosition").get("X")
    y = point.get("BuilderPosition").get("Y")+0.56
    z = point.get("BuilderPosition").get("Z")#+0.8
    yaw = point.get("BuilderPosition").get("Yaw")+90
    pitch = point.get("BuilderPosition").get("Pitch")*-1
    world = [(xyz['X'], xyz['Y']-1, xyz['Z']) for xyz in [p['AbsoluteCoordinates'] for p in point['BlocksInGrid']]]
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
    args = parser.parse_args()
    if args.experiment:
        experiment_id = args.experiment
    else:
        print("No experiment specified, picking a random one")
        experiment_id = random.choice(data.experiments(".."))
    points = [convert_point(p) for p in data.load(experiment_id, args.path) if is_valid_point(p)]
    app = App(points, args.step)
    app.run()
