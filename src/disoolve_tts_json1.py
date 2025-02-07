import json

    def get_unique_nodes(file_path):
        """ 从 JSON 文件读取数据并返回唯一节点集合 """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)  # 解析 JSON 文件
        except FileNotFoundError:
            print("错误: 文件未找到")
            return []
        except json.JSONDecodeError:
            print("错误: JSON 格式错误")
            return []

        nodes_set = set()

        def find_node_attributes(data):
            if isinstance(data, dict):  # 如果是字典
                if "FaceURL" in data:  # 确保当前节点是有效目标
                    node = (
                        data.get("FaceURL", ""),
                        data.get("BackURL", ""),
                        data.get("NumWidth", 0),
                        data.get("NumHeight", 0),
                        data.get("BackIsHidden", False),
                        data.get("UniqueBack", False),
                        data.get("Type", 0)
                    )
                    nodes_set.add(node)  # 存入 set 自动去重

                # 递归处理子节点
                for value in data.values():
                    find_node_attributes(value)

            elif isinstance(data, list):  # 如果是列表
                for item in data:
                    find_node_attributes(item)

        find_node_attributes(data)

        # 转换成结构化列表
        return [
            {
                "FaceURL": node[0],
                "BackURL": node[1],
                "NumWidth": node[2],
                "NumHeight": node[3],
                "BackIsHidden": node[4],
                "UniqueBack": node[5],
                "Type": node[6],
            }
            for node in nodes_set
        ]



