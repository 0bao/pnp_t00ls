import json

def clean_string(input_str):
    """清理字符串，移除 ':', '/', '-', '.' 字符"""
    cleaned_str = input_str.replace(":", "").replace("/", "").replace("-", "").replace(".", "")
    return cleaned_str

def get_unique_nodes(file_path):
    """ 从 JSON 文件中递归查找 CustomDeck，并返回唯一节点集合 """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 解析 JSON 文件
    except FileNotFoundError:
        print("错误: 文件未找到")
        return []
    except json.JSONDecodeError:
        print("错误: JSON 格式错误")
        return []

    # 用于存储唯一节点的集合
    nodes_set = set()

    # 递归查找 CustomDeck 字段
    def find_custom_deck(data):
        if isinstance(data, dict):  # 如果是字典
            # 检查是否有 CustomDeck 字段
            if "CustomDeck" in data:
                for deck_id, deck in data["CustomDeck"].items():
                    # 获取 FaceURL 和 BackURL 并清理字符串
                    face_url = clean_string(deck.get("FaceURL", ""))
                    back_url = clean_string(deck.get("BackURL", ""))

                    node = (
                        face_url,
                        back_url,
                        deck.get("NumWidth", 0),
                        deck.get("NumHeight", 0),
                        deck.get("BackIsHidden", False),
                        deck.get("UniqueBack", False),
                        deck.get("Type", 0)
                    )
                    nodes_set.add(node)  # 存入 set 自动去重

            # 递归处理子节点
            for value in data.values():
                find_custom_deck(value)

        elif isinstance(data, list):  # 如果是列表
            for item in data:
                find_custom_deck(item)

    # 启动递归查找
    find_custom_deck(data)

    # 转换成结构化列表
    return [
        {
            "FaceName": node[0],
            "BackName": node[1],
            "NumWidth": node[2],
            "NumHeight": node[3],
            "BackIsHidden": node[4],
            "UniqueBack": node[5],
            "Type": node[6],
        }
        for node in nodes_set
    ]
