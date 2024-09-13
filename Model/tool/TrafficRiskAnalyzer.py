
import pandas as pd
from shapely.geometry import Polygon
import os
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
from tqdm import tqdm
import csv
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'SimSun', 'Microsoft YaHei' 等
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题


class TrafficRiskAnalyzer:
    def __init__(self, file_path):
        """
        Initialize the analyzer with the CSV file path.
        """
        self.file_path = file_path
        self.df = None
        self.processed_df = None

    def load_data(self):
        """
        Load the CSV file and parse the structure.
        """
        # Load the file as a DataFrame
        self.df = pd.read_csv(
            self.file_path,
            delimiter=',',
            encoding='utf-8-sig',
            engine='python',
            error_bad_lines=False,  # Skip bad lines
            warn_bad_lines=True,    # Warn about bad lines
            quoting=csv.QUOTE_NONE
        )
        
        # Print column names to inspect them
        # print("Loaded columns:", self.df.columns.tolist())
        
        # Extract number of time frames based on the number of coordinate columns in the dataset
        num_coordinate_columns = self.df.shape[1] - 6  # Remove the first six metadata columns
        num_frames = num_coordinate_columns // 8  # Each frame has 8 coordinates (x1, y1, x2, y2, x3, y3, x4, y4)
        
        # Rename the initial columns based on your provided structure
        metadata_columns = ['Trajectory_ID', 'Start_Frame', 'End_Frame', 'Enter_Intersection', 'Exit_Intersection', 'Type']
        coordinate_columns = [f'{coord}{p}_t{t}' for t in range(1, num_frames + 1) for p in range(1,5) for coord in ('x', 'y')]
        self.df.columns = metadata_columns + coordinate_columns
        
        # Optional: Print the new column names to verify
        # print("Renamed columns:", self.df.columns.tolist())
    
    def create_bounding_box(self, row, t):
        """
        Create a bounding box Polygon for a given row of trajectory data and specific time frame.
        """
        return Polygon([
            (row[f'x1_t{t}'], row[f'y1_t{t}']),
            (row[f'x2_t{t}'], row[f'y2_t{t}']),
            (row[f'x3_t{t}'], row[f'y3_t{t}']),
            (row[f'x4_t{t}'], row[f'y4_t{t}'])
        ])
    
    def find_high_risk_trajectories(self):
        """
        Find trajectories with exit times less than or equal to 3 seconds after overlap.
        """
        from tqdm import tqdm  # 如果未在顶部导入，这里也可以导入

        high_risk_trajectories = []
        FRAME_RATE = 30.0  # Assuming 30 frames per second

        total_pairs = len(self.df) * (len(self.df) - 1) // 2  # 计算总共需要比较的轨迹对数
        pair_count = 0  # 用于计数已处理的轨迹对

        # 使用tqdm显示进度
        for index_a, row_a in tqdm(self.df.iterrows(), total=len(self.df), desc='Processing Trajectories'):
            start_frame_a = int(row_a['Start_Frame'])
            end_frame_a = int(row_a['End_Frame'])

            for index_b, row_b in self.df.iterrows():
                if index_a >= index_b:  # 避免重复比较和自我比较
                    continue
                start_frame_b = int(row_b['Start_Frame'])
                end_frame_b = int(row_b['End_Frame'])

                # Compare for overlapping time frames
                overlap_start = max(start_frame_a, start_frame_b)
                overlap_end = min(end_frame_a, end_frame_b)

                if overlap_start > overlap_end:
                    continue  # No overlapping frames

                for t in range(overlap_start, overlap_end + 1):
                    # Adjust the frame index relative to each trajectory's start frame
                    t_relative_a = t - start_frame_a + 1
                    t_relative_b = t - start_frame_b + 1

                    bbox_a = self.create_bounding_box(row_a, t_relative_a)
                    bbox_b = self.create_bounding_box(row_b, t_relative_b)

                    # Check if the bounding boxes intersect
                    if bbox_a.intersects(bbox_b):
                        # Calculate exit time (in seconds)
                        exit_time_frames = end_frame_a - t
                        exit_time_seconds = exit_time_frames / FRAME_RATE
                        if exit_time_seconds <= 3:
                            high_risk_trajectories.append({
                                'Trajectory_ID_A': row_a['Trajectory_ID'],
                                'Trajectory_ID_B': row_b['Trajectory_ID'],
                                'Start_Frame_A': start_frame_a,
                                'End_Frame_A': end_frame_a,
                                'Exit_Time_Seconds': exit_time_seconds
                            })
                        break  # Found an overlap, no need to check further for this pair

                pair_count += 1  # 更新已处理的轨迹对数

        # Convert the results into a DataFrame
        self.processed_df = pd.DataFrame(high_risk_trajectories)


    def get_high_risk_trajectories(self):
        """
        Return the high-risk trajectories as a DataFrame.
        """
        return self.processed_df if self.processed_df is not None else pd.DataFrame()
    
def visualize_and_save_high_risk_trajectories(analyzer, output_dir):
    """
    可视化高风险轨迹，并将图像保存到指定的文件夹。
    """
    import os

    high_risk_df = analyzer.get_high_risk_trajectories()
    FRAME_RATE = 30.0  # 每秒帧数

    # 创建输出文件夹
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, risk_event in high_risk_df.iterrows():
        traj_id_a = risk_event['Trajectory_ID_A']
        traj_id_b = risk_event['Trajectory_ID_B']
        start_frame_a = int(risk_event['Start_Frame_A'])
        exit_time_seconds = risk_event['Exit_Time_Seconds']
        end_frame_a = int(risk_event['End_Frame_A'])
        overlap_frame = end_frame_a - int(exit_time_seconds * FRAME_RATE)

        # 获取轨迹数据
        row_a = analyzer.df[analyzer.df['Trajectory_ID'] == traj_id_a].iloc[0]
        row_b = analyzer.df[analyzer.df['Trajectory_ID'] == traj_id_b].iloc[0]

        # 计算相对时间帧索引
        t_relative_a = overlap_frame - int(row_a['Start_Frame']) + 1
        t_relative_b = overlap_frame - int(row_b['Start_Frame']) + 1

        # 创建多边形
        bbox_a = analyzer.create_bounding_box(row_a, t_relative_a)
        bbox_b = analyzer.create_bounding_box(row_b, t_relative_b)

        # 绘制多边形
        fig, ax = plt.subplots()
        x_a, y_a = bbox_a.exterior.xy
        x_b, y_b = bbox_b.exterior.xy

        ax.fill(x_a, y_a, alpha=0.5, fc='red', ec='black', label=f'ID {traj_id_a}')
        ax.fill(x_b, y_b, alpha=0.5, fc='blue', ec='black', label=f'ID {traj_id_b}')

        # 绘制交集区域
        intersection = bbox_a.intersection(bbox_b)
        if not intersection.is_empty:
            if intersection.geom_type == 'Polygon':
                x_int, y_int = intersection.exterior.xy
                ax.fill(x_int, y_int, alpha=0.7, fc='purple', ec='black', label='overlapping')

        ax.set_title(f'High Rsik Track : ID {traj_id_a} and ID {traj_id_b} overlapping in frame {overlap_frame}')
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.legend()
        plt.gca().invert_yaxis()  # 如果坐标系与图像坐标系相反，可以反转Y轴

        # 保存图像
        output_path = os.path.join(output_dir, f'high_risk_{traj_id_a}_{traj_id_b}_frame_{overlap_frame}.png')
        plt.savefig(output_path)
        plt.close(fig)  # 关闭图形，释放内存



# Example usage:
file_path = r"D:\TrafficTrackerGUI-MOTC\result\1120619_120m_A架次\result\csv\short_gate.csv"  # Path to the input CSV file
analyzer = TrafficRiskAnalyzer(file_path)
analyzer.load_data()
analyzer.find_high_risk_trajectories()
high_risk_df = analyzer.get_high_risk_trajectories()
visualize_and_save_high_risk_trajectories(analyzer, r"D:\TrafficTrackerGUI-MOTC\result\1120619_120m_A架次\result\csv" )
print(high_risk_df)
