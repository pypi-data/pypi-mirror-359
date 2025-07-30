import re

def extract_category(filename: str) -> str:
    if filename.endswith('.js'):
        # 상위 폴더명 추출
        parts = filename.split('/')
        if len(parts) > 1:
            parent = parts[-2]
            if parent == 'pg':
                return 'PG-연동스크립트'
            elif parent == 'ezauth':
                return '내통장결제-연동스크립트'
            else:
                return f'{parent}-연동스크립트'
        return '연동스크립트'
    if "pg/" in filename:
        return "PG"
    elif "ezauth/" in filename:
        return "내통장결제"
    elif "instructions.md" in filename:
        return "가이드"
    return "기타" 