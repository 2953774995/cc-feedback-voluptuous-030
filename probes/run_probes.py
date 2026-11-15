#!/usr/bin/env python3
"""多文档校验错误聚合验收探针。

契约：
  from voluptuous.report import validate_many
  res = validate_many(schema, [doc1, doc2])
  res.errors  [{index, path, msg}]，path 形如 "name"、"tags[0]"
  res.ok      是否全部通过
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
FAIL = 0


def probe(code, desc, fn):
    global FAIL
    try:
        fn()
        print(f"[PASS] {code} {desc}")
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {code} {desc}\n        {type(exc).__name__}: {exc}")
        FAIL += 1


def main():
    try:
        from voluptuous.report import validate_many  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] P0 导入 voluptuous.report 失败：{type(exc).__name__}: {exc}")
        print("-" * 60)
        print("探针汇总：0/4 通过")
        return 1

    import voluptuous as vol
    SCHEMA = vol.Schema({vol.Required("name"): str, "age": int})

    def p1():
        res = validate_many(SCHEMA, [{"name": "x", "age": 3}])
        assert res.ok is True and res.errors == [], res.errors

    def p2():
        res = validate_many(SCHEMA, [{"name": "x", "age": "old"}])
        assert res.errors[0]["index"] == 0 and res.errors[0]["path"] == "age", res.errors

    def p3():
        res = validate_many(SCHEMA, [{"age": 1}])
        assert any(e["path"] == "name" for e in res.errors), res.errors

    def p4():
        res = validate_many(SCHEMA, [{"name": "x"}, {"name": "y", "age": "bad"}])
        assert len(res.errors) == 1 and res.errors[0]["index"] == 1, res.errors

    probe("P1", "合法文档通过", p1)
    probe("P2", "字段路径", p2)
    probe("P3", "缺失必填字段", p3)
    probe("P4", "多文档分别定位", p4)

    print("-" * 60)
    print(f"探针汇总：{4 - FAIL}/4 通过")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
