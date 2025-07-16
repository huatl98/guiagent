import time
from adb_utils import setup_device
import logging
import os
from agent_wrapper import MiniCPMWrapper
import numpy as np
from PIL import Image
# 引入日志记录装饰器
from log_recorder import record_task
    

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def run_task(query):
    device = setup_device()
    minicpm = MiniCPMWrapper(model_name='AgentCPM-GUI', temperature=1, use_history=True, history_size=2)
    
    is_finish = False
    while not is_finish:
        text_prompt = query
        screenshot = device.screenshot(1120)
        response = minicpm.predict_mm(text_prompt, [np.array(screenshot)])
        action = response[3]
        print(f"action:{action}")
        is_finish = device.step(action)
        time.sleep(2.5)
    return is_finish

# 只在文件末尾添加装饰器调用
if __name__ == "__main__":
    # 使用装饰器包裹原函数
    recorded_run_task = record_task(run_task)
    
    # 执行任务（自动记录日志）
    recorded_run_task("打开bilibili给李子柒的第二个视频点赞")