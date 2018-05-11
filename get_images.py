import os


def get_images(file_path):
    """
    Description: Get file_names from a certain directory and store them into a list.
    :param file_path: file_path
    :return: put all file_names in a list
    """
    if r'/' != file_path[-1]:
        file_path += r'/'
    images = []
    path_dir = os.listdir(file_path)
    for i in path_dir:
        child = os.path.join('%s%s' % (file_path, i))
        images.append(child)

    return images
