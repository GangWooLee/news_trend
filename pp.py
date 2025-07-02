import sys

def in_venv():
    # virtualenv: sys.real_prefix 존재 여부
    # venv 모듈: base_prefix와 prefix 차이 비교
    return hasattr(sys, "real_prefix") or (sys.base_prefix != sys.prefix)

if in_venv():
    print("✅ 현재 가상환경 안에 있습니다.")
else:
    print("❌ 가상환경이 아닙니다.")
