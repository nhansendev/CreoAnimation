import creopyson
import cv2
import os
import numpy as np

c = creopyson.Client()
c.connect()
creopyson.creo_set_creo_version(c, 13)

c.creo_cd('D:/CreoProjects/Pump/animation/')

model_name = c.file_get_active()['file']
current_folder = c.creo_pwd()

image_names = []
count = 0
for i in np.linspace(-45, 45, 100) % 360:
    c.file_relations_set(model_name, [f'd21:481={i}']) # set new relation value
    c.file_regenerate(model_name) # force regeneration
    imname = f'render_{count}.jpg' # keep track of generated image names
    image_names.append(imname)
    c.interface_export_image('JPEG', model_name, imname, height=12, width=16) # capture a jpeg of the current screen
    count += 1

# Setup and Create Video
first_image = cv2.imread(os.path.join(current_folder, image_names[0]))
height, width, _ = first_image.shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
video = cv2.VideoWriter(os.path.join(current_folder, 'animation.mp4'), fourcc, 45, (width, height))

for image_file in image_names:
    image_path = os.path.join(current_folder, image_file)
    frame = cv2.imread(image_path)
    video.write(frame)

video.release()
cv2.destroyAllWindows()

# Done!
