import os
import json
import logging
import time
import argparse
from PIL import Image
from adb_utils import setup_device  # 确保设备操作可用

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("LogReplayer")

def replay_log(log_dir_path):
    """重放日志记录的任务"""
    try:
        # 加载日志文件
        log_file = os.path.join(log_dir_path, "action_log.json")
        if not os.path.exists(log_file):
            logger.error(f"Log file not found: {log_file}")
            return False
        
        with open(log_file) as f:
            log_data = json.load(f)
        
        # 显示任务信息
        metadata = log_data["metadata"]
        logger.info(f"Replaying task: {metadata['query']}")
        logger.info(f"Start time: {metadata['start_time']}")
        logger.info(f"Steps to replay: {len(log_data['steps'])}")
        
        # 准备设备
        device = setup_device()
        
        # 逐步骤重放
        for step in log_data["steps"]:
            logger.info(f"Replaying step {step['step']}: Action={step['action']}")
            
            # 显示原始截图（可选）
            if os.path.exists(step["screenshot"]):
                Image.open(step["screenshot"]).show()
            
            # 执行原始操作
            device.step(step["action"])
            time.sleep(2.5)  # 与原任务相同的延迟
            
            # 显示原始响应（调试用）
            if "response" in step:
                logger.debug(f"Original response: {step['response']}")
        
        logger.info(f"Task completed successfully! Result: {metadata.get('result', '')}")
        return True
    
    except Exception as e:
        logger.error(f"Replay failed: {str(e)}")
        return False

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='Replay task execution log')
    parser.add_argument('log_dir', type=str, help='Path to log directory')
    args = parser.parse_args()
    
    replay_log(args.log_dir)