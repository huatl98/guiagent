import json
import os

#updata_path为日志路径用于更新日志
update_path = "./task_logs_new"
file_name = "action_log.json"

class Experience_Pool:
    def __init__(self, pool_file = "./experience_pool.json"):
        self.pool_file = pool_file
        self.experiences = self._load_pool()
        self.map = self._load_map()
    
    def _load_pool(self):
        """加载经验池"""
        if os.path.exists(self.pool_file):
            with open(self.pool_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
                return data.get("experiences", [])
        return []
    
    def _load_map(self):
        """加载映射"""
        path_map = {exp["query"]: exp["log_path"] 
            for exp in self.experiences}
        return path_map
    
    def save_pool(self):
        """保存经验池"""
        with open(self.pool_file, 'w', encoding="utf-8") as f:
            json.dump({"experiences": self.experiences}, f, indent=2, ensure_ascii=False)

    def get_all_queries(self):
        """获取所有query列表"""
        return [exp["query"] for exp in self.experiences]
    
    def add_experience(self, query, log_path):
        """添加新经验"""
        #检查是否已存在相同query
        if query in self.get_all_queries():
            return False
            
        self.experiences.append({
            "query": query,
            "log_path": log_path
        })
        return True
    
    #读取日志更新经验池
    def update_query(self):
        for file in os.listdir(update_path):
            file_path = os.path.join(update_path, file) #日志文件夹
            file_path_log = os.path.join(file_path, file_name)#日志action_log.json
            with open(file_path_log, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data["metadata"]["experience_flag"] == True:
                self.add_experience(data["metadata"]["query"], file_path)
        self.save_pool()
        return True