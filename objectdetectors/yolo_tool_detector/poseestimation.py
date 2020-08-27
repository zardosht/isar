import logging
import multiprocessing as mp
import os
import random
import sys
import traceback

import cv2
import numpy as np
import time

import isar
from isar.tracking.objectdetection import POISON_PILL
from objectdetectors.yolo_mainboard_detector import temp_folder_path

logger = logging.getLogger('mirdl.yolo_pose_estimator')
debug = False


DEFAULT_HOMOGRAPHY = np.array([[1., 0., 0.], [0., 1., 0.]])
MIN_IMAGE_DIMENSION = 150  # px
SCALE_FACTOR = 2

class PoseEstimator(mp.Process):

    MAX_FEATURES = 500
    GOOD_MATCH_PERCENT = 0.90
    ransac_reprojection_threshold = 5
    recompute_homography_using_only_inliers = False

    # recompute_homography_using_ECC = False
    recompute_homography_using_ECC = True
    recompute_homography_using_ECC_threshold_min = 40
    recompute_homography_using_ECC_threshold_max = 70

    def __init__(self, task_queue, result_queue):
        mp.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            pe_input = self.task_queue.get()

            if pe_input == POISON_PILL:
                logger.info("Received None pose_estimation_input. Shutting down.")
                self.task_queue.task_done()
                sys.exit(0)

            # compute pose from template and target images
            # put a PoseEstimationOutput instance into the results queue
            t1 = time.time()
            try:
                estimated_pose = self.find_best_homography(pe_input.template_image, pe_input.target_image,
                                                           pe_input.best_homography)
            except:
                estimated_pose = PoseEstimationOutput(None, DEFAULT_HOMOGRAPHY, 1.)

            estimated_pose.object_name = pe_input.object_name
            self.task_queue.task_done()
            self.result_queue.put(estimated_pose)
            logger.debug("Finding best homograpy for {} took {}".format(pe_input.object_name, time.time() - t1))


    def find_best_homography(self, physical_object_image, cropped_image, best_pe):
        pe_result = self.compute_homography(physical_object_image, cropped_image)
        pe_result.error = self.compute_error(pe_result.homography, physical_object_image, cropped_image)
        # Keep track of the best pe_result. If the newly computed one is better, replace the best with it.
        # See compute_quality_score(). I think a better approach would be compute the quality of a pe_result using reprojection error.
        if best_pe is not None:
            best_pe.error = self.compute_error(best_pe.homography, physical_object_image, cropped_image, "_best")

        if self.recompute_homography_using_ECC:
            try:
                better_pe = best_pe if best_pe is not None and best_pe.error < pe_result.error else pe_result
                if self.recompute_homography_using_ECC_threshold_min < better_pe.error < self.recompute_homography_using_ECC_threshold_max:
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1000, 1e-6)
                    physical_object_image_gray, cropped_image_gray = self.convert_to_gray_scale(physical_object_image, cropped_image)
                    better_homography_float32 = better_pe.homography.astype(np.float32)

                    if isar.PLATFORM == "Darwin":
                        (cc, h_ECC) = cv2.findTransformECC(physical_object_image_gray, cropped_image_gray,
                                                           better_homography_float32,
                                                           cv2.MOTION_AFFINE, criteria)
                    else:
                        (cc, h_ECC) = cv2.findTransformECC(physical_object_image_gray, cropped_image_gray,
                                                           better_homography_float32,
                                                           cv2.MOTION_AFFINE, criteria,
                                                           inputMask=None,
                                                           gaussFiltSize=5)

                    errror_ecc = self.compute_error(h_ECC, physical_object_image, cropped_image, "_ecc")
                    if h_ECC is not None and errror_ecc < better_pe.error:
                        pe_result.homography = h_ECC
                        pe_result.error = errror_ecc
            except Exception as exp:
                logger.error("Error recomputing homography using ECC")
                logger.error(exp)
                traceback.print_tb(exp.__traceback__)

        epsilon = 5e0
        if best_pe is None or pe_result.error < best_pe.error:
            return pe_result
        elif np.abs(pe_result.error - best_pe.error) < epsilon:
            return random.choice((pe_result, best_pe))
        else:
            return best_pe

    def compute_homography(self, physical_object_image, cropped_image):
        # If the image of the physical object is too small, 
        # scale it up to improve feature detection
        physical_object_image, cropped_image = self.checkAndScaleImages(physical_object_image, cropped_image)
        # I tried SIFT, SURF, and ORB too. AKAZE gives the best and fastest result. 
        physicalObjectKeyPoints, physicalObjectDescriptors, croppedImageKeyPoints, croppedImageDescriptors \
            = self.extract_feature_points(physical_object_image, cropped_image, algorithm='AKAZE')
        # I also tried BRUTE_FORCE_L1, BRUTE_FORCE_HAMMING with ratio test, and FLANN. 
        matches = self.find_matches(physicalObjectDescriptors, croppedImageDescriptors, algorithm='BRUTE_FORCE_HAMMING', ratio_test=False)
        if debug: 
            # Draw top matches
            im_matches = cv2.drawMatches(physical_object_image, physicalObjectKeyPoints, cropped_image, croppedImageKeyPoints, matches, None)
            cv2.imwrite(str(os.path.join(temp_folder_path, "matches.jpg")), im_matches)
        points1, points2 = self.find_points_from_matches(physicalObjectKeyPoints, croppedImageKeyPoints, matches)
        try:
            h1, mask = cv2.estimateAffine2D(points1, points2, method=cv2.RANSAC,
                                            ransacReprojThreshold=self.ransac_reprojection_threshold)
        except:
            h1 = DEFAULT_HOMOGRAPHY

        homography_result = PoseEstimationOutput(None, h1, None)

        if self.recompute_homography_using_only_inliers:
            # get the inlier matches (list of tuples of points)
            # run find homography again unsing only the inliers this time instead of LEMDS or RHO instead of RANSAC
            boolean_inliers_mask = (mask > 0)
            inlier_points1 = points1[boolean_inliers_mask.repeat(2, axis =1)].reshape((-1, 2))
            inlier_points2 = points2[boolean_inliers_mask.repeat(2, axis =1)].reshape((-1, 2))
            # h2, mask = cv2.findHomography(inlier_points1, inlier_points2, cv2.LMEDS)
            h2, mask = cv2.estimateAffine2D(inlier_points1, inlier_points2, cv2.LMEDS)
            # prosac_reprojection_error = 2.5
            # h2, mask = cv2.findHomography(inlier_points1, inlier_points2, cv2.RHO, prosac_reprojection_error)
            if h2 is not None:
                homography_result.homography = h2
                
        logger.debug("Homography: %s", homography_result.homography)
        return homography_result


    @staticmethod
    def checkAndScaleImages(physical_obj_image, cropped_image):
        heigt, width, _ = physical_obj_image.shape
        if heigt < MIN_IMAGE_DIMENSION or width < MIN_IMAGE_DIMENSION:
            scaled_phys_obj_image = np.copy(physical_obj_image)
            scaled_phys_obj_image = cv2.resize(physical_obj_image, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_CUBIC)
            scaled_cropped_image = np.copy(cropped_image)
            scaled_cropped_image = cv2.resize(cropped_image, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_CUBIC)
            return scaled_phys_obj_image, scaled_cropped_image

        return physical_obj_image, cropped_image


    @staticmethod
    def convert_to_gray_scale(*images):
        result = []
        for image in images:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = gray.astype(np.float32)
            gray = gray / 255
            result.append(gray)
        return tuple(result)

    def extract_feature_points(self, physical_object_image, cropped_image, algorithm='SURF'):
        feature_extractor = None
        if algorithm == 'SURF':
            feature_extractor = cv2.xfeatures2d.SURF_create()
        elif algorithm == 'SIFT':
            feature_extractor = cv2.xfeatures2d.SIFT_create()
        elif algorithm == 'ORB':
            feature_extractor = cv2.ORB_create(self.MAX_FEATURES)
        elif algorithm == 'AKAZE':
            feature_extractor = cv2.AKAZE_create(threshold=1e-4)

        physical_object_key_points, physical_object_descriptors = feature_extractor.detectAndCompute(physical_object_image, None)
        cropped_image_key_points, cropped_image_descriptors = feature_extractor.detectAndCompute(cropped_image, None)

        return physical_object_key_points, physical_object_descriptors, cropped_image_key_points, cropped_image_descriptors

    def find_matches(self, physical_object_descriptors, cropped_image_descriptors, algorithm=None, ratio_test=False):
        matcher = None
        if algorithm == 'FLANN':
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            matcher = cv2.FlannBasedMatcher(index_params, search_params)
        elif algorithm == 'BRUTE_FORCE_HAMMING':
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            # matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        elif algorithm == 'BRUTE_FORCE_L1':
            matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_L1)

        good_matches = []
        if ratio_test:
            matches = matcher.knnMatch(physical_object_descriptors, cropped_image_descriptors, k=2)
            for m, n in matches:
                if m.distance < 0.5 * n.distance:
                    good_matches.append(m)
        else:
            matches = matcher.match(physical_object_descriptors, cropped_image_descriptors)
            matches.sort(key=lambda x: x.distance, reverse=False)
            num_good_matches = int(len(matches) * self.GOOD_MATCH_PERCENT)
            good_matches = matches[:num_good_matches]

        logger.debug("Number of good matches: %s", len(good_matches))
        return good_matches

    @staticmethod
    def find_points_from_matches(physical_object_key_points, cropped_image_key_points, matches):
        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = physical_object_key_points[match.queryIdx].pt
            points2[i, :] = cropped_image_key_points[match.trainIdx].pt

        return points1, points2

    @staticmethod
    def get_gradient(im):
        # Calculate the x and y gradients using Sobel operator
        grad_x = cv2.Sobel(im, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(im, cv2.CV_32F, 0, 1, ksize=3)

        # Combine the two gradients
        grad = cv2.addWeighted(np.absolute(grad_x), 0.5, np.absolute(grad_y), 0.5, 0)
        return grad

    @staticmethod
    def compute_error(homography, physical_object_image, cropped_image, debug_postfix=""):
        height, width, channels = cropped_image.shape

        # warpped_original = cv2.warpPerspective(physical_object_image, homography, (width, height))
        warpped_original = cv2.warpAffine(physical_object_image, homography, (width, height), flags = cv2.INTER_LINEAR)

        warpped_original[warpped_original == 0] = 255
        if debug: cv2.imwrite(str(os.path.join(temp_folder_path, "warpped_original" + debug_postfix + ".jpg")), warpped_original)

        difference_image = np.abs(cropped_image.astype("float32") - warpped_original.astype("float32"))
        difference_image = cv2.cvtColor(difference_image, cv2.COLOR_BGR2GRAY)

        # difference_image = cv2.normalize(difference_image, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        # # difference_image = get_gradient(difference_image)
        # # difference_image = cv2.erode(difference_image, np.ones((3, 3), np.uint8), iterations=1)
        # # difference_image = cv2.dilate(difference_image, np.ones((3,3),np.uint8), iterations=1)
        #
        # morph_elem = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        # # difference_image = cv2.morphologyEx(difference_image, cv2.MORPH_CLOSE, morph_elem)
        # # difference_image = cv2.morphologyEx(difference_image, cv2.MORPH_TOPHAT, morph_elem)
        # difference_image = cv2.morphologyEx(difference_image, cv2.MORPH_BLACKHAT, morph_elem)
        # # ret, difference_image = cv2.threshold(difference_image, 100, 255, cv2.THRESH_BINARY)
        # difference_image = cv2.adaptiveThreshold(difference_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        #
        # morph_elem = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # difference_image = cv2.morphologyEx(difference_image, cv2.MORPH_OPEN, morph_elem)
        # # difference_image = cv2.morphologyEx(difference_image, cv2.MORPH_TOPHAT, morph_elem)

        if debug: cv2.imwrite(str(os.path.join(temp_folder_path, "difference_image" + debug_postfix + ".jpg")), difference_image)

        # error = (1 / (height * width)) * np.sum(difference_image ** 2)
        error = np.sqrt((1 / (height * width)) * np.sum(difference_image ** 2))

        # cropped_image_gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        # warpped_original_gray = cv2.cvtColor(warpped_original, cv2.COLOR_BGR2GRAY)
        # similarity_score = ssim(cropped_image_gray, warpped_original_gray, gradient=False)
        # error = (1 - similarity_score) / 2

        return error


class PoseEstimationOutput:
    def __init__(self, name, homography, error):
        self.object_name = name
        self.homography = homography
        self.error = error


class PoseEstimationInput:
    def __init__(self, object_name, template_image, target_image, best_homography):
        self.object_name = object_name
        self.template_image = template_image
        self.target_image = target_image
        self.best_homography = best_homography



