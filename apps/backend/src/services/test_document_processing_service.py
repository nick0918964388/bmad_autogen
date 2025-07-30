"""
文件處理服務單元測試
測試文件讀取、分塊、安全驗證等業務邏輯
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from .document_processing_service import (
    DocumentProcessingService, 
    ChunkingStrategy, 
    DocumentMetadata
)
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseStatus
from ..core.exceptions import ValidationError, SecurityError, ServiceError


class TestDocumentProcessingService:
    """文件處理服務測試類別"""

    def setup_method(self):
        """每個測試方法前的設置"""
        self.service = DocumentProcessingService()

    @pytest.mark.asyncio
    async def test_validate_path_security_valid_path(self):
        """測試有效路徑的安全驗證"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validated_path = await self.service.validate_path_security(temp_dir)
            assert os.path.exists(validated_path)
            assert os.path.isabs(validated_path)

    @pytest.mark.asyncio
    async def test_validate_path_security_nonexistent_path(self):
        """測試不存在路徑的安全驗證"""
        nonexistent_path = "/nonexistent/path"
        
        with pytest.raises(ValidationError) as exc_info:
            await self.service.validate_path_security(nonexistent_path)
        
        assert "指定的路徑不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_path_security_file_instead_of_directory(self):
        """測試檔案路徑而非目錄路徑"""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValidationError) as exc_info:
                await self.service.validate_path_security(temp_file.name)
            
            assert "不是一個目錄" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_path_security_sensitive_directories(self):
        """測試敏感目錄的存取限制"""
        sensitive_paths = ["/root", "/etc", "/var", "/sys", "/proc"]
        
        for sensitive_path in sensitive_paths:
            # 只測試路徑檢查邏輯，不依賴實際目錄存在
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.is_dir', return_value=True), \
                 patch('os.access', return_value=True):
                
                with pytest.raises(SecurityError) as exc_info:
                    await self.service.validate_path_security(sensitive_path)
                
                assert "不允許存取系統目錄" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_scan_directory_with_supported_files(self):
        """測試掃描包含支援檔案的目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建測試檔案
            test_files = [
                "document.txt",
                "readme.md", 
                "script.py",
                "config.json",
                "style.css"
            ]
            
            for filename in test_files:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Content of {filename}")
            
            files_info = await self.service.scan_directory(temp_dir)
            
            assert len(files_info) == len(test_files)
            
            # 檢查檔案資訊正確性
            found_files = [info['relative_path'] for info in files_info]
            for filename in test_files:
                assert filename in found_files
            
            # 檢查檔案資訊結構
            for file_info in files_info:
                assert 'path' in file_info
                assert 'relative_path' in file_info
                assert 'size' in file_info
                assert 'extension' in file_info
                assert 'modified_time' in file_info

    @pytest.mark.asyncio
    async def test_scan_directory_filters_unsupported_files(self):
        """測試掃描過濾不支援的檔案"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建支援和不支援的檔案
            supported_file = os.path.join(temp_dir, "document.txt")
            unsupported_file = os.path.join(temp_dir, "image.png")
            
            for file_path in [supported_file, unsupported_file]:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("test content")
            
            files_info = await self.service.scan_directory(temp_dir)
            
            # 應該只找到支援的檔案
            assert len(files_info) == 1
            assert files_info[0]['relative_path'] == "document.txt"

    @pytest.mark.asyncio
    async def test_scan_directory_handles_large_files(self):
        """測試掃描處理大檔案"""
        with tempfile.TemporaryDirectory() as temp_dir:
            large_file = os.path.join(temp_dir, "large.txt")
            
            # 創建超過大小限制的檔案
            with open(large_file, 'w', encoding='utf-8') as f:
                f.write("x" * (self.service.MAX_FILE_SIZE + 1))
            
            files_info = await self.service.scan_directory(temp_dir)
            
            # 大檔案應該被跳過
            assert len(files_info) == 0

    @pytest.mark.asyncio
    async def test_scan_directory_recursive(self):
        """測試遞歸掃描子目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建子目錄結構
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            
            # 在根目錄和子目錄創建檔案
            root_file = os.path.join(temp_dir, "root.txt")
            sub_file = os.path.join(subdir, "sub.txt")
            
            for file_path in [root_file, sub_file]:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("test content")
            
            files_info = await self.service.scan_directory(temp_dir)
            
            assert len(files_info) == 2
            relative_paths = [info['relative_path'] for info in files_info]
            assert "root.txt" in relative_paths
            assert os.path.join("subdir", "sub.txt") in relative_paths

    @pytest.mark.asyncio
    async def test_read_file_content_utf8(self):
        """測試讀取 UTF-8 編碼檔案"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            test_content = "這是測試內容\nLine 2\nLine 3"
            f.write(test_content)
            f.flush()
            
            try:
                content = await self.service.read_file_content(f.name)
                assert content == test_content
            finally:
                os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_read_file_content_different_encodings(self):
        """測試讀取不同編碼的檔案"""
        encodings_to_test = ['utf-8', 'gbk', 'big5']
        test_content = "測試內容"
        
        for encoding in encodings_to_test:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(test_content.encode(encoding))
                f.flush()
                
                try:
                    content = await self.service.read_file_content(f.name)
                    assert test_content in content  # 可能包含額外字符
                finally:
                    os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_read_file_content_unsupported_format(self):
        """測試讀取不支援格式的檔案"""
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as f:
            f.write(b"some content")
            f.flush()
            
            try:
                with pytest.raises(ServiceError) as exc_info:
                    await self.service.read_file_content(f.name)
                
                assert "不支援的文件格式" in str(exc_info.value)
            finally:
                os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_extract_document_content_pdf(self):
        """測試 PDF 文件內容提取（占位符實作）"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            f.flush()
            
            try:
                content = await self.service._extract_document_content(f.name)
                assert "[PDF文件內容]" in content
                assert os.path.basename(f.name) in content
            finally:
                os.unlink(f.name)

    def test_create_text_chunks_basic(self):
        """測試基本文字分塊功能"""
        text = "這是一段測試文字。" * 100  # 創建足夠長的文字
        document_path = "test.txt"
        
        chunks = self.service.create_text_chunks(text, document_path)
        
        assert len(chunks) > 0
        
        # 檢查分塊結構
        for i, chunk in enumerate(chunks):
            assert chunk['chunk_index'] == i
            assert chunk['document_path'] == document_path
            assert 'content' in chunk
            assert 'start_position' in chunk
            assert 'end_position' in chunk
            assert len(chunk['content']) <= self.service.CHUNK_SIZE

    def test_create_text_chunks_empty_text(self):
        """測試空文字分塊"""
        chunks = self.service.create_text_chunks("", "test.txt")
        assert len(chunks) == 0

    def test_create_text_chunks_short_text(self):
        """測試短文字分塊"""
        short_text = "短文字"
        chunks = self.service.create_text_chunks(short_text, "test.txt")
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == short_text
        assert chunks[0]['chunk_index'] == 0

    def test_create_text_chunks_sentence_boundary(self):
        """測試在句子邊界分塊"""
        text = "第一句話。第二句話！第三句話？" + "填充文字" * 200
        chunks = self.service.create_text_chunks(text, "test.txt")
        
        # 檢查是否在標點符號處分割
        if len(chunks) > 1:
            first_chunk = chunks[0]['content']
            # 應該在句子結束符後分割
            assert first_chunk.endswith(('。', '！', '？'))

    @pytest.mark.asyncio
    async def test_process_knowledge_base_success(self):
        """測試成功處理知識庫"""
        # 創建模擬的知識庫和資料庫會話
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "測試知識庫"
        mock_kb.path = "/test/path"
        mock_kb.update_status = Mock()
        
        mock_db = Mock(spec=Session)
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.add = Mock()
        
        # 模擬掃描目錄結果
        mock_files = [
            {
                'path': '/test/path/file1.txt',
                'relative_path': 'file1.txt',
                'size': 100,
                'extension': '.txt'
            },
            {
                'path': '/test/path/file2.md',
                'relative_path': 'file2.md', 
                'size': 200,
                'extension': '.md'
            }
        ]
        
        with patch.object(self.service, 'scan_directory', return_value=mock_files) as mock_scan, \
             patch.object(self.service, 'read_file_content', return_value="測試內容") as mock_read, \
             patch.object(self.service, 'create_text_chunks', return_value=[
                 {'chunk_index': 0, 'content': '測試分塊', 'document_path': 'file1.txt'}
             ]) as mock_chunks:
            
            await self.service.process_knowledge_base(mock_kb, mock_db)
            
            # 驗證方法被正確呼叫
            mock_scan.assert_called_once_with(mock_kb.path)
            assert mock_read.call_count == len(mock_files)
            assert mock_chunks.call_count == len(mock_files)
            
            # 驗證狀態更新
            mock_kb.update_status.assert_called_with(KnowledgeBaseStatus.READY)
            mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_process_knowledge_base_no_files(self):
        """測試處理沒有支援檔案的知識庫"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.name = "空知識庫"
        mock_kb.path = "/empty/path"
        mock_kb.update_status = Mock()
        
        mock_db = Mock(spec=Session)
        mock_db.commit = Mock()
        
        with patch.object(self.service, 'scan_directory', return_value=[]):
            await self.service.process_knowledge_base(mock_kb, mock_db)
            
            # 應該設置為錯誤狀態
            mock_kb.update_status.assert_called_with(
                KnowledgeBaseStatus.ERROR,
                "指定目錄中沒有找到支援的文件"
            )

    @pytest.mark.asyncio
    async def test_process_knowledge_base_handles_file_errors(self):
        """測試處理檔案讀取錯誤"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.name = "測試知識庫"
        mock_kb.path = "/test/path"
        mock_kb.update_status = Mock()
        
        mock_db = Mock(spec=Session)
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.add = Mock()
        
        mock_files = [
            {
                'path': '/test/path/good.txt',
                'relative_path': 'good.txt',
                'size': 100,
                'extension': '.txt'
            },
            {
                'path': '/test/path/bad.txt',
                'relative_path': 'bad.txt',
                'size': 100,
                'extension': '.txt'
            }
        ]
        
        def mock_read_file(path):
            if 'bad.txt' in path:
                raise ServiceError("讀取失敗")
            return "正常內容"
        
        with patch.object(self.service, 'scan_directory', return_value=mock_files), \
             patch.object(self.service, 'read_file_content', side_effect=mock_read_file), \
             patch.object(self.service, 'create_text_chunks', return_value=[
                 {'chunk_index': 0, 'content': '測試分塊', 'document_path': 'good.txt'}
             ]):
            
            await self.service.process_knowledge_base(mock_kb, mock_db)
            
            # 應該成功處理好的檔案，跳過壞的檔案
            mock_kb.update_status.assert_called_with(KnowledgeBaseStatus.READY)

    @pytest.mark.asyncio
    async def test_get_processing_progress(self):
        """測試獲取處理進度"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        mock_kb.status = KnowledgeBaseStatus.PROCESSING
        mock_kb.document_count = 5
        mock_kb.total_chunks = 20
        mock_kb.processing_started_at = "2023-01-01T00:00:00"
        mock_kb.processing_completed_at = None
        mock_kb.error_details = None
        
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_kb
        mock_db.query.return_value = mock_query
        
        progress = await self.service.get_processing_progress("test-kb-id", mock_db)
        
        assert progress['knowledge_base_id'] == "test-kb-id"
        assert progress['status'] == "processing"
        assert progress['document_count'] == 5
        assert progress['total_chunks'] == 20

    @pytest.mark.asyncio
    async def test_get_processing_progress_not_found(self):
        """測試獲取不存在知識庫的進度"""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with pytest.raises(ValidationError) as exc_info:
            await self.service.get_processing_progress("nonexistent-id", mock_db)
        
        assert "知識庫不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_knowledge_base_files(self):
        """測試刪除知識庫檔案"""
        mock_kb = Mock(spec=KnowledgeBase)
        mock_kb.id = "test-kb-id"
        
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.delete.return_value = 15  # 模擬刪除了 15 個分塊
        mock_db.query.return_value = mock_query
        mock_db.commit = Mock()
        
        deleted_count = await self.service.delete_knowledge_base_files(mock_kb, mock_db)
        
        assert deleted_count == 15
        mock_db.commit.assert_called_once()

    def test_supported_extensions(self):
        """測試支援的檔案擴展名"""
        expected_extensions = {
            '.txt', '.md', '.markdown', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx',
            '.html', '.htm', '.css', '.json', '.xml', '.yaml', '.yml', '.ini', 
            '.cfg', '.conf', '.log', '.csv', '.sql', '.sh', '.bat', '.ps1',
            '.c', '.cpp', '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs'
        }
        
        assert self.service.SUPPORTED_EXTENSIONS == expected_extensions

    def test_document_extensions(self):
        """測試文件格式擴展名"""
        expected_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
        assert self.service.DOCUMENT_EXTENSIONS == expected_extensions

    def test_chunk_configuration(self):
        """測試分塊配置"""
        assert self.service.CHUNK_SIZE == 1000
        assert self.service.CHUNK_OVERLAP == 100
        assert self.service.MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB


class TestChunkingStrategy:
    """分塊策略測試類別"""
    
    def test_default_chunking_strategy(self):
        """測試預設分塊策略"""
        strategy = ChunkingStrategy()
        
        assert strategy.chunk_size == 1000
        assert strategy.chunk_overlap == 100
        assert strategy.respect_sentences is True
        assert strategy.respect_paragraphs is True
        assert strategy.min_chunk_size == 50
        assert strategy.max_chunk_size == 2000
    
    def test_custom_chunking_strategy(self):
        """測試自定義分塊策略"""
        strategy = ChunkingStrategy(
            chunk_size=500,
            chunk_overlap=50,
            respect_sentences=False,
            respect_paragraphs=False,
            min_chunk_size=25,
            max_chunk_size=1000
        )
        
        assert strategy.chunk_size == 500
        assert strategy.chunk_overlap == 50
        assert strategy.respect_sentences is False
        assert strategy.respect_paragraphs is False
        assert strategy.min_chunk_size == 25
        assert strategy.max_chunk_size == 1000


class TestDocumentMetadata:
    """文件元數據測試類別"""
    
    def test_document_metadata_creation(self):
        """測試文件元數據創建"""
        metadata = DocumentMetadata(
            file_path="/test/path/file.txt",
            relative_path="file.txt",
            file_size=1024,
            file_type=".txt",
            mime_type="text/plain",
            modified_time=datetime.now(),
            encoding="utf-8",
            language="en"
        )
        
        assert metadata.file_path == "/test/path/file.txt"
        assert metadata.relative_path == "file.txt"
        assert metadata.file_size == 1024
        assert metadata.file_type == ".txt"
        assert metadata.mime_type == "text/plain"
        assert metadata.encoding == "utf-8"
        assert metadata.language == "en"


class TestEnhancedChunking:
    """增強分塊功能測試類別"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.service = DocumentProcessingService()
        self.metadata = DocumentMetadata(
            file_path="/test/file.txt",
            relative_path="file.txt",
            file_size=1000,
            file_type=".txt",
            mime_type="text/plain",
            modified_time=datetime.now(),
            encoding="utf-8"
        )
    
    def test_detect_text_language_chinese(self):
        """測試中文語言檢測"""
        chinese_text = "這是一段中文文本，用於測試語言檢測功能。"
        language = self.service._detect_text_language(chinese_text)
        assert language == "zh"
    
    def test_detect_text_language_english(self):
        """測試英文語言檢測"""
        english_text = "This is an English text for language detection testing."
        language = self.service._detect_text_language(english_text)
        assert language == "en"
    
    def test_detect_text_language_empty(self):
        """測試空文本語言檢測"""
        language = self.service._detect_text_language("")
        assert language == "unknown"
    
    def test_clean_text_content(self):
        """測試文本清理功能"""
        messy_text = "  Line 1  \n\n\n  Line 2  \t\t\n\n\n  Line 3  "
        cleaned = self.service._clean_text_content(messy_text)
        
        assert cleaned == "Line 1\n\nLine 2\n\nLine 3"
    
    def test_clean_text_content_empty(self):
        """測試空文本清理"""
        cleaned = self.service._clean_text_content("")
        assert cleaned == ""
    
    def test_find_chunk_boundaries_paragraph(self):
        """測試段落邊界查找"""
        text = "第一段內容。\n\n第二段內容。\n\n第三段內容。"
        strategy = ChunkingStrategy(respect_paragraphs=True)
        
        # 在第二段開始前找邊界
        boundary = self.service._find_chunk_boundaries(text, 0, 10, strategy)
        
        # 應該找到段落邊界
        assert boundary > 0
        assert text[boundary-2:boundary] == "\n\n" or boundary == len(text)
    
    def test_find_chunk_boundaries_sentence(self):
        """測試句子邊界查找"""
        text = "第一句話。第二句話！第三句話？第四句話。"
        strategy = ChunkingStrategy(respect_sentences=True, respect_paragraphs=False)
        
        boundary = self.service._find_chunk_boundaries(text, 0, 10, strategy)
        
        # 應該在句子結束符後分割
        if boundary > 0 and boundary < len(text):
            assert text[boundary-1] in ['。', '！', '？']
    
    def test_create_text_chunks_enhanced(self):
        """測試增強分塊功能"""
        text = "第一段內容。這是第一段的詳細說明。\n\n第二段內容。這是第二段的詳細說明。\n\n第三段內容。"
        
        chunks = self.service.create_text_chunks(text, self.metadata)
        
        assert len(chunks) > 0
        
        # 檢查增強的分塊資訊
        for chunk in chunks:
            assert 'chunk_index' in chunk
            assert 'content' in chunk
            assert 'document_path' in chunk
            assert 'start_position' in chunk
            assert 'end_position' in chunk
            assert 'chunk_size' in chunk
            assert 'language' in chunk
            assert 'file_type' in chunk
            assert 'encoding' in chunk
            
            # 驗證資料類型
            assert isinstance(chunk['chunk_index'], int)
            assert isinstance(chunk['content'], str)
            assert isinstance(chunk['start_position'], int)
            assert isinstance(chunk['end_position'], int)
            assert isinstance(chunk['chunk_size'], int)
    
    def test_create_text_chunks_custom_strategy(self):
        """測試自定義分塊策略"""
        text = "這是一段很長的文本。" * 50
        
        custom_strategy = ChunkingStrategy(
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_size=50,
            max_chunk_size=300
        )
        
        chunks = self.service.create_text_chunks(text, self.metadata, custom_strategy)
        
        assert len(chunks) > 0
        
        # 檢查分塊大小符合策略
        for chunk in chunks:
            chunk_size = len(chunk['content'])
            assert chunk_size >= custom_strategy.min_chunk_size
            assert chunk_size <= custom_strategy.max_chunk_size
    
    def test_create_text_chunks_empty_text(self):
        """測試空文本分塊"""
        chunks = self.service.create_text_chunks("", self.metadata)
        assert len(chunks) == 0
    
    def test_create_text_chunks_short_text(self):
        """測試短文本分塊"""
        short_text = "短文本"
        chunks = self.service.create_text_chunks(short_text, self.metadata)
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == short_text
        assert chunks[0]['language'] == "zh"  # 中文文本
    
    @pytest.mark.asyncio
    async def test_extract_text_content_success(self):
        """測試文本內容提取成功"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            test_content = "這是測試內容"
            f.write(test_content)
            f.flush()
            
            try:
                content, encoding = await self.service.extract_text_content(f.name)
                assert content == test_content
                assert encoding == "utf-8"
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_extract_text_content_unsupported(self):
        """測試不支援格式的內容提取"""
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as f:
            f.write(b"content")
            f.flush()
            
            try:
                with pytest.raises(ServiceError) as exc_info:
                    await self.service.extract_text_content(f.name)
                
                assert "不支援的文件格式" in str(exc_info.value)
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_extract_markdown_content(self):
        """測試 Markdown 內容提取"""
        markdown_content = "# 標題\n\n## 副標題\n\n段落內容。"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown_content)
            f.flush()
            
            try:
                content, encoding = await self.service._extract_markdown_content(f.name)
                
                assert "標題" in content
                assert "段落內容" in content
                assert encoding == "utf-8"
            finally:
                os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_scan_directory_with_metadata(self):
        """測試掃描目錄返回元數據"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 創建測試文件
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("test content")
            
            # 掃描並獲取元數據
            metadata_list = await self.service.scan_directory(temp_dir, return_metadata=True)
            
            assert len(metadata_list) == 1
            assert isinstance(metadata_list[0], DocumentMetadata)
            
            metadata = metadata_list[0]
            assert metadata.relative_path == "test.txt"
            assert metadata.file_type == ".txt"
            assert metadata.file_size > 0
            assert metadata.mime_type == "text/plain"