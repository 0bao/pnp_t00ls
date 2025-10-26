import os
import re
from libs.file_collector_with_ignore.file_collector_with_ignore import collect_files  # ✅ 引入你提供的脚本

from pnpconfig_parser import PnpConfigParser  # 直接导入你的解析器类
from typing import Dict, Any

def collect_pnpcfgs(base_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    递归扫描目录下所有 .pnpcfg 文件，并使用 PnpConfigParser 解析。
    返回 {目录路径: 配置字典}
    """
    cfg_map = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pnpcfg"):
                parser = PnpConfigParser(root)
                parser.parse()
                cfg_map[root] = parser.found_values.copy()
    return cfg_map


def get_effective_config(filepath: str, cfg_map: Dict[str, Dict[str, Any]], base_dir: str) -> Dict[str, Any]:
    """
    计算给定文件路径的“最终生效配置”
    - 会向上查找父目录的配置
    - 子目录配置覆盖父目录配置
    """
    base_dir = os.path.abspath(base_dir)
    file_dir = os.path.dirname(os.path.abspath(filepath))

    merged = {}
    dirs = []
    current = file_dir
    while True:
        dirs.append(current)
        if current == base_dir:
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    dirs.reverse()

    for d in dirs:
        if d in cfg_map:
            merged.update(cfg_map[d])

    return merged


def main():
    base_dir = input("请输入要扫描的根目录路径：").strip().strip('"')
    print(f"\n📁 扫描路径: {base_dir}\n")

    # 第一步：收集所有目标文件
    files = collect_files(base_dir)
    print(f"共找到 {len(files)} 个文件")

    # 第二步：收集并解析所有 .pnpcfg
    cfg_map = collect_pnpcfgs(base_dir)
    print(f"共解析 {len(cfg_map)} 个配置目录\n")

    # 第三步：为每个文件计算最终配置
    for f in files:
        cfg = get_effective_config(f, cfg_map, base_dir)
        print(f"\n=== 文件: {f} ===")
        for k, v in cfg.items():
            print(f"  {k:16} = {v}")


if __name__ == "__main__":
    main()