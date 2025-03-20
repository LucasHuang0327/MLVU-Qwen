# MLVU Test on Qwen-VL-Max-Latest

This is a **demonstration** on how to **launch** an MLVU test using an **API**🔥. 
The code was written hastily, and some issues could be explored further.
代码写得仓促, 有些问题可以深入探究一下~

## How to run:
1. **Download and unzip** the MLVU Test dataset from [🤗Hugging Face](https://huggingface.co/datasets/MLVU/MLVU_Test/tree/main).

2. **Modify the paths** in both `converter.py` and `test.py`, and **update your `API KEY`** in `test.py`.

3. **Run `converter.py`** to sample frames from videos and convert them to base64 format:
```shell
python converter.py
```

4. **Run `test.py`** to start the test:
```shell
python test.py
```

## Reminder⚠️
1. The code is **exclusively designed** for "Qwen-VL-Max-Latest". Some details may need to be adjusted to work with other Qwen-VL models to avoid errors. For example, "Qwen-VL-Max" (2024-10) only supports image list input lengths between 4 and 80, whereas this code uses 160 frames per video as input.

2. The my_test_res.json file does not contain the complete results (anomaly_reco, count, needleQA, order, tutorialQA) for the test_question set because I ran out of free tokens. 🫠

3. Using base64-encoded images seems to **reduce token usage** (by nearly 40% compared to HTTP consumption calculations) while maintaining the same performance. The average token usage per video is around 7100.

4. The API service for this experiment was purchased from **Alibaba Cloud Bailian**. 本实验的API服务从阿里云百炼所购买。
