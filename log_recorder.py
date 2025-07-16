import json
import os
import logging
import shutil
import time
from datetime import datetime
from functools import wraps
from PIL import Image

class TaskLogger:
    """任务日志记录器（上下文管理器）"""
    
    def __init__(self, log_dir="task_logs_new"):
        self.log_dir = log_dir
        self.log_data = {
            "metadata": {
                "start_time": None,
                "end_time": None,
                "status": "running",
                "experience_flag":"",
                "query": ""
            },
            "steps": []
        }
        self.current_step = 0
        self.log_path = None
    
    def __enter__(self):
        """开始记录日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = os.path.join(self.log_dir, timestamp)
        os.makedirs(os.path.join(self.log_dir, "screenshots"), exist_ok=True)
        self.log_data["metadata"]["start_time"] = datetime.now().isoformat()
        logging.info(f"Logger started. Logs will be saved to: {self.log_dir}")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """结束日志记录"""
        success = exc_type is None
        self.log_data["metadata"]["end_time"] = datetime.now().isoformat()
        #既不报错又要满足最后一个step状态为finish, last_step_ok标记用于防止空数组
        last_step_ok = False
        if self.log_data["steps"]:  # 检查是否为空（该处做了修改，运行时发现STATUS键没有无法运行）
            last_step_ok = (self.log_data["steps"][-1].get("action", {}).get("STATUS")=="finish")
        
        self.log_data["metadata"]["status"] = "completed" if (last_step_ok and success) else "failed"

        #先默认为不加入经验池
        self.log_data["metadata"]["experience_flag"] = False
        
        self.log_path = os.path.join(self.log_dir, "action_log.json")
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)# ensure_ascii=False来保留中文
        
        if success:
            logging.info(f"Log saved successfully to {self.log_path}")
        else:
            logging.error(f"Task failed. Log saved to {self.log_path}")
        return True  # 抑制异常传播
    
    def record_step(self, screenshot, action, response):
        """记录单步操作"""
        self.current_step += 1
        step_id = self.current_step
        
        # 保存截图
        screenshot_path = os.path.join(
            self.log_dir, "screenshots", f"step_{step_id:03d}.png"
        )
        screenshot.save(screenshot_path)
        
        #记录步骤数据
        step_data = {
            "step": step_id,
            "timestamp": datetime.now().isoformat(),
            "screenshot": screenshot_path,
            "action": action,
            "response": response
        }
        self.log_data["steps"].append(step_data)
        logging.info(f"Recorded step {step_id}: Action={action}")

def record_task(func):
    """装饰器：自动记录任务执行过程"""
    @wraps(func)
    def wrapper(query, *args, **kwargs):
        with TaskLogger() as logger:
            #记录任务开始信息
            logger.log_data["metadata"]["query"] = query
            
            #特殊处理：重定向原函数中的print操作
            def print_wrapper(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                print(f"ACTION: {message}")
                logging.info(f"Original print: {message}")
            
            # 替换原函数中的print
            original_print = print
            try:
                globals()['print'] = print_wrapper
                
                # 执行原任务函数
                result = func(query, logger=logger, *args, **kwargs)
                logger.log_data["metadata"]["result"] = result
                return result
            finally:
                globals()['print'] = original_print
    
    return wrapper