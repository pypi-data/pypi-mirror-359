import os
import glob
import numpy as np

# 输入和输出路径
yolo_labels_dir = '/Users/weidongguo/Workspace/crm/boxmot/assets/MOT17-mini/train/MOT17-03-FRCNN/det2/labels'
output_det_file = '/Users/weidongguo/Workspace/crm/boxmot/assets/MOT17-mini/train/MOT17-03-FRCNN/det/det.txt'
output_gt_file = '/Users/weidongguo/Workspace/crm/boxmot/assets/MOT17-mini/train/MOT17-03-FRCNN/gt/gt_temp.txt'

# 确保输出目录存在
os.makedirs(os.path.dirname(output_det_file), exist_ok=True)
os.makedirs(os.path.dirname(output_gt_file), exist_ok=True)

# 图像尺寸（从seqinfo.ini中获取）
img_width = 1920
img_height = 1080

# 获取所有标签文件并排序
label_files = sorted(glob.glob(os.path.join(yolo_labels_dir, '*.txt')))

# 初始化MOT格式的检测结果和真值
det_results = []
gt_results = []

# 为每个对象分配一个唯一的ID
object_ids = {}
next_id = 1

# 处理每个标签文件
for label_file in label_files:
    # 从文件名中提取帧ID
    frame_id = int(os.path.basename(label_file).split('.')[0])
    
    # 读取YOLO格式的标签
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    # 处理每个检测结果
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 6:  # 确保有足够的数据
            class_id = int(parts[0])
            center_x = float(parts[1])
            center_y = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            track_id = int(parts[5])  # 使用YOLO格式中的track_id
            
            # 转换为像素坐标
            x = int((center_x - width/2) * img_width)
            y = int((center_y - height/2) * img_height)
            w = int(width * img_width)
            h = int(height * img_height)
            
            # 确保坐标不为负数
            x = max(0, x)
            y = max(0, y)
            
            # 设置置信度为1.0（因为这是真值数据）
            confidence = 1.0
            
            # 添加到检测结果
            det_results.append(f"{frame_id},-1,{x},{y},{w},{h},{confidence}")
            
            # 添加到真值（使用YOLO格式中的track_id，类别ID设为1表示人）
            gt_results.append(f"{frame_id},{track_id},{x},{y},{w},{h},1,1,1.0")

# 写入检测结果文件
with open(output_det_file, 'w') as f:
    f.write('\n'.join(det_results))

# 写入真值文件
with open(output_gt_file, 'w') as f:
    f.write('\n'.join(gt_results))

print(f"转换完成。检测结果保存到 {output_det_file}，真值保存到 {output_gt_file}")