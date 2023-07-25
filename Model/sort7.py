import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment
import cv2

class Track(object):
    def __init__(self, detection, track_id):
        self.kf = KalmanFilter(dim_x=8, dim_z=5)
        self.kf.F = np.array([
            [1, 0, 0, 0, 0, 1, 0, 0],  #Cx
            [0, 1, 0, 0, 0, 0, 1, 0],  #Cy
            [0, 0, 1, 0, 0, 0, 0, 0],  #w
            [0, 0, 0, 1, 0, 0, 0, 0],  #h
            [0, 0, 0, 0, 1, 0, 0, 1],  #a
            [0, 0, 0, 0, 0, 1, 0, 0],  #Cx var
            [0, 0, 0, 0, 0, 0, 1, 0],  #Cy var
            [0, 0, 0, 0, 0, 0, 0, 1]   #a var
        ])
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0]
        ])
        #R越大越相信舊測量；R越小越相信新測量好收斂
        # self.kf.R *= 0.5
        # #P越小越相信當前預測、越快收斂
        # self.kf.P *= 0.9
        # #Q越大越相信測量；Q越小越相信預測
        # self.kf.Q *= 0.001
        #R越大越相信舊測量；R越小越相信新測量好收斂
        self.kf.R *= 0.0001
        #P越小越相信當前預測、越快收斂
        self.kf.P *= 0.0001
        
        # Adjust initial covariance matrix P
        max_velocity = 1.8
        max_acceleration = 0.12
        self.kf.P[5:7, 5:7] *= 0.001        
        self.kf.R[5:7, 5:7] *= 0.001        
        self.kf.P[2:4, 2:4] *= 0.01
        self.kf.R[2:4, 2:4] *= 0.01
        self.kf.P[4, 4] *= 0.01
        self.kf.R[4, 4] *= 0.001
        self.kf.Q[4, 4] *= 0.01

        
        # Q越大越相信測量；Q越小越相信預測
        self.kf.Q[5:7, 5:7] *= 0.1
        self.kf.Q[2:4, 2:4] *= 0.5 

        
        self.kf.x[:5] = np.reshape(detection[:5], (5, 1))
        self.corners = np.reshape(detection[5:13], (8, 1))
        self.vote = detection[13]
        self.track_id = track_id
        self.age = 1
        self.hits = 1

    def predict(self):
        self.kf.predict()
        self.age += 1

    def update(self, detection):
        self.kf.update(detection[:5])
        self.corners = detection[5:13]
        self.vote = detection[13]
        self.hits += 1

def iou_rotated(bbox1, bbox2):
    rect1 = ((bbox1[0], bbox1[1]), (bbox1[2], bbox1[3]), bbox1[4] * 180.0 / np.pi)
    rect2 = ((bbox2[0], bbox2[1]), (bbox2[2], bbox2[3]), bbox2[4] * 180.0 / np.pi)

    box1 = np.int0(cv2.boxPoints(rect1))
    box2 = np.int0(cv2.boxPoints(rect2))

    inter_area = cv2.intersectConvexConvex(np.array(box1), np.array(box2))[0]

    area1 = bbox1[2] * bbox1[3]
    area2 = bbox2[2] * bbox2[3]

    union_area = area1 + area2 - inter_area

    if union_area == 0:
        return 0
    return inter_area / union_area

def associate_detections_to_trackers(detections, trackers, iou_threshold):
    iou_matrix = np.zeros((len(detections), len(trackers)), dtype=float)

    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            iou_matrix[d, t] = iou_rotated(det, trk)
    
    matched_indices = linear_sum_assignment(-iou_matrix)
    matched_indices = np.asarray(matched_indices)
    matched_indices = np.transpose(matched_indices)

    unmatched_detections = np.setdiff1d(range(len(detections)), matched_indices[:, 0])
    unmatched_trackers = np.setdiff1d(range(len(trackers)), matched_indices[:, 1])

    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections = np.append(unmatched_detections, m[0])
            unmatched_trackers = np.append(unmatched_trackers, m[1])
        else:
            matches.append(m.reshape(1, 2))

    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, unmatched_detections, unmatched_trackers

class SORT(object):
    def __init__(self, max_age=1, min_hits=1, iou_threshold=0.1):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0
        self.next_id = 0

    def update(self, detections):
        self.frame_count += 1

        if len(self.trackers) > 0:
            for trk in self.trackers:
                trk.predict()

        matched, unmatched_detections, unmatched_trackers = associate_detections_to_trackers(detections, [trk.kf.x[:5].reshape(-1) for trk in self.trackers], self.iou_threshold)

        for t in unmatched_trackers:
            trk = self.trackers[t]
            trk.age += 1
            trk.corners = np.zeros(8, dtype=np.int32)
            
        for d in unmatched_detections:
            trk = Track(detections[d], self.next_id)
            self.trackers.append(trk)
            self.next_id += 1

        for m in matched:
            trk = self.trackers[m[1]]
            trk.update(detections[m[0]])
            trk.age = 0  # Reset the tracker's age after a successful update


        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = trk.kf.x[:5].reshape(-1)
            c = trk.corners[:8].reshape(-1)
            v = int(trk.vote)
            # if (trk.hits >= self.min_hits or self.frame_count <= self.min_hits) and trk.age <= self.max_age:
            if trk.hits >= self.min_hits and trk.age <= self.max_age:
                yield trk.track_id, d, c, v
            i -= 1
            if trk.age > self.max_age:
                self.trackers.pop(i)

