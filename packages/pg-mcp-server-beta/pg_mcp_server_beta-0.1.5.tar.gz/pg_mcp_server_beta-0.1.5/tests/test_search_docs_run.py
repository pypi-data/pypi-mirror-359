import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from pg_mcp_server_beta.tools.search_docs import search_docs

def main():
    query = '신용카드'
    print(f"[TEST] search_docs('{query}') 호출")
    results = search_docs(query)
    print(f"[TEST] 반환 청크 수: {len(results)}")
    for i, chunk in enumerate(results):
        print(f"--- 청크 {i+1} ---")
        if isinstance(chunk, dict):
            print(chunk.get('text', str(chunk))[:500])
        else:
            print(str(chunk)[:500])

if __name__ == '__main__':
    main() 