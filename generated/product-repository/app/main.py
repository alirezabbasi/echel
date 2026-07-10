from __future__ import annotations

import json


def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "generated-product",
        "architecture": "local-first",
        "source": "echel-repository-factory",
    }


if __name__ == "__main__":
    print(json.dumps(health_check(), sort_keys=True))
