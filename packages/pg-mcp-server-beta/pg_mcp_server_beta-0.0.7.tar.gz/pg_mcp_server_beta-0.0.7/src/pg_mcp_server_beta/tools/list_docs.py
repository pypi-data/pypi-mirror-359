import json
from ..core.document_repository import get_repository

def list_docs() -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서의 전체 목록과 주요 정보를 안내합니다.

    Returns:
        dict: {
            "문서목록": [
                {
                    "문서ID": int,         # 문서 고유 ID(숫자)
                    "제목": str,           # 문서 제목(첫 줄)
                    "카테고리": str,       # 자동 분류된 카테고리
                    "파일명": str,         # 문서 파일 경로/이름
                    "태그": list[str],     # 문서에서 추출된 태그 목록
                },
                ...
            ],
            "비고": str                  # 안내 메시지(고정)
        }
        ※ 오류 시 {"오류": "..."} 형태로 반환
    """
    try:
        repository = get_repository()
        documents = repository.list_documents()
        documents_with_id = []

        for doc in documents:
            documents_with_id.append(
                {
                    "문서ID": doc["id"],  # 파일명을 ID로 사용
                    "제목": doc["title"],
                    "카테고리": doc["category"],
                    "파일명": doc["filename"],
                    "태그": doc["tags"],
                }
            )

        return {
            "문서목록": documents_with_id,
            "비고": "문서 ID(숫자)를 참고해 get_docs로 상세 내용을 확인할 수 있습니다.",
        }

    except Exception as e:
        return {
            "오류": f"문서 목록 안내 중 문제가 발생했습니다: {str(e)}"
        }
