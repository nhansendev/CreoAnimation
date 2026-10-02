# CreoAnimation
Basic guide and script for animating assemblies in PTC Creo using Python, via [creopyson](https://pypi.org/project/creopyson/) and [CREOSON](https://github.com/SimplifiedLogic/creoson/releases).
Installing [Open CV](https://github.com/opencv/opencv-python) is recommended for streamlined conversion of images to videos


## Motivation
One fundamental problem with creating simple animations in PTC Creo is that there is no option to force a regeneration on each frame. This means that objects with non-rigid geometry, cross-sections, etc. do not update their appearance appropriately.

A simple example of that can be seen here, where a worm gear assembly has been sectioned and animated using Creo's Mechanism tools (notice how the cross-section is not updated correctly as the gears rotate):
<img width="960" height="512" alt="WORM_GEAR_TEST_ASM" src="https://github.com/user-attachments/assets/d374b379-d30b-4b1a-afa8-b01196ef63d2" />

Using a scripted approach we can force Creo to regenerate, allowing great flexibility in what can be animated:
<img width="800" height="600" alt="animation_5" src="https://github.com/user-attachments/assets/10facb58-605a-49b0-84e3-33bcd1625ce6" />
<img width="800" height="600" alt="animation_8" src="https://github.com/user-attachments/assets/a11a1a5e-cbaf-45dc-8b67-9a6f4362db55" />
<img width="1280" height="720" alt="animation_3 (1)" src="https://github.com/user-attachments/assets/661cf8fb-4737-434a-b93c-7a2989c5416f" />

## Setup
The general setup process is as follows:
1. Ensure your instance of Creo has been installed with support for Jlink, which CREOSON uses to communicate with Creo
2.  <img width="609" height="481" alt="image" src="https://github.com/user-attachments/assets/05441c84-ad0b-4668-8599-ea417190ef62" />
3. Setup CREOSON server: follow instructions from the [CREOSON Github](https://github.com/SimplifiedLogic/creoson), which is basically "extract zip and run server"
4. To use with Python, install [creopyson](https://pypi.org/project/creopyson/): `pip install creopyson`
5. Optionally, if you want an easy way to convert captured images to videos, install [Open CV](https://github.com/opencv/opencv-python): `pip install opencv-python`
6. Test: you should now be able to open an instance of Creo, run the server, and try connecting via Python

```
import creopyson

c = creopyson.Client()
c.connect()
creopyson.creo_set_creo_version(c, 13) # use your major version of Creo 13.4.0 -> 13

model_name = c.file_get_active()['file']
print(model_name)
```

Note that by default the script will export images to somewhere in User/Documents, which can be updated via "creo_cd":
Ex: `c.creo_cd('D:/CreoProjects/Pump/animation/')`

## Example
For something simple like animating this flexible tube (defined as a sweep in the assembly), we just need to set a relation that adjusts a dimension of interest:
<img width="1518" height="395" alt="image" src="https://github.com/user-attachments/assets/76b4b564-f6ad-4a84-8869-b8c6f67ac8d7" />
Here, the dimension is "d21:481", which we can add a relation for and repeatedly set via a script to any value we want, then regenerate and capture an image:

```
import creopyson
import cv2
import os
import numpy as np # for convenience, but can be replaced with pure python

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
```
<img width="800" height="600" alt="animation_9 (1)" src="https://github.com/user-attachments/assets/7b8dbc59-1d45-4a0f-b727-801f19d8c3e8" />

## Example 2: Mechanism Integration
It's also possible to apply this method to assemblies that use Mechanism constraints, though it requires the use of a reference component/plane/etc.

In this example we want to set the rotation of the gears, but since we can't directly set rotation/translation of a mechanism constraint, we can do the next-best thing and set it to *match* the rotation of a reference plane or object.
Here a nut is used as our reference point, which uses default constraints including one angle offset, which can be adjusted via relations like before.
Setting the mechanism constraint to use the nut's plane as its reference for "zero" means that if we rotate the nut and regenerate, then the gear rotates to match:
<img width="1088" height="824" alt="image" src="https://github.com/user-attachments/assets/45e35a01-1e74-4429-9ab4-e053cfbba8b5" />
<img width="966" height="498" alt="image" src="https://github.com/user-attachments/assets/4b56aad0-cc98-46ba-9089-5e3fb4aacebc" />

We can then run the same script as before, with updated angle range and the relation to match (`f'd15:129={i}'`):
<img width="800" height="600" alt="animation_10 (1)" src="https://github.com/user-attachments/assets/a8605005-4746-41c2-97e5-8c5d73a9811a" />
