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

    def get(self, var_name: str, default_value: Any) -> Any:
        if var_name in self.found_values:
            val = self.found_values[var_name]
            print(f"[✔] 使用配置 {var_name} = {val}")
            return val
        else:
            print(f"[·] 使用默认值 {var_name} = {default_value}")
            return default_value

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
                return val_str
