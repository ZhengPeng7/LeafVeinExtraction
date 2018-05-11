import cv2
import numpy as np
import matplotlib.pyplot as plt
import get_images
import local_enhancement
import os
import shutil
import split_leaves
import save_split_leaves
import cut_out_corrected_img
import show_images
import extract_vein_by_region_grow
import get_angle_vertical
from skimage import morphology
import get_top_and_bottom
import get_curvature
import save_in_csv_and_xlsx


# Get Corrected_after Leaves Begin
# clear "split_after" directory
if os.path.isdir(r'./split_after'):
    if os.listdir(r'./split_after'):
        shutil.rmtree(r'./split_after')
        os.mkdir(r'./split_after')

# clear "corrected_after" directory
if os.path.isdir(r'./corrected_after'):
    if os.listdir(r'./corrected_after'):
        shutil.rmtree(r'./corrected_after')
        os.mkdir(r'./corrected_after')

# get images
leave_split_before = get_images.get_images(r'./split_before')[0]
leaves_split = split_leaves.split_leaves(leave_split_before)
save_split_leaves.save_split_leaves(leaves_split, leave_split_before, r'./split_after')
images = sprted(get_images.get_images(r'./split_after'))

imgs_rotated = []
imgs_shape = []

for image in images:
    print('Straightening {}'.format(image))
    img_rotated_cut = cut_out_corrected_img.cut_out_corrected_img(image)
    cv2.imwrite(r'./corrected_after/'+image.rpartition('/')[-1].rpartition('.')[-3][-1]+'.jpg', img_rotated_cut)
    imgs_rotated.append(img_rotated_cut)
    imgs_shape.append(img_rotated_cut.shape)

column = 5
img_joined = show_images.show_images(imgs_rotated, imgs_shape, column, alignment='left')
img_ori = cv2.imread(leave_split_before)
# Get Corrected_after Leaves Begin

images = sorted(get_images.get_images(r'./corrected_after/'))

edges_canny = []
edges_equalized = []
edges_canny_shape = []
edges_equalized_shape = []

for image in images:
    img, img_equalized, edge_canny, edge_equalized = local_enhancement.local_enhancement(image)
    edges_canny.append(edge_canny)
    # edges_equalized.append(edge_equalized)
    edges_canny_shape.append(edge_canny.shape)
    # edges_equalized_shape.append(edge_equalized.shape)
    # plt.imshow(edge_canny, plt.cm.gray)
    # plt.show()

column = 5
edge_canny_joined = show_images.show_images(edges_canny, edges_canny_shape, column, alignment='left')
# edge_equalized_joined = show_images.show_images(edges_equalized, edges_equalized_shape, column, alignment='left')


# Extract main vein
main_veins = []
veins = []
main_veins_points = []
veins_points = []
main_veins_shape = []
veins_shape = []
veins_bgr = []
veins_bgr_shape = []
imgs = []
imgs_shape = []
tops = []
bottoms = []
curvatures = []
all_angles = []     # angles in all leaves
for i in range(len(edges_canny)):
    print('Extracting {}'.format(images[i]))
    vein, main_vein, vein_points, main_vein_points = \
        extract_vein_by_region_grow.extract_vein_by_region_grow(edges_canny[i], images[i], 150, (15, 15))

    # COLORIZATION BEGIN
    other_vein = cv2.subtract(vein, main_vein)
    _, contours, hierarchy = cv2.findContours(other_vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_perimeters = [j for j in contours if len(j) < 50]  # 删短周长的区域
    cv2.fillPoly(other_vein, small_perimeters, 0)
    other_vein_bgr = cv2.cvtColor(other_vein, cv2.COLOR_GRAY2BGR)
    _, contours, hierarchy = cv2.findContours(other_vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    color_choice = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 144, 30),
                    (0, 90, 139), (130, 0, 75), (34, 128, 34), (118, 16, 205), (0, 118, 238), (139, 236, 255)]
    masks = []
    individual_branchs = []
    for j in range(10):
        color_choice.append(np.random.randint(0, 255, size=(1, 3))[0].tolist())
    for c in range(len(contours)-1, -1, -1):
        if cv2.arcLength(contours[c], True) < 100:
            contours.pop(c)
    # Append curvatures
    curvatures.append([])
    for c in contours:
        curvatures[-1].append(np.mean(get_curvature.get_curvature(np.squeeze(c))))

    for c in range(len(contours)):
        cv2.fillPoly(other_vein_bgr, [contours[c]], color_choice[c])
        t = np.zeros_like(other_vein_bgr, dtype=np.uint8)
        for j in range(other_vein_bgr.shape[0]):
            for k in range(other_vein_bgr.shape[1]):
                if other_vein_bgr[j][k].tolist() == list(color_choice[c]):
                    t[j][k] = [255, 255, 255]
        individual_branchs.append(t.copy())
    pts = []
    for c in range(len(contours)+1):
        pts.append([])
        if c == 0:
            skin = morphology.skeletonize((main_vein / 255).astype(np.uint8)) * 255
        else:
            gray = cv2.cvtColor(individual_branchs[c-1], cv2.COLOR_RGB2GRAY)
            ret, thr = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            skin = morphology.skeletonize((thr / 255).astype(np.uint8)) * 255
        for j in range(skin.shape[0]):
            for k in range(skin[i].shape[0]):
                if skin[j][k]:
                    pts[c].append([j, k])
    pts = np.array(pts)
    angles = []
    text_places = []
    for j in range(len(pts)):
        if j == 0:
            current_angle = get_angle_vertical.get_angle_vertical(pts[j])
        else:
            current_angle = get_angle_vertical.get_angle_vertical(pts[j], angles[0])
        # print('current_angle:', current_angle)
        angles.append(current_angle)
        text_places.append(pts[j][np.argmin(np.array(pts[j])[:, 0])])
    # print("text_places:", text_places)
    main_vein_bgr = cv2.cvtColor(main_vein, cv2.COLOR_GRAY2BGR)
    vein_bgr = cv2.add(main_vein_bgr, other_vein_bgr)
    for j in range(len(pts)):
        cv2.putText(vein_bgr, str(angles[j])[:str(angles[j]).find('.') + 3],
                    (min(vein_bgr.shape[0]-100, max(50, text_places[j][1]-30)),
                     min(vein_bgr.shape[1]-50, max(30, text_places[j][0]))),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (111, 222, 111), thickness=2)
    # fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    # ax.imshow(vein_bgr, cmap="gray")
    # plt.title('Colored Veins with Angles')
    # plt.show()
    # COLORIZATION END

    # get top and bottom begin.
    img = cv2.imread(images[i])
    top, bottom = get_top_and_bottom.get_top_and_bottom(images[i], angles[0])
    tops.append(top)
    bottoms.append(bottom)
    cv2.circle(img, top[::-1], 10, (0, 0, 255), thickness=7)
    cv2.circle(img, bottom[::-1], 10, (0, 0, 255), thickness=7)
    imgs.append(img)
    imgs_shape.append(img.shape)
    # get top and bottom end
    veins.append(vein)
    veins_shape.append(vein.shape)
    veins_points.append(vein_points)
    main_veins.append(main_vein)
    main_veins_shape.append(main_vein.shape)
    main_veins_points.append(main_vein_points)
    veins_bgr.append(vein_bgr)
    veins_bgr_shape.append(vein_bgr.shape)
    all_angles.append(angles)

for i in range(len(images)):
    image = [images[i] for j in range(len(curvatures[i]))]
    save_in_csv_and_xlsx.save_in_csv_and_xlsx(image, curvatures[i], all_angles[i])
save_in_csv_and_xlsx.csv2xlsx("curvatures_and_angles.csv")

column = 5
vein_joined = show_images.show_images(veins, veins_shape, column, alignment='left')
main_vein_joined = show_images.show_images(main_veins, main_veins_shape, column, alignment='left')
vein_bgr_joined = show_images.show_images(veins_bgr, veins_bgr_shape, column, alignment='left')
img_joined = show_images.show_images(imgs, imgs_shape, column, alignment='left')

# plt.shows
fig_1, axes_1 = plt.subplots(1, 1, figsize=(16, 8))
axes_1.imshow(edge_canny_joined, plt.cm.gray)
axes_1.set_title('Cannied Edges')
# axes_1.set_axis_off()

fig_2, axes_2 = plt.subplots(1, 1, figsize=(16, 8))
axes_2.imshow(vein_joined, plt.cm.gray)
axes_2.set_title('Veins')
# axes_2.set_axis_off()

fig_3, axes_3 = plt.subplots(1, 1, figsize=(16, 8))
axes_3.imshow(main_vein_joined, plt.cm.gray)
axes_3.set_title('Main Veins')
# axes_3.set_axis_off()

fig_4, axes_4 = plt.subplots(1, 1, figsize=(16, 8))
axes_4.imshow(cv2.cvtColor(vein_bgr_joined, cv2.COLOR_BGR2RGB))
axes_4.set_title('Colored Veins')
# axes_4.set_axis_off()

fig_5, axes_5 = plt.subplots(1, 1, figsize=(16, 8))
axes_5.imshow(cv2.cvtColor(img_joined, cv2.COLOR_BGR2RGB))
axes_5.set_title('Leaves with tops and bottoms')
# axes_5.set_axis_off()

frame = plt.gca()
frame.axes.get_yaxis().set_visible(False)
frame.axes.get_xaxis().set_visible(False)
plt.show()
