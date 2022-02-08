import torch

# model
model = torch.hub.load("ultralytics/yolov5", "yolov5l")
model.conf = 0.3
# Images
img = 'my_desktop.jpg'

# Inference
results = model(img)

# Result
results.print()
results.show()




