import json

from ..core.document_repository import get_repository


def search_docs(query: str) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서에서 원하는 정보를 쉽고 빠르게 찾아주는 스마트 검색 도구입니다.
    (원문 쿼리, 띄어쓰기 조합, 표/코드 우선 등)

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
        repository = get_repository()
        results = []
        seen_chunks = set()

        # 1차: 원문 쿼리로 검색
        keywords = [query.strip()]
        result1 = repository.search_documents(keywords)
        if "검색결과" in result1:
            for entry in result1["검색결과"]:
                if entry not in seen_chunks:
                    results.append(entry)
                    seen_chunks.add(entry)

        # 2차: 띄어쓰기 분해/조합/붙여쓰기 등 다양한 쿼리로 추가 검색
        tokens = query.split()
        combos = set(tokens + [query.replace(" ", ""), query.replace(" ", "_")])
        for combo in combos:
            if not combo or combo == query:
                continue
            result2 = repository.search_documents([combo])
            if "검색결과" in result2:
                for entry in result2["검색결과"]:
                    if entry not in seen_chunks:
                        results.append(entry)
                        seen_chunks.add(entry)

        # 3차: 표/목록/코드 등 특정 섹션 우선 안내
        def is_table_or_code(entry):
            return "```" in entry or "|" in entry  # 코드블록 또는 마크다운 표

        table_or_code = [r for r in results if is_table_or_code(r)]
        others = [r for r in results if not is_table_or_code(r)]
        final_results = table_or_code + others

        if not final_results:
            return {"안내": f"'{query}'에 대한 검색 결과가 없습니다."}

        return {
            "검색어": [query],
            "검색결과": final_results,
            "비고": "원문, 띄어쓰기 조합, 표/코드 우선 등 스마트 검색 결과입니다.",
        }

    except Exception as e:
        return {
            "오류": f"검색 중 문제가 발생했습니다: {str(e)}",
            "안내": "다시 시도해 주시거나 다른 키워드로 검색해보세요.",
        }
