
import pandas as pd
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv
import numpy as np
import csv
import numpy as np
class OrientedBoundingBox:
    def __init__(self, corners):
        """
        Initialize the Oriented Bounding Box (OBB) from a set of corners (4 points).
        """
        self.corners = np.array(corners)
        self.center = np.mean(self.corners, axis=0)  # Calculate the center point
        self.axes = self._compute_axes()  # Compute the OBB's axes (orientation)
        self.extents = self._compute_extents()  # Compute the extents along the axes

    def _compute_axes(self):
        """
        Compute the normalized axes based on the first two sides of the quadrilateral.
        """
        axis1 = self.corners[1] - self.corners[0]  # Vector from corner 0 to corner 1
        axis2 = self.corners[3] - self.corners[0]  # Vector from corner 0 to corner 3
        return [axis1 / np.linalg.norm(axis1), axis2 / np.linalg.norm(axis2)]

    def _compute_extents(self):
        """
        Project the corners onto the axes to find the extents (min/max projection).
        """
        projections = [[np.dot(corner - self.center, axis) for axis in self.axes] for corner in self.corners]
        projections = np.array(projections)
        min_projections = projections.min(axis=0)
        max_projections = projections.max(axis=0)
        return max_projections - min_projections

    def overlaps_with(self, other):
        """
        Check for overlap between this OBB and another OBB using the Separating Axis Theorem (SAT).
        """
        axes = self.axes + other.axes
        for axis in axes:
            proj1 = self.project(axis)
            proj2 = other.project(axis)
            if not self._overlap_on_axis(proj1, proj2):
                return False  # No overlap found on this axis
        return True

    def project(self, axis):
        """
        Project the OBB's corners onto an axis.
        """
        min_proj = np.inf
        max_proj = -np.inf
        for corner in self.corners:
            projection = np.dot(corner, axis)
            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)
        return (min_proj, max_proj)

    def _overlap_on_axis(self, proj1, proj2):
        """
        Check if two projections overlap on a given axis.
        """
        return proj1[0] <= proj2[1] and proj2[0] <= proj1[1]


class Trajectory:
    def __init__(self, trajectory_id, corners):
        """
        Represents a trajectory, with a trajectory ID and Oriented Bounding Box (OBB).
        """
        self.id = trajectory_id
        self.bounding_box = OrientedBoundingBox(corners)

    def overlaps_with(self, other):
        """
        Check if this trajectory's bounding box overlaps with another trajectory's bounding box.
        """
        return self.bounding_box.overlaps_with(other.bounding_box)


class BVHNode:
    def __init__(self, trajectories, depth=0, max_depth=10):
        """
        A node in the Bounding Volume Hierarchy (BVH).
        """
        self.trajectories = trajectories
        self.children = []
        self.bounds = self._compute_bounding_volume(trajectories)
        
        if depth < max_depth and len(trajectories) > 1:
            # Recursively split the node by alternating between x and y axes
            axis = depth % 2  # Alternate between splitting along x and y axes
            sorted_trajectories = sorted(trajectories, key=lambda t: t.bounding_box.center[axis])
            mid = len(sorted_trajectories) // 2
            self.children.append(BVHNode(sorted_trajectories[:mid], depth + 1, max_depth))
            self.children.append(BVHNode(sorted_trajectories[mid:], depth + 1, max_depth))

    def _compute_bounding_volume(self, trajectories):
        """
        Compute a bounding volume that encloses all the trajectories in this node.
        """
        all_corners = np.vstack([traj.bounding_box.corners for traj in trajectories])
        return OrientedBoundingBox(all_corners)

    def is_leaf(self):
        """
        Check if this node is a leaf node (no children).
        """
        return len(self.children) == 0

    def detect_collisions(self, other_node, collisions):
        """
        Recursively detect collisions between this BVH node and another BVH node.
        """
        if not self.bounds.overlaps_with(other_node.bounds):
            return  # No overlap, so no collision

        if self.is_leaf() and other_node.is_leaf():
            # Check for collisions between the trajectories in the leaf nodes
            for traj1 in self.trajectories:
                for traj2 in other_node.trajectories:
                    if traj1 != traj2 and traj1.overlaps_with(traj2):
                        collisions.append((traj1.id, traj2.id))
        else:
            # Recursively check child nodes for collisions
            for child_self in self.children:
                for child_other in other_node.children:
                    child_self.detect_collisions(child_other, collisions)


class TrafficRiskAnalyzer:
    def __init__(self, file_path):
        """
        Initialize the analyzer with the CSV file path.
        """
        self.file_path = file_path
        self.df = None
        self.trajectories = []
        self.bvh_root = None
        self.collisions = []  # Store detected collisions

    def load_data(self):
        """
        Load the CSV file and parse the structure.
        """
        print("Loading data...")
        # Load CSV while ignoring bad lines
        self.df = pd.read_csv(self.file_path, header=None, error_bad_lines=False, warn_bad_lines=True)
        print("Data loaded with shape:", self.df.shape)

    def create_trajectories(self):
        """
        Create trajectory objects from the loaded data.
        Each trajectory can span multiple frames, with each frame having its own OBB.
        """
        print("Creating trajectories...")

        num_frames = (self.df.shape[1] - 6) // 8  # Number of frames based on the number of columns after metadata
        for idx, row in self.df.iterrows():
            trajectory_id = row[0]  # Trajectory ID is in the first column (index 0)
            frames = {}
            for frame in range(num_frames):
                start_col = 6 + frame * 8  # Starting index for this frame's coordinates
                corners = [
                    [row[start_col], row[start_col + 1]],   # x1, y1
                    [row[start_col + 2], row[start_col + 3]], # x2, y2
                    [row[start_col + 4], row[start_col + 5]], # x3, y3
                    [row[start_col + 6], row[start_col + 7]]  # x4, y4
                ]
                frames[frame] = OrientedBoundingBox(corners)
            self.trajectories.append(Trajectory(trajectory_id, frames))


    def build_bvh(self):
        """
        Build the Bounding Volume Hierarchy (BVH) using the trajectories' bounding boxes.
        """
        print("Building BVH...")
        self.bvh_root = BVHNode(self.trajectories)

    def detect_collisions(self, frame):
        """
        Detect collisions using the BVH structure at a given frame.
        """
        print(f"Detecting collisions at frame {frame}...")
        self.collisions = []
        self.bvh_root.detect_collisions(self.bvh_root, self.collisions, frame)
        return self.collisions

    def save_collisions(self, output_file):
        """
        Save detected collisions to a CSV file.
        """
        print("Saving collisions...")
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Trajectory 1', 'Trajectory 2'])
            for traj1, traj2 in self.collisions:
                writer.writerow([traj1, traj2])

# Example usage
# Example usage
file_path = r"D:\TrafficTrackerGUI-MOTC\result\1120619_120m_A架次\result\csv\short_gate.csv"
output_file = r"D:\TrafficTrackerGUI-MOTC\result\1120619_120m_A架次\result\csv\collisions.csv"

analyzer = TrafficRiskAnalyzer(file_path)
analyzer.load_data()
analyzer.create_trajectories()
analyzer.build_bvh()

# Detect collisions at a specific frame
frame = 1  # Adjust this frame index as needed
collisions = analyzer.detect_collisions(frame)

# Save collisions to a CSV file
analyzer.save_collisions(output_file)