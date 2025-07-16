import time
from adb_utils import setup_device
import logging
import os
from agent_wrapper import MiniCPMWrapper
import numpy as np
from PIL import Image
#引入日志记录装饰器
from log_recorder import record_task
from experience_pool import Experience_Pool
from openai import OpenAI
from log_replay import replay_log

client = OpenAI(
  api_key=os.environ.get("OPENAI_KEY"),
  base_url='https://yeysai.com/v1/'
) 

model_name = "deepseek-v3-250324"

def run_task(query, logger=None):
    device = setup_device()
    minicpm = MiniCPMWrapper(model_name='AgentCPM-GUI', temperature=1, use_history=True, history_size=2)
    pool = Experience_Pool()

    history_queries = pool.get_all_queries()
    history_prompt = "以下是你之前执行过的任务：\n" + "\n".join([f"- {q}" for q in history_queries])

    system_prompt = f"""你是一个经验池匹配专家，负责判断新任务描述是否与已有经验池中的任务语义相似。请严格遵循以下规则：
    1. 目前已有经验池任务列表{history_prompt}
    2. 仅当新指令与经验池中的指令在以下两个维度完全一致时才返回匹配项：
    - 平台名称（如bilibili/百度/QQ）必须字符级一致
    - 操作对象（如老番茄/账号名称）必须完全匹配
    3. 忽略其他修饰词差异（如"打开"/"访问"等）
    4. 如果两个维度都匹配那么返回经验池中所匹配的那个query(仅仅返回query即可,不要有多余的其他内容)
    5. 只要任一核心要素变更即返回"no_match"
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    query_map = response.choices[0].message.content

    #先尝试是否能够使用经验
    #print(f"query_map:{query_map}")
    if query_map in history_queries:
        print(f"使用经验池，对应query为：{query_map}")
        log_path = pool.map[query_map]
        print(f"log_path:{log_path}")
        replay_log(log_path)
        #对新加入的日志内容进行调整
        #
        
    #若不能使用经验池
    else:
        is_finish = False
        while not is_finish:
            text_prompt = query
            screenshot = device.screenshot(1120)
            response = minicpm.predict_mm(text_prompt, [np.array(screenshot)])
            action = response[3]
            print(f"action:{action}")
            is_finish = device.step(action)
            if logger:  # 确保 logger 存在
                logger.record_step(
                    screenshot=screenshot,
                    action=action,
                    response=str(response[2])  
                )
            time.sleep(2)
        return is_finish

if __name__ == "__main__":
    recorded_run_task = record_task(run_task)
    
    #执行任务（自动记录日志）
    recorded_run_task("在bilibili上，看老番茄第1个视频，并点赞")
    #pool = Experience_Pool()
    #pool.update_query()


