import json
from collections import defaultdict

def clean_string(input_str):
    """清理字符串，移除 ':', '/', '-', '.' 字符"""
    return input_str.replace(":", "").replace("/", "").replace("-", "").replace(".", "").replace("?", "").replace("=", "").replace("_", "")

def get_unique_nodes(file_path):
    """ 从 JSON 文件中递归查找 CustomDeck 和 Bags，并返回结构化数据 """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 解析 JSON 文件
    except FileNotFoundError:
        print("错误: 文件未找到")
        return {}
    except json.JSONDecodeError:
        print("错误: JSON 格式错误")
        return {}

    # 用于存储唯一的 CustomDeck 信息
    custom_deck_set = set()
    # 用于存储所有 Bag 及其 Custom_Tile 和 CustomMesh
    bags = []
    bag_counter = 1  # 用于为每个 Unknown Bag 添加编号

    def find_custom_deck(data):
        """递归查找 CustomDeck"""
        if isinstance(data, dict):
            # 处理 CustomDeck
            if "CustomDeck" in data:
                for deck_id, deck in data["CustomDeck"].items():
                    node = (
                        clean_string(deck.get("FaceURL", "")),
                        clean_string(deck.get("BackURL", "")),
                        deck.get("NumWidth", 0),
                        deck.get("NumHeight", 0),
                        deck.get("BackIsHidden", False),
                        deck.get("UniqueBack", False),
                        deck.get("Type", 0),
                        deck.get("FaceURL", ""),
                        deck.get("BackURL", "")
                    )
                    custom_deck_set.add(node)

            # 递归处理子节点
            for value in data.values():
                find_custom_deck(value)

        elif isinstance(data, list):
            for item in data:
                find_custom_deck(item)

    def find_bags(data):
        """递归查找 Name = 'Bag' 的节点，并提取 Custom_Tile 和 CustomMesh"""
        nonlocal bag_counter  # 使用外部 bag_counter 变量
        if isinstance(data, dict):
            # 仅处理 Name == "Bag" 的节点
            if data.get("Name") == "Bag" and "ContainedObjects" in data:
                bag_tiles = defaultdict(list)  # 以 BackImageName 归类多个 FrontImageNames
                rbag_tiles = defaultdict(list)  # 以 BackImageName 归类多个 FrontImageNames
                for obj in data["ContainedObjects"]:
                    # 处理 Custom_Tile
                    if isinstance(obj, dict) and obj.get("Name") == "Custom_Tile" or obj.get("Name") == "Custom_Token":
                        custom_image = obj.get("CustomImage", {})
                        if "ImageURL" in custom_image and "ImageSecondaryURL" in custom_image:
                            front_image_name = clean_string(custom_image["ImageURL"])
                            back_image_name = clean_string(custom_image["ImageSecondaryURL"])
                            bag_tiles[back_image_name].append(front_image_name)
                            rbag_tiles[front_image_name].append(back_image_name)

                    # 处理 CustomMesh
                    if isinstance(obj, dict) and "CustomMesh" in obj:
                        custom_mesh = obj["CustomMesh"]
                        if "MeshURL" in custom_mesh and "DiffuseURL" in custom_mesh:
                            front_image_name = clean_string(custom_mesh["MeshURL"])
                            back_image_name = clean_string(custom_mesh["DiffuseURL"])
                            bag_tiles[back_image_name].append(front_image_name)
                            rbag_tiles[front_image_name].append(back_image_name)


                # 合并相同的 BackImageName 和 FrontImageNames
                new_tiles = []
                for back_image_name, front_image_names in bag_tiles.items():
                    # 使用 set 合并相同的 front_image_names，去除重复项
                    unique_front_image_names = list(set(front_image_names))
                    new_tiles.append({
                        "BackImageName": back_image_name,
                        "FrontImageNames": unique_front_image_names
                    })


                # 合并相同的 BackImageName 和 FrontImageNames
                rnew_tiles = []
                for back_image_name, front_image_names in rbag_tiles.items():
                    # 使用 set 合并相同的 front_image_names，去除重复项
                    unique_front_image_names = list(set(front_image_names))
                    rnew_tiles.append({
                        "BackImageName": back_image_name,
                        "FrontImageNames": unique_front_image_names
                    })

                if len(rnew_tiles) < len(new_tiles):
                    new_tiles = rnew_tiles
                # 如果当前 Bag 下有 Custom_Tile 或 CustomMesh，则存入 bags 列表
                if new_tiles:
                    bag_name = data.get("Nickname", f"Unknown Bag {bag_counter}")  # 可能有 Bag 的昵称，或是编号
                    bags.append({
                        "BagName": clean_string(bag_name).strip(),  # 如果是 Unknown Bag，将加上编号
                        "Tiles": new_tiles
                    })
                    bag_counter += 1  # 递增编号

            # 递归处理子节点
            for value in data.values():
                find_bags(value)

        elif isinstance(data, list):
            for item in data:
                find_bags(item)

    # 启动递归查找
    find_custom_deck(data)
    find_bags(data)

    return {
        "CustomDeck": [
            {
                "FaceName": node[0],
                "BackName": node[1],
                "NumWidth": node[2],
                "NumHeight": node[3],
                "BackIsHidden": node[4],
                "UniqueBack": node[5],
                "Type": node[6],
                "FaceURL": node[7],
                "BackURL": node[8]

            }
            for node in custom_deck_set
        ],
        "Bags": bags  # 每个 Bag 下包含它的 Custom_Tile 和 CustomMesh
    }

# 示例调用
# file_path = "D:/tts/姬路城（白城堡） 正式版中文图包 by南徐舟/Mods/Workshop/3059780948.json"
# # file_path = "C:/Users/11400/Desktop/share/桌游/arnak-lost_ruins_of_arnak-阿纳克遗迹-mini/backup/失落的阿纳克遗迹中文版（全扩带脚本）Lost Ruins of Arnak - 副本/Mods/Workshop/2893704734.json"
# result = get_unique_nodes(file_path)
# print(json.dumps(result, indent=4, ensure_ascii=False))
