import os
import json
import logging
import time
import argparse
from PIL import Image
from adb_utils import setup_device 

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("LogReplayer")

LOG_DIR = "D:\GUIAgent\\task_logs\\20250711_085142" 

def replay_log(log_dir_path):
    """重放日志记录的任务"""
    try:
        #加载日志文件
        log_file = os.path.join(log_dir_path, "action_log.json")
        if not os.path.exists(log_file):
            logger.error(f"Log file not found: {log_file}")
            return False
        
        with open(log_file, "r", encoding="utf-8") as f:
            log_data = json.load(f)
        
        #显示任务信息
        metadata = log_data["metadata"]
        logger.info(f"Replaying task: {metadata['query']}")
        logger.info(f"Start time: {metadata['start_time']}")
        logger.info(f"Steps to replay: {len(log_data['steps'])}")
        
        #准备设备
        device = setup_device()
        
        #逐步骤重放
        for step in log_data["steps"]:
            logger.info(f"Replaying step {step['step']}: Action={step['action']}")
            
            #执行原始操作
            device.step(step["action"])
            time.sleep(1.5)  #增加延迟
            
            #显示原始响应
            if "response" in step:
                logger.debug(f"Original response: {step['response']}")
        
        logger.info(f"Task completed successfully! Result: {metadata.get('result', '')}")
        return True
    
    except Exception as e:
        logger.error(f"Replay failed: {str(e)}")
        return False

if __name__ == "__main__":
    replay_log("D:\\GUIAgent\\task_logs_new\\20250713_202634")