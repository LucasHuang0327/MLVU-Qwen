import cv2
import os
import re
import base64
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

#每分鐘生成16幀
'''
def sample_frames_from_video(video_path, output_folder, frames_per_minute=16):
    """
    从视频中每分钟采样指定数量的帧并保存为 .jpg 格式。

    :param video_path: 视频文件路径
    :param output_folder: 保存采样图片的文件夹
    :param frames_per_minute: 每分钟采样的帧数
    """
    
    if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
        print(f"已采样完成，跳过视频: {video_path}")
        return
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return

    # 获取视频的帧率和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 每秒帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
    duration = total_frames / fps  # 视频时长（秒）
    print(f"视频时长: {duration:.2f} 秒, 帧率: {fps:.2f} fps, 总帧数: {total_frames}")

    # 每分钟的帧数
    frames_per_minute_interval = int(fps * 60 / frames_per_minute)

    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 每隔指定帧数保存一张图片
        if frame_count % frames_per_minute_interval == 0:
            output_path = os.path.join(output_folder, f"{fname}_frame_{saved_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            #print(f"保存图片: {output_path}")
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"采样完成，共保存 {saved_count} 张图片到 {output_folder}")
'''
# 每隔指定帧数采样
def sample_frames_from_video(video_path, output_folder, max_frames=160):
    """
    从视频中采样指定数量的帧并保存为 .jpg 格式。
    如果视频长度超过 10 分钟，仍然只采样最多 max_frames 张图片。

    :param video_path: 视频文件路径
    :param output_folder: 保存采样图片的文件夹
    :param max_frames: 最大采样帧数
    """
    fname = output_folder.split("/")[-1]
    
    if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
        print(f"**{fname}**已采样完成，跳过视频")
        return

    stime_start = time.time()

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return

    # 获取视频的帧率和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 每秒帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
    duration = total_frames / fps  # 视频时长（秒）
    
    # 动态计算采样间隔
    interval = max(1, total_frames // max_frames)  # 确保至少采样 1 帧
    print(f"^^{fname}^^视频时长: {duration:.2f} 秒, 总帧数: {total_frames}, 隔格長度為:",interval)
    
    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 每隔指定帧数保存一张图片
        if frame_count % interval == 0:
            output_path = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1

            # 如果达到最大采样帧数，则停止
            if saved_count >= max_frames:
                break

        frame_count += 1

    cap.release()
    
    print(f"**{fname}采样完成**，耗时{time.time()-stime_start:.2f}秒, 共保存 {saved_count} 张图片")

# 多线程处理视频文件
def process_video(video_path, output_folder):
    """
    处理单个视频文件，采样帧并保存。
    """
    try:
        sample_frames_from_video(video_path, output_folder)
    except Exception as e:
        print(f"处理视频 {video_path} 时出错: {e}")

num_workers = 6
def sample_frames_parellel(video_root, output_root, file_names = None,max_frames=160):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:  # 设置并行线程数
        futures = []
        
        if file_names is not None:
            for file_name in file_names:
                video_path = os.path.join(video_root, file_name)
                output_folder = os.path.join(output_root, file_name)
                futures.append(executor.submit(process_video, video_path, output_folder))
        else:
            print("file_names is None") 
            '''for file_name in os.listdir(video_root):
                video_path = os.path.join(video_root, file_name)
                output_folder = os.path.join(output_root, file_name)
                futures.append(executor.submit(process_video, video_path, output_folder))
            '''
            return 
        # 等待所有任务完成
        for future in as_completed(futures):
            future.result()  # 捕获异常（如果有）
        print("所有视频处理完成！")

# 将图片转换为 Base64 编码
def frame_to_base64(frame_path, output_folder):
    """
    将图片转换为 Base64 编码并保存到文件。
    :param frame_path: 图片所在文件夹路径
    :param output_folder: 保存 Base64 编码文件的文件夹
    """
    fname = output_folder.split("/")[-2]
    
    if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
        print(f"**{fname}**Base64 转换已完成，跳过文件夹\n")
        return
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    
    # 获取所有图片文件
    count = 0
    frames = [f for f in os.listdir(frame_path) if os.path.isfile(os.path.join(frame_path, f))]
    for frame in frames:
        frame_full_path = os.path.join(frame_path, frame)
        with open(frame_full_path, "rb") as frame_file:
            # 将图片转换为 Base64 编码
            encoded_image = base64.b64encode(frame_file.read()).decode("utf-8")
        
        # 保存 Base64 编码到文件
        base64_output_path = os.path.join(output_folder, f"{os.path.splitext(frame)[0]}.txt")
        with open(base64_output_path, "w", encoding="utf-8") as base64_file:
            base64_file.write(encoded_image)
        count += 1 
        #print(f"保存 Base64 编码文件: {base64_output_path}")
    print(f"**{fname}完成Base64 转换**，共保存 {count} 个文件到")

# 尺寸轉換
def resize_sampled_frames(input_folder, output_folder, target_size=[224, 224]):
    """
    将采样的帧调整为指定尺寸并保存。

    :param input_folder: 输入图片文件夹路径
    :param output_folder: 输出图片文件夹路径
    :param target_size: 目标尺寸 (宽, 高)，默认为 (224, 224)
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有图片文件
    frames = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    for frame in frames:
        input_path = os.path.join(input_folder, frame)
        output_path = os.path.join(output_folder, frame)

        # 读取图片
        image = cv2.imread(input_path)
        if image is None:
            print(f"无法读取图片: {input_path}")
            continue
        
        original_height, original_width = image.shape[:2]
        scale = target_size[1]/original_height  # 选择较小的缩放比例

        # 计算新的宽高
        target_size[0] = int(original_width * scale)
        
        # 调整图片尺寸
        resized_image = cv2.resize(image, target_size)

        # 保存调整后的图片
        cv2.imwrite(output_path, resized_image)
        print(f"已调整并保存图片: {output_path}")

def get_files_by_pattern(folder_path, pattern):
    """
    从指定文件夹中提取符合正则表达式模式的文件名。

    :param folder_path: 文件夹路径
    :param pattern: 正则表达式模式
    :return: 符合条件的文件名列表
    """
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return []

    # 获取文件夹中的所有文件
    all_files = os.listdir(folder_path)

    # 使用正则表达式过滤文件名
    matched_files = [f for f in all_files if re.match(pattern, f)]

    return matched_files

def main():
    time_start = time.time()
    
    # root and folder
    video_root = "./MLVU/data/MLVUTest/video/"
    output_root = "./MLVU/data/MLVUTest/sampled_frames/"
    file_names = get_files_by_pattern(video_root, r"test_.*\.mp4$")
    print("Num of files need to sample:",len(file_names))
    
    #CPU並行處理
    if len(file_names)%6 == 5 or len(file_names)%6 == 0 or len(file_names) >=18:
        num_workers = 6
    else:
        num_workers = 3
    sample_frames_parellel(video_root, output_root, file_names)
    
    for fname in file_names: 
        #video_path = f"./MLVU/data/MLVUTest/video/{fname}"  # 替换为你的视频路径
        output_folder = f"./MLVU/data/MLVUTest/sampled_frames/{fname}/"  # 替换为你的输出文件夹
        base64_folder = f"./MLVU/data/MLVUTest/base64_frames/{fname}/"  # 保存 Base64 编码文件的文件夹
        #CPU串行處理
        #sample_frames_from_video(video_path, output_folder)
    
        frame_to_base64(output_folder, base64_folder)
    
    time_end = time.time()
    print("Total time cost:", f"{time_end - time_start:.2f}", "s")
    '''
    video_path = f"./MLVU/data/MLVUTest/video/{file_names}"  # 替换为你的视频路径
    output_folder = f"./MLVU/data/MLVUTest/sampled_frames/{file_names}/"  # 替换为你的输出文件夹
    base64_folder = f"./MLVU/data/MLVUTest/base64_frames/{file_names}/"  # 保存 Base64 编码文件的文件夹
    
    #CPU串行處理
    #sample_frames_from_video(video_path, output_folder)
    
    #CPU並行處理
    sample_frames_parellel(video_path, output_folder)
    frame_to_base64(output_folder, base64_folder)
    '''

def main_resize():
    time_start = time.time()
    
    # root and folder
    sampleframe_root = "./MLVU/data/MLVUTest/sampled_frames/"
    re_sampleframe_root = "./MLVU/data/MLVUTest/re_sampled_frames/"
    re_base64frame_root = "./MLVU/data/MLVUTest/re_base64_frames/"
    
    os.makedirs(re_sampleframe_root, exist_ok=True)
    os.makedirs(re_base64frame_root, exist_ok=True)
    
    
    file_names = get_files_by_pattern(sampleframe_root, r"test_.*\.mp4$")
    print("Num of files need to sample:",len(file_names))
    
    for fname in file_names: 
        resize_sampled_frames(f"{sampleframe_root}{fname}/", f"{re_sampleframe_root}{fname}/")
        frame_to_base64(f"{re_sampleframe_root}{fname}/", f"{re_base64frame_root}{fname}/")
    
    time_end = time.time()
    print("Total time cost:", f"{time_end - time_start:.2f}", "s")
    '''
    video_path = f"./MLVU/data/MLVUTest/video/{file_names}"  # 替换为你的视频路径
    output_folder = f"./MLVU/data/MLVUTest/sampled_frames/{file_names}/"  # 替换为你的输出文件夹
    base64_folder = f"./MLVU/data/MLVUTest/base64_frames/{file_names}/"  # 保存 Base64 编码文件的文件夹
    
    #CPU串行處理
    #sample_frames_from_video(video_path, output_folder)
    
    #CPU並行處理
    sample_frames_parellel(video_path, output_folder)
    frame_to_base64(output_folder, base64_folder)
    '''
    
def main_base64():
    time_start = time.time()
    
    # root and folder
    re_sampleframe_root = "./MLVU/data/MLVUTest/re_sampled_frames/"
    re_base64frame_root = "./MLVU/data/MLVUTest/re_base64_frames/"
    
    os.makedirs(re_sampleframe_root, exist_ok=True)
    os.makedirs(re_base64frame_root, exist_ok=True)
    
    
    file_names = get_files_by_pattern(re_sampleframe_root, r"test_.*\.mp4$")
    for fname in file_names: 
        frame_to_base64(f"{re_sampleframe_root}{fname}/", f"{re_base64frame_root}{fname}/")
    
    time_end = time.time()
    print("Total time cost:", f"{time_end - time_start:.2f}", "s")
 
if __name__ == "__main__":
    main_base64()


'''
def frame_to_base64(frame_path):
    frames = os.listdir(frame_path)
    for frame in frames:
        with open(frame, "rb") as frame_file:
            encode_image= base64.b64encode(frame_file.read()).encoded_string.decode("utf-8")
        
        
        output_path = os.path.join(output_folder, f"{fname}_frame_{saved_count:04d}.jpg")
        cv2.imwrite(output_path, frame)
        print(f"保存图片: {output_path}")
        
if __name__ == "__main__":
    # 示例用法
    # 获取文件夹中的所有文件名
    video_root = "./MLVU/data/MLVUTest/video/"
    #file_names = [f for f in os.listdir(video_root) if os.path.isfile(os.path.join(video_root, f))]
    file_names = ["test_surveil_0.mp4", "test_surveil_1.mp4", "test_surveil_2.mp4", "test_surveil_3.mp4"]
    
    for fname in file_names: 
        video_path = f"./MLVU/data/MLVUTest/video/{fname}"  # 替换为你的视频路径
        output_folder = f"./MLVU/data/MLVUTest/sampled_frames/{fname}/"  # 替换为你的输出文件夹
        sample_frames_from_video(video_path, output_folder)
        frame_to_base64(output_folder)
        
'''