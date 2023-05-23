import numpy as np
import cv2
import copy


def Average_Image(images):
    width = images[0].shape[1]
    height = images[0].shape[0]
    sum = np.zeros((height, width), dtype=np.float32)
    for i in range(len(images)):
        if (i // 14) % 6 == 0 and i % 14 == 0 and i != 0:
            cv2.waitKey(1)
            cv2.destroyAllWindows()
        # 평균 영상
        sum += np.array(images[i], dtype=np.float32)

        # 출력
        title = f"train{i:03d}.jpg"
        cv2.namedWindow(title)
        cv2.moveWindow(title, (i % 14) * width, (((i // 14) % 6) * (height + 20)))
        cv2.imshow(title, images[i].astype(np.uint8))

    cv2.waitKey(1)
    cv2.destroyAllWindows()

    return sum / len(images)


def Difference_Image(images, average):
    size = average.shape[0] * average.shape[1]
    array_image = np.zeros((size, 1), dtype=np.uint8)
    for i in range(len(images)):
        image = images[i]
        image = image - average
        image = image.reshape(size, 1)
        array_image = np.append(array_image, image, axis=1)
    return np.delete(array_image, 0, axis=1)


def Eigen_Sort(value, vector):
    index = value.argsort()[::-1]
    value_sort = value[index]
    vector_sort = vector[:, index]
    return value_sort, vector_sort


image_count = 310
width = 120
height = 150
size = width * height

image_files = []

for i in range(image_count):
    image = cv2.imread(f"./face_img/train/train{i:03d}.jpg", cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (width, height))
    image_files.append(image)

sum_image = np.zeros((height, width), dtype=np.float32)

# 평균 영상 구하기
average = Average_Image(copy.deepcopy(image_files))
cv2.imshow("Average Image", average.astype(np.uint8))


# 차영상? 한줄영상
print("차 영상 구하기 시작")
difference_array = Difference_Image(copy.deepcopy(image_files), average)
print("차 영상 구하기 완료")
print(difference_array)


# 공분산 행렬
print("공분산 행렬 구하기 시작")
covariance_array = np.cov(difference_array.T)
print("공분산 행렬 구하기 완료")
print(covariance_array)


# 고유값 고유벡터
print("고유값, 고유벡터 구하기 시작")
eigen_value, eigen_vector = np.linalg.eig(covariance_array)
print("고유값, 고유벡터 구하기 완료")
print(eigen_value)
print(eigen_vector)


# 고유값/고유벡터 정렬
print("고유값/고유벡터 정렬 시작")
eigen_value_sort, eigen_vector_sort = Eigen_Sort(eigen_value, eigen_vector)
print("고유값/고유벡터 정렬 완료")
print(eigen_value_sort)
print(eigen_vector_sort)

sum = 0
rate = 0.95
select_index = 0

sum_eigen_value = eigen_value_sort.sum() * rate
for i in range(len(eigen_value_sort)):
    sum += eigen_value_sort[i]

    if sum_eigen_value <= sum:
        select_index = i + 1
        break;

# print(select_index)

transform_matrix = np.zeros((size, 1))

for i in range(select_index):
    mul = (difference_array @ eigen_vector_sort[:, i]).reshape(size, 1)
    transform_matrix = np.append(transform_matrix, mul / np.linalg.norm(mul), axis=1)

transform_matrix = np.delete(transform_matrix, 0, axis=1)

# print(transform_matrix)

pca_array = np.zeros((select_index, 1))
for i in range(image_count):
    pca_array = np.append(pca_array, (transform_matrix.T @ difference_array[:, i]).reshape(select_index, 1), axis=1)

pca_array = np.delete(pca_array, 0, axis=1)

# print(pca_array)

test_image_count = 93
test_files = []

for i in range(test_image_count):
    image = cv2.imread(f"./face_img/test/test{i:03d}.jpg", cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (width, height))
    test_files.append(np.array(image, np.float32))

# print(test_files)

for test_image_number in range(test_image_count):
    image = test_files[test_image_number] - average
    image = image.reshape(size, 1)
    image_value = transform_matrix.T @ image

    min_array = 0
    min_number = 0

    for i in range(image_count):
        arr = pca_array[:, i].reshape(select_index, 1)
        sum = 0
        for j in range(select_index):
            sum += (image_value[j, 0] - arr[j, 0]) ** 2
        sum **= 1 / 2
        if i == 0 or min_array > sum:
            min_array = sum
            min_number = i

    find_num = min_number

    find_image_title = f"Find Image.{find_num:03d}"
    cv2.namedWindow(find_image_title)
    cv2.moveWindow(find_image_title, 100, 100)
    test_image_title = f"Test Image.{test_image_number:03d}"
    cv2.namedWindow(test_image_title)
    cv2.moveWindow(test_image_title, 200 + width, 100)

    cv2.imshow(find_image_title, np.array(image_files[find_num], dtype=np.uint8))
    cv2.imshow(test_image_title, np.array(test_files[test_image_number], dtype=np.uint8))

    cv2.waitKey(100)