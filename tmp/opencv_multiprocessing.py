

import multiprocessing
import cv2

queue_from_cam = multiprocessing.Queue()


def cam_loop(queue_from_cam):
    print('initializing cam')
    cap = cv2.VideoCapture(0)
    while True:
        print('querying frame')
        hello, img = cap.read()
        print('queueing image')
        queue_from_cam.put(img)

    print('cam_loop done')


cam_process = multiprocessing.Process(target=cam_loop,args=(queue_from_cam,))
cam_process.start()

while queue_from_cam.empty():
    pass

print('getting image')
from_queue = queue_from_cam.get()

# print('saving image')
# cv2.imwrite('temp.png', from_queue)
# print('image saved')


while True:
    print("showing image")
    from_queue = queue_from_cam.get()
    cv2.imshow('img', from_queue)
    if cv2.waitKey(30) >= 0:
        break

cv2.destroyAllWindows()
cam_process.terminate()












# =====================================================================================
# import multiprocessing
# import cv2
#
# queue_from_cam = multiprocessing.Queue()
#
# def cam_loop(queue_from_cam):
#     print('initializing cam')
#     cap = cv2.VideoCapture(0)
#     print('querying frame')
#     hello, img = cap.read()
#     print('queueing image')
#     queue_from_cam.put(img)
#     print('cam_loop done')
#
# cam_process = multiprocessing.Process(target=cam_loop,args=(queue_from_cam,))
# cam_process.start()
#
# while queue_from_cam.empty():
#     pass
#
# print('getting image')
# from_queue = queue_from_cam.get()
# print('saving image')
# cv2.imwrite('temp.png', from_queue)
# print('image saved')


