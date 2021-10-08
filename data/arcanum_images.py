from glob import glob
import random
import cv2
import tqdm
import multiprocessing

def get_filenames(file_patterns):
    image_paths = [file_path for file_pattern in file_patterns for file_path in glob(file_pattern, recursive=True)]
    image_paths = _reduce_filenames(image_paths)
    random.shuffle(image_paths)
    # 90% train images and 10% test images
    n_train_samples = int(len(image_paths) * 0.9)
    train_filenames = image_paths[:n_train_samples]
    test_filenames = image_paths[n_train_samples:]

    return train_filenames, test_filenames

def check_img_path(img_path):
    image = cv2.imread(img_path)
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return True
    except:
        print('Problem with path: ', img_path)
        return False

def _reduce_filenames(image_paths):
    reduced_paths = []
    for img_path in tqdm.tqdm(image_paths):
        if check_img_path(img_path):
            reduced_paths.append(img_path)
    return reduced_paths

