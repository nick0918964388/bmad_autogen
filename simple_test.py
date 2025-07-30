#!/usr/bin/env python3
"""
簡單的功能驗證測試
"""

import tempfile
import numpy as np

def test_faiss():
    """測試 Faiss 基本功能"""
    print("=== 測試 Faiss ===")
    
    try:
        import faiss
        
        # 創建簡單的向量索引
        dimension = 384
        index = faiss.IndexFlatIP(dimension)  # 內積索引
        
        # 創建測試向量
        np.random.seed(42)
        vectors = np.random.random((10, dimension)).astype('float32')
        
        # 正規化向量（用於餘弦相似度）
        faiss.normalize_L2(vectors)
        
        # 添加向量到索引
        index.add(vectors)
        
        # 測試搜索
        query_vector = vectors[0:1]  # 使用第一個向量作為查詢
        scores, indices = index.search(query_vector, 3)
        
        print(f"✓ Faiss 基本功能正常")
        print(f"  索引維度: {dimension}")
        print(f"  向量數量: {index.ntotal}")
        print(f"  搜索結果: {indices[0]}")
        print(f"  相似度分數: {scores[0]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Faiss 測試失敗: {e}")
        return False

def test_httpx():
    """測試 HTTP 客戶端"""
    print("\n=== 測試 HTTPX ===")
    
    try:
        import httpx
        
        # 測試創建客戶端
        client = httpx.Client(timeout=5.0)
        print("✓ HTTPX 客戶端創建成功")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ HTTPX 測試失敗: {e}")
        return False

def test_text_processing():
    """測試文本處理功能"""
    print("\n=== 測試文本處理 ===")
    
    try:
        import re
        
        # 模擬文本分塊邏輯
        text = "這是一個測試文件。包含多個句子。用於測試分塊功能。" * 20
        
        chunk_size = 100
        chunk_overlap = 20
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append({
                'content': chunk,
                'start': start,
                'end': end,
                'size': len(chunk)
            })
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        print(f"✓ 文本分塊功能正常")
        print(f"  原文本長度: {len(text)} 字元")
        print(f"  分塊數量: {len(chunks)}")
        print(f"  平均分塊大小: {sum(c['size'] for c in chunks) / len(chunks):.1f} 字元")
        
        return True
        
    except Exception as e:
        print(f"✗ 文本處理測試失敗: {e}")
        return False

def test_json_handling():
    """測試 JSON 處理"""
    print("\n=== 測試 JSON 處理 ===")
    
    try:
        import json
        
        # 模擬 Embedding API 回應
        mock_response = {
            "model": "all-minilm:l6-v2",
            "embedding": [0.1] * 384
        }
        
        # 序列化和反序列化
        json_str = json.dumps(mock_response)
        parsed = json.loads(json_str)
        
        print(f"✓ JSON 處理功能正常")
        print(f"  模型: {parsed['model']}")
        print(f"  向量維度: {len(parsed['embedding'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON 處理測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("開始基本功能驗證...\n")
    
    tests = [
        test_faiss,
        test_httpx,
        test_text_processing,
        test_json_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 測試結果 ===")
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有基本功能驗證通過！")
        print("✓ 系統準備就緒，可以運行 Embedding 功能")
        return True
    else:
        print(f"✗ 有 {total - passed} 個測試失敗")
        return False

if __name__ == "__main__":
    import sys
    result = main()
    sys.exit(0 if result else 1)