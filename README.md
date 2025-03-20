# MLVU Test on Qwen-VL-Max-Latest

This is a dominstration on how to lanuch a MLVU test with **API**.
代码写得仓促, 有些问题还可以深入探究一下~

## How to run:
1. Download and unzip the MLVU Test dataset on [huggingface](https://huggingface.co/datasets/MLVU/MLVU_Test/tree/main)

2. Modify paths on both `converter.py` and `test.py`, and change your `API KEY` in `test.py`. 

3. run `converter.py` to sample frames from videos and convert to base64 form.
```shell
python converter.py
```

4. Run `test.py` to launch the test
```shell
python test.py
```

## Reminder
1. The code is exclusivly designed for "Qwen-VL-Max-Latest". Some details have to be adjusted to suit other Qwen-VL models in case of reporting errors. For instance, "Qwen-VL-Max" (2024-10)only supports image list input length between 4 to 80, while taking 160 frames per video as input here.

2. The my_test_res.json file is not complete result(anomaly_reco, count, needleQA, order, tutorialQA) of test_question set since I'm running out of my free tokens :'O


3. Base64 encoded image seems to reduce Tokens usage(nearly a 40% cut compared to consumption calculation for http) while maintaining same performance. The average token usage per video is around 7100.

4. The API service for this experiment was purchased from Alibaba Cloud Chain.本实验的API服务从阿里云百炼所购买。