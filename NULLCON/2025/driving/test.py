from PIL import Image
import numpy as np

img = Image.open('./driving/result/frames_sum.png').convert("RGBA")
img_array = np.array(img, dtype=np.uint8)

print(img_array[1, 1])
print((img_array[:, :, 3] == 255).all())

mask = (img_array[:, :, 0] >= 10) & (img_array[:, :, 1] >= 10) & (img_array[:, :, 2] >= 10)
img_array[:, :, :3][mask] *= 10
img_array[:, :, :3][mask] += 2

img_array = np.clip(img_array, 0, 255).astype(np.uint8)
Image.fromarray(img_array, mode='RGBA').save('./driving/result/frames.png')