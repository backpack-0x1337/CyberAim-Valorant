from roboflow import Roboflow
rf = Roboflow(api_key="KxQLXJZVvfqOwOBriMFR")
project = rf.workspace().project("valorant-object-detection")
dataset = project.version(1).download("yolov5")


#python3 train.py --img 650 --batch 64 --epochs 700 --data ../data.yaml --weights 'yolov5l.pt' --cache --nosave --name valorant_scratch
#python3.9 train.py --img 650 --batch 32 --epochs 500 --data ../data.yaml --weights yolov5l.pt --cache --nosave --name valorant_scratch
#python3.9 train.py --img 672 --batch 8 --epochs 250 --data ../data.yaml --weights yolov5s.pt --nosave --name valorant_scratch

