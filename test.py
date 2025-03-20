#單視頻單文本生成
#輸出message僅有ABCD

import os
import json
import logging
from tqdm import tqdm
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor



# 配置日志记录器
log_file = "process.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding="utf-8"),  # 写入日志文件
        logging.StreamHandler()  # 输出到终端
    ]
)

# global variable
res_list = []
res_file = "./MLVU/data/MLVUTest/my_test_res.json"

logging.basicConfig(filename="error.log", level=logging.ERROR)
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-bcc8d8956ed1496b9e8109f6b8fbbd87",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 讀取 Base64 编码的图片内容
def get_video_list(base64_folder):
    base64_images = []
    for frame_file in os.listdir(base64_folder):
        frame_path = os.path.join(base64_folder, frame_file)
        if frame_file.endswith(".txt"):  # 确保只处理 .txt 文件
            with open(frame_path, "r", encoding="utf-8") as f:
                encoded_image = f.read().strip()
                base64_images.append(encoded_image)
    video_list = [f"data:image/jpeg;base64,{base64_image}" for base64_image in base64_images]
    return video_list

def extract_video_questions(json_file):
    """
    从 JSON 文件中提取每个视频的 question, candidates, question_type 和 question_id。

    :param json_file: JSON 文件路径
    :return: 包含提取信息的列表
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    extracted_data = []
    for item in data:
        # 检查是否包含所有需要的字段
        if all(key in item for key in ["question", "candidates", "question_type", "question_id"]):
            extracted_data.append({
                "video": item["video"],
                "question": item["question"],
                "candidates": item["candidates"],
                "question_type": item["question_type"],
                "question_id": item["question_id"]
            })

    return extracted_data

def align_base64_with_questions(base64_root, json_file):
    """
    对齐 base64 图片与 JSON 文件中的问题数据。

    :param base64_root: 存放 base64 文件夹的根目录
    :param json_file: JSON 文件路径
    :return: 对齐后的数据集
    """
    # 提取 JSON 文件中的问题数据
    questions = extract_video_questions(json_file)

    aligned_data = []

    # 使用 tqdm 显示进度条
    for question in tqdm(questions, desc="Aligning data"):
        video_name = question["video"]  # 获取视频名称
        base64_folder = os.path.join(base64_root, video_name)  # 构造对应的 base64 文件夹路径

        if os.path.exists(base64_folder):
            # 获取 base64 图片列表
            video_list = get_video_list(base64_folder)
            # 将对齐的数据存储到列表
            aligned_data.append({
                "video": video_name,
                "question": question["question"],
                "candidates": question["candidates"],
                "question_type": question["question_type"],
                "question_id": question["question_id"],
                "video_list": video_list
            })
        #else:
            #logging.warning(f"警告: 找不到对应的 base64 文件夹: {base64_folder}")

    return aligned_data

def run_Qwen_VL_Max(video_list, question_prompt, candidate):
    """
    调用 Qwen-VL-Max 模型生成对话。
    """
    system_prompt = "These frames are from a video. Please examine each frame in the sequence provided to understand the narrative or activities depicted. Based on your observations, select the option that best answers the question."
    completion = client.chat.completions.create(
        model="qwen-vl-max-latest",
        messages=[
            {"role": "system",
             "content": [
                 {"type": "text", "text": system_prompt}
             ]},
            {"role": "user",
             "content": [
                 {"type": "video", "video": video_list},
                 {"type": "text", "text": question_prompt + "Only give the best option by using alphabet. Best option:(" + candidate}
             ]}
        ]
    )
    return completion.choices[0].message.content, completion.usage

def process_single_data(data):
    """
    处理单个数据条目，调用模型并返回结果。
    """
    video_list = data['video_list']
    question_prompt = data['question']
    candidate = ",".join([f"{chr(65 + i)}.{option}" for i, option in enumerate(data['candidates'])])

    try:
        answer, usage = run_Qwen_VL_Max(video_list, question_prompt, candidate)
        return {
            "question_id": data['question_id'],
            "question_type": data['question_type'],
            "question": question_prompt,
            "candidates": candidate,
            "answer": answer,
            "usage": usage.prompt_tokens_details.video_tokens
        }
    except Exception as e:
        logging.error(f"处理结果时出错: {e}, 结果: {data['question_id']}")
        return {
            "question_id":  data['question_id'],
            "question_type": data['question_type'],
            "question": question_prompt,
            "candidates": candidate,
            "answer": 'Unknown',
            "usage": 'Unknown',
            "error": str(e)
        }
   
#json write
def append_to_json_file(file_path, new_data):
    """
    将新数据追加到 JSON 文件中的列表。

    :param file_path: JSON 文件路径
    :param new_data: 要追加的新数据（列表或单个字典）
    """
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 如果文件存在，读取现有内容
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)  # 加载现有数据
                if not isinstance(data, list):
                    raise ValueError("JSON 文件的根元素必须是一个列表")
            except json.JSONDecodeError:
                # 如果文件为空或格式错误，初始化为空列表
                data = []
    else:
        # 如果文件不存在，初始化为空列表
        data = []

    # 将新数据追加到列表中
    if isinstance(new_data, list):
        data.extend(new_data)  # 如果新数据是列表，扩展现有列表
    else:
        data.append(new_data)  # 如果新数据是单个字典，直接追加

    # 将更新后的列表写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logging.info(f"数据已成功追加到文件: {file_path}")

def main_parellel():
    # 文件路径
    #base64_root = "./MLVU/data/MLVUTest/re_base64_frames/"
    base64_root = "./MLVU/data/MLVUTest/Temp/"
    json_file = "./MLVU/data/MLVUTest/test_question.json"

    # 对齐数据
    aligned_dataset = align_base64_with_questions(base64_root, json_file)
    global res_file
    # 使用 ThreadPoolExecutor的executor.submit和future.result并行处理
    
    global res_list
    '''
    with ThreadPoolExecutor(max_workers=6) as executor:  # 设置并行线程数
        futures = {executor.submit(process_single_data, data): data for data in aligned_dataset}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing data"):
            result = future.result()
            results.append(result)
    '''
    with ThreadPoolExecutor(max_workers=6) as executor:  # 设置并行线程数
        # 使用 map 并行处理数据
        # tqdm 包裹 executor.map 以显示进度条
        results = list(tqdm(executor.map(process_single_data, aligned_dataset), 
                            total=len(aligned_dataset), 
                            desc="Processing data"))
        count = 0
        for result in results:
            res_list.append({
            "question_id": result['question_id'],
            "question_type": result['question_type'],
            "option": result['answer']
            })
            count += 1
            logging.info(f"Question ID: {result['question_id']}")
            logging.info(f"Question Type: {result['question_type']}")
            logging.info(f"Question: {result['question']}")
            logging.info(f"Answer: {result['answer']}")
            logging.info(f"video_tokens_usage:{result['usage']}")
            logging.info('-' * 50)
            
            # 每十次輸出寫入一次
            if count == 10:
                append_to_json_file(res_file, res_list)
                res_list = []
                count = 0
            
        append_to_json_file(res_file, res_list)   
        print("=" * 50, end="\n\n")


    
    # 打印结果
    '''for result in results:
        if "error" in result:
            logging.info(f"Question ID: {result['question_id']} - Error: {result['error']}")
        else:
            logging.info(f"Question ID: {result['question_id']}")
            logging.info(f"Question Type: {result['question_type']}")
            logging.info(f"Question: {result['question']}")
            logging.info(f"Candidates: {result['candidates']}")
            logging.info(f"Answer: {result['answer']}")
            logging.info('-' * 50)
            logging.info(f"Usage: {result['usage']}")
        logging.info("=" * 50, end="\n\n")
    '''
    
    
# main_casade
def main():
    
    global res_list
    #whole dataset
    #base64_root = "./MLVU/data/MLVUTest/base64_frames/"
    
    #test for one video
    base64_root = "./MLVU/data/MLVUTest/Temp/"
    json_file = "d:/BaiduSyncdisk/MyResearch/MLLM/MLVU/data/MLVUTest/test_question.json"

    # align base64 with questions with all data in base64_root
    aligned_dataset = align_base64_with_questions(base64_root, json_file)
        
    # for text in whole_text:
    for data in aligned_dataset:
        video_list = data['video_list']
        question_prompt = data['question']
        #candidate = ",".join(data['candidates']) # 将 candidates 列表转换为字符串
        candidate = ",".join([f"{chr(65 + i)}.{option}" for i, option in enumerate(data['candidates'])])
        
        # 调用模型并获取结果
        message, usage = run_Qwen_VL_Max(video_list, question_prompt, candidate)

        # 构造结果字典
        res_list.append({
            "question_id": data['question_id'],
            "question_type": data['question_type'],
            "option": message
        })
        
        # 打印问题信息到终端
        ''' 
        logging.info("=" * 50)
        logging.info(f"Question ID: {data['question_id']}")
        logging.info(f"Question Type: {data['question_type']}")
        logging.info(f"Number of Frames: {len(data['video_list'])}")
        logging.info(f"Question: {question_prompt}")
        logging.info(f"Candidates: {candidate}")
        logging.info("-" * 50)
        logging.info("The answer is:", message)
        logging.info("-" * 50)
        logging.info(usage)
        '''

if __name__ == "__main__":
    main_parellel()
    
    logging.info(f"/FINISH/ my_test_res.json: {res_file}")
        