import json

from ..core.document_repository import get_repository


def search_docs(query: str) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서에서 원하는 정보를 쉽고 빠르게 찾아주는 검색 도구입니다.

    Args:
        query (str): 찾고 싶은 주요 단어(쉼표 또는 공백으로 구분)

    Returns:
        dict: {
            "검색결과": list[str],   # 검색 결과(문서 chunk 리스트, 마크다운)
            "안내": str,           # 검색 결과가 없거나 안내가 필요한 경우
            "오류": str            # 오류 발생 시
            (option) "검색어": list[str],  # 사용자가 입력한 검색어(분리된 키워드, 일부 케이스)
            (option) "비고": str           # 안내 메시지(일부 케이스)
        }
        ※ 검색 결과가 없거나 오류 시 {"안내": "..."} 또는 {"오류": "..."} 형태로 반환

    Raises:
        Exception: 검색 중 문제가 발생한 경우

    Example:
        >>> search_docs("PG 결제")
        {"검색결과": ["## 원본문서 제목: ...", ...]}
        >>> search_docs("")
        {"안내": "검색어를 입력해 주세요. 예시: ..."}
    """
    if not query:
        return {
            "안내": "검색어를 입력해 주세요. 예시: '내통장 결제', '신용카드', '계좌이체' 등",
            "팁": "전체 문서 목록을 보려면 'list_docs' 도구를 사용하세요.",
        }

    try:
        # 간단한 키워드 분리
        keywords = [keyword.strip() for keyword in query.split() if keyword.strip()]

        if not keywords:
            return {
                "안내": "유효한 검색어를 입력해 주세요. 예시: '내통장 결제', '신용카드', '계좌이체' 등"
            }

        repository = get_repository()
        # 동적으로 전체 카테고리 집합 추출
        all_categories = set(doc["category"] for doc in repository.documents)
        matched_categories = [cat for cat in all_categories if cat in query]

        result = repository.search_documents(keywords)

        # result가 안내/오류 메시지면 그대로 반환
        if isinstance(result, dict) and ("안내" in result or "오류" in result):
            return result

        # result가 dict이고 '검색결과' 키가 있으면 단일 리스트로 반환
        if isinstance(result, dict) and "검색결과" in result:
            return {
                "검색어": keywords,
                "검색결과": result["검색결과"],
                "비고": "BM25 점수순으로 관련성이 높은 문서 섹션을 안내합니다.",
            }

        # 그 외는 그대로 반환 (예외적 상황)
        return result

    except Exception as e:
        return {
            "오류": f"검색 중 문제가 발생했습니다: {str(e)}",
            "안내": "다시 시도해 주시거나 다른 키워드로 검색해보세요.",
        }
