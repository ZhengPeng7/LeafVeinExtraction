import cv2


def save_split_leaves(leaves_all, leaves_source, path=r'./'):
    if path[-1] != '/':
        path += '/'
    counter = 0
    for i in leaves_all:
        cv2.imwrite(path + 'seg' + leaves_source.rpartition('/')[-1] + '_' + str(counter) + '.jpg', i)
        counter += 1
