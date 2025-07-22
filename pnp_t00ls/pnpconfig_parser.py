import os
import re
from typing import Any, Dict


class PnpConfigParser:
    _pattern = re.compile(
        r'^\s*(MAX_CARD_WIDTH_MM|MAX_CARD_HEIGHT_MM|CARD_WIDTH_MM|CARD_HEIGHT_MM|'
        r'REPEAT|REPEAT_COUNT|WRITE_TEXT|ROWS|COLS|RIGHT_TO_LEFT)\s*=\s*(.+)$'
    )

    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.found_values: Dict[str, Any] = {}

        # 默认值，可按需改
        self.defaults = {
            "MAX_CARD_WIDTH_MM": 44,
            "MAX_CARD_HEIGHT_MM": 66,
            "CARD_WIDTH_MM": 42.5,
            "CARD_HEIGHT_MM": 64.5,
            "REPEAT": False,
            "REPEAT_COUNT": 0,
            "WRITE_TEXT": "",
            "ROWS": -1,
            "COLS": -1,
            "RIGHT_TO_LEFT": False,
        }

    def parse(self) -> None:
        if not os.path.isdir(self.config_dir):
            print(f"[⚠️] 配置目录不存在: {self.config_dir}")
            return

        found_any = False

        for fname in os.listdir(self.config_dir):
            if fname.endswith(".pnpcfg"):
                found_any = True
                path = os.path.join(self.config_dir, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        m = self._pattern.match(line)
                        if m:
                            var_name = m.group(1)
                            val = self._parse_value(m.group(2))
                            self.found_values[var_name] = val
                print(f"[✅] 加载配置文件: {fname}")

        if not found_any:
            print(f"[⚠️] 未找到任何 .pnpcfg 配置文件")
            return

        # 读取过程打印
        print("\n=== 配置转换过程（原始读取值） ===")
        for key in self.defaults.keys():
            raw_val = self.found_values.get(key, None)
            print(f"{key:16}: 原始值 = {raw_val}")

        # 解析后最终值打印
        print("\n=== 解析后最终值 ===")
        for key, default_val in self.defaults.items():
            val = self.get(key, default_val)
            print(f"{key:16} = {val}")
        print("\n")

    def get(self, var_name: str, default_value: Any) -> Any:
        raw_val = self.found_values.get(var_name, default_value)
        resolved = self.resolve_value(var_name, raw_val, default_value)
        return resolved

    def resolve_value(self, var_name: str, val: Any, default_value: Any) -> Any:
        if not isinstance(val, str):
            return val  # 原始数值、布尔型等

        val = val.strip()

        if val.upper() == "DEFAULT":
            return default_value

        const_match = re.match(r'^CONST\((.+)\)$', val, re.IGNORECASE)
        if const_match:
            raw_val = const_match.group(1).strip()
            parsed = self._parse_value(raw_val)
            return parsed

        fit_match = re.match(r'^FIT\((\w+)\)$', val, re.IGNORECASE)
        if fit_match:
            ref_var = fit_match.group(1)
            ref_val = self.get(ref_var, default_value)
            return ref_val

        ref_expr = re.match(r'^REF\((\w+)\s*([+\-])?\s*([\d\.]+)?\)$', val, re.IGNORECASE)
        if ref_expr:
            ref_var = ref_expr.group(1)
            op = ref_expr.group(2)
            offset = ref_expr.group(3)

            ref_val = self.get(ref_var, default_value)
            if not isinstance(ref_val, (int, float)):
                return default_value

            if op and offset:
                offset_val = float(offset)
                result = ref_val + offset_val if op == '+' else ref_val - offset_val
                return result
            else:
                return ref_val

        return self._parse_value(val)

    @staticmethod
    def _parse_value(val_str: str) -> Any:
        val_str = val_str.strip()
        if val_str.lower() == "true":
            return True
        if val_str.lower() == "false":
            return False
        try:
            return int(val_str)
        except ValueError:
            try:
                return float(val_str)
            except ValueError:
                return val_str  # 保留字符串，后续再解析



