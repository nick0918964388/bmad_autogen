"""
文件處理服務
處理文件讀取、分塊、安全驗證等業務邏輯
"""

import os
import asyncio
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, AsyncGenerator, Union
from datetime import datetime
from mimetypes import guess_type
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.knowledge_base import KnowledgeBase, DocumentChunk, KnowledgeBaseStatus
from ..core.exceptions import (
    ServiceError,
    ValidationError,
    SecurityError,
    DatabaseError
)

# 設置日誌
logger = logging.getLogger(__name__)


@dataclass
class ChunkingStrategy:
    """文本分塊策略配置"""
    chunk_size: int = 1000      # 每個分塊的字元數
    chunk_overlap: int = 100    # 分塊重疊字元數
    respect_sentences: bool = True  # 是否在句子邊界分割
    respect_paragraphs: bool = True  # 是否在段落邊界分割
    min_chunk_size: int = 50    # 最小分塊大小
    max_chunk_size: int = 2000  # 最大分塊大小


@dataclass
class DocumentMetadata:
    """文件元數據"""
    file_path: str
    relative_path: str
    file_size: int
    file_type: str
    mime_type: Optional[str]
    modified_time: datetime
    encoding: Optional[str] = None
    language: Optional[str] = None


class DocumentProcessingService:
    """文件處理服務類別"""
    
    # 支援的文件格式
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.markdown', '.rst', '.py', '.js', '.ts', '.jsx', '.tsx',
        '.html', '.htm', '.css', '.json', '.xml', '.yaml', '.yml', '.ini', 
        '.cfg', '.conf', '.log', '.csv', '.sql', '.sh', '.bat', '.ps1',
        '.c', '.cpp', '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs'
    }
    
    # PDF 和 Office 文件（需要額外處理）
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
    
    # 最大文件大小 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # 分塊設定
    CHUNK_SIZE = 1000  # 每個分塊的字元數
    CHUNK_OVERLAP = 100  # 分塊重疊字元數
    
    def __init__(self, chunking_strategy: Optional[ChunkingStrategy] = None):
        self.chunking_strategy = chunking_strategy or ChunkingStrategy()
    
    async def validate_path_security(self, path: str) -> str:
        """驗證路徑安全性"""
        try:
            # 解析路徑
            resolved_path = Path(path).resolve()
            
            # 檢查路徑是否存在
            if not resolved_path.exists():
                raise ValidationError(f"指定的路徑不存在: {path}")
            
            # 檢查是否為目錄
            if not resolved_path.is_dir():
                raise ValidationError(f"指定的路徑不是一個目錄: {path}")
            
            # 檢查讀取權限
            if not os.access(resolved_path, os.R_OK):
                raise SecurityError(f"沒有讀取權限: {path}")
            
            # 防止存取系統敏感目錄
            sensitive_dirs = {
                '/root', '/etc', '/var', '/sys', '/proc', '/boot',
                'C:\\Windows', 'C:\\System', 'C:\\Program Files'
            }
            
            path_str = str(resolved_path).lower()
            for sensitive_dir in sensitive_dirs:
                if path_str.startswith(sensitive_dir.lower()):
                    raise SecurityError(f"不允許存取系統目錄: {path}")
            
            return str(resolved_path)
            
        except (OSError, PermissionError) as e:
            raise SecurityError(f"路徑驗證失敗: {str(e)}")
    
    async def scan_directory(
        self, 
        directory_path: str, 
        return_metadata: bool = True
    ) -> Union[List[Dict[str, any]], List[DocumentMetadata]]:
        """掃描目錄中的文件"""
        try:
            validated_path = await self.validate_path_security(directory_path)
            path = Path(validated_path)
            
            files_info = []
            
            # 遞歸掃描所有文件
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    # 檢查文件擴展名
                    if file_path.suffix.lower() in (self.SUPPORTED_EXTENSIONS | self.DOCUMENT_EXTENSIONS):
                        try:
                            file_stat = file_path.stat()
                            
                            # 檢查文件大小
                            if file_stat.st_size > self.MAX_FILE_SIZE:
                                logger.warning(f"文件過大，跳過: {file_path} ({file_stat.st_size} bytes)")
                                continue
                            
                            # 檢查文件權限
                            if not os.access(file_path, os.R_OK):
                                logger.warning(f"沒有讀取權限，跳過: {file_path}")
                                continue
                            
                            if return_metadata:
                                # 返回 DocumentMetadata 對象
                                metadata = DocumentMetadata(
                                    file_path=str(file_path),
                                    relative_path=str(file_path.relative_to(path)),
                                    file_size=file_stat.st_size,
                                    file_type=file_path.suffix.lower(),
                                    mime_type=guess_type(str(file_path))[0],
                                    modified_time=datetime.fromtimestamp(file_stat.st_mtime)
                                )
                                files_info.append(metadata)
                            else:
                                # 返回字典（保持向後兼容）
                                files_info.append({
                                    'path': str(file_path),
                                    'relative_path': str(file_path.relative_to(path)),
                                    'size': file_stat.st_size,
                                    'extension': file_path.suffix.lower(),
                                    'mime_type': guess_type(str(file_path))[0],
                                    'modified_time': datetime.fromtimestamp(file_stat.st_mtime)
                                })
                            
                        except (OSError, PermissionError) as e:
                            logger.warning(f"無法讀取文件資訊，跳過: {file_path} - {str(e)}")
                            continue
            
            logger.info(f"掃描完成，找到 {len(files_info)} 個支援的文件")
            return files_info
            
        except Exception as e:
            logger.error(f"目錄掃描失敗: {str(e)}")
            raise ServiceError(f"目錄掃描失敗: {str(e)}")
    
    async def read_file_content(self, file_path: str) -> str:
        """讀取文件內容"""
        try:
            path = Path(file_path)
            
            # 檢查文件類型
            if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # 文本文件直接讀取
                encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin1']
                
                for encoding in encodings:
                    try:
                        with open(path, 'r', encoding=encoding) as f:
                            content = f.read()
                        logger.debug(f"成功使用 {encoding} 編碼讀取文件: {file_path}")
                        return content
                    except UnicodeDecodeError:
                        continue
                
                raise ServiceError(f"無法解碼文件: {file_path}")
                
            elif path.suffix.lower() in self.DOCUMENT_EXTENSIONS:
                # 處理 PDF 和 Office 文件
                return await self._extract_document_content(file_path)
            
            else:
                raise ServiceError(f"不支援的文件格式: {path.suffix}")
                
        except Exception as e:
            logger.error(f"讀取文件失敗: {file_path} - {str(e)}")
            raise ServiceError(f"讀取文件失敗: {str(e)}")
    
    async def _extract_document_content(self, file_path: str) -> str:
        """提取文件內容（PDF、Office 等）"""
        # 這裡暫時返回占位符文本，實際實現需要相應的庫
        # 例如：PyPDF2, python-docx, openpyxl 等
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            # TODO: 實作 PDF 文件提取
            return f"[PDF文件內容] - {path.name}\n（需要實作 PDF 內容提取功能）"
        
        elif path.suffix.lower() in {'.doc', '.docx'}:
            # TODO: 實作 Word 文件提取
            return f"[Word文件內容] - {path.name}\n（需要實作 Word 內容提取功能）"
        
        else:
            return f"[文件內容] - {path.name}\n（需要實作對應格式的內容提取功能）"
    
    def _detect_text_language(self, text: str) -> str:
        """檢測文本語言（簡單實現）"""
        if not text:
            return "unknown"
        
        # 簡單的中文檢測
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > len(text) * 0.3:
            return "zh"
        
        # 預設為英文
        return "en"
    
    def _clean_text_content(self, text: str) -> str:
        """清理文本內容"""
        if not text:
            return ""
        
        # 移除多餘的空白和換行
        text = re.sub(r'\n\s*\n', '\n\n', text)  # 保留段落分隔
        text = re.sub(r'[ \t]+', ' ', text)      # 統一空格
        text = text.strip()
        
        return text
    
    def _find_chunk_boundaries(
        self, 
        text: str, 
        start: int, 
        target_end: int,
        strategy: ChunkingStrategy
    ) -> int:
        """找到合適的分塊邊界"""
        if target_end >= len(text):
            return len(text)
        
        # 如果策略允許在段落邊界分割
        if strategy.respect_paragraphs:
            # 向後搜索段落邊界（雙換行）
            for i in range(target_end, max(target_end - 200, start), -1):
                if i < len(text) - 1 and text[i:i+2] == '\n\n':
                    return i + 2
        
        # 如果策略允許在句子邊界分割
        if strategy.respect_sentences:
            # 定義句子結束符號
            sentence_endings = ['.', '!', '?', '。', '！', '？', '\n']
            
            # 向後搜索句子邊界
            for i in range(target_end, max(target_end - 100, start), -1):
                if i < len(text) and text[i] in sentence_endings:
                    return i + 1
        
        # 如果找不到合適的邊界，使用目標位置
        return target_end
    
    def create_text_chunks(
        self, 
        text: str, 
        document_metadata: DocumentMetadata,
        strategy: Optional[ChunkingStrategy] = None
    ) -> List[Dict[str, any]]:
        """將文本分塊（增強版）"""
        try:
            if not text or not text.strip():
                return []
            
            # 使用提供的策略或預設策略
            chunk_strategy = strategy or self.chunking_strategy
            
            # 清理文本
            cleaned_text = self._clean_text_content(text)
            text_length = len(cleaned_text)
            
            # 檢測語言
            language = self._detect_text_language(cleaned_text)
            
            chunks = []
            start = 0
            chunk_index = 0
            
            logger.debug(f"開始分塊文件: {document_metadata.relative_path}, 文本長度: {text_length}")
            
            while start < text_length:
                # 計算目標結束位置
                target_end = min(start + chunk_strategy.chunk_size, text_length)
                
                # 找到實際的分塊邊界
                actual_end = self._find_chunk_boundaries(
                    cleaned_text, start, target_end, chunk_strategy
                )
                
                # 提取分塊內容
                chunk_content = cleaned_text[start:actual_end].strip()
                
                # 檢查分塊大小
                if len(chunk_content) < chunk_strategy.min_chunk_size and actual_end < text_length:
                    # 如果分塊太小且不是最後一個分塊，擴展到最小大小
                    actual_end = min(start + chunk_strategy.min_chunk_size, text_length)
                    chunk_content = cleaned_text[start:actual_end].strip()
                
                elif len(chunk_content) > chunk_strategy.max_chunk_size:
                    # 如果分塊太大，強制截斷
                    actual_end = start + chunk_strategy.max_chunk_size
                    chunk_content = cleaned_text[start:actual_end].strip()
                
                # 創建分塊（只有非空內容才創建）
                if chunk_content:
                    chunks.append({
                        'chunk_index': chunk_index,
                        'content': chunk_content,
                        'document_path': document_metadata.relative_path,
                        'start_position': start,
                        'end_position': actual_end,
                        'chunk_size': len(chunk_content),
                        'language': language,
                        'file_type': document_metadata.file_type,
                        'encoding': document_metadata.encoding
                    })
                    chunk_index += 1
                
                # 移動到下一個分塊開始位置（考慮重疊）
                if actual_end >= text_length:
                    break
                
                next_start = actual_end - chunk_strategy.chunk_overlap
                start = max(start + 1, next_start)  # 避免無限循環
                
                # 安全檢查
                if start >= actual_end:
                    start = actual_end
            
            logger.debug(f"文件 {document_metadata.relative_path} 分塊完成，共 {len(chunks)} 個分塊")
            return chunks
            
        except Exception as e:
            logger.error(f"文本分塊失敗: {document_metadata.relative_path} - {str(e)}")
            raise ServiceError(f"文本分塊失敗: {str(e)}")
    
    async def extract_text_content(self, file_path: str) -> Tuple[str, str]:
        """提取文本內容並返回內容和編碼"""
        path = Path(file_path)
        
        if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
            return await self._extract_text_file_content(file_path)
        elif path.suffix.lower() == '.pdf':
            return await self._extract_pdf_content(file_path)
        elif path.suffix.lower() in {'.md', '.markdown'}:
            return await self._extract_markdown_content(file_path)
        else:
            raise ServiceError(f"不支援的文件格式: {path.suffix}")
    
    async def _extract_text_file_content(self, file_path: str) -> Tuple[str, str]:
        """提取純文本文件內容"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"成功使用 {encoding} 編碼讀取文件: {file_path}")
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        raise ServiceError(f"無法解碼文件: {file_path}")
    
    async def _extract_pdf_content(self, file_path: str) -> Tuple[str, str]:
        """提取 PDF 文件內容"""
        try:
            # 檢查是否有 PyPDF2 或其他 PDF 庫可用
            try:
                import PyPDF2
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = []
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append(f"[第 {page_num + 1} 頁]\n")
                            text_content.append(page_text)
                            text_content.append("\n\n")
                    
                    content = "".join(text_content)
                    logger.debug(f"成功提取 PDF 內容: {file_path}, {len(pdf_reader.pages)} 頁")
                    return content, "pdf-extracted"
                    
            except ImportError:
                logger.warning("PyPDF2 未安裝，使用佔位符內容")
                path = Path(file_path)
                return f"[PDF文件內容] - {path.name}\n（需要安裝 PyPDF2 來提取實際內容）", "placeholder"
                
        except Exception as e:
            logger.error(f"PDF 內容提取失敗: {file_path} - {str(e)}")
            path = Path(file_path)
            return f"[PDF文件內容提取失敗] - {path.name}\n錯誤: {str(e)}", "error"
    
    async def _extract_markdown_content(self, file_path: str) -> Tuple[str, str]:
        """提取 Markdown 文件內容"""
        try:
            # 先讀取原始文本
            content, encoding = await self._extract_text_file_content(file_path)
            
            # 可以在這裡添加 Markdown 特殊處理邏輯
            # 例如：移除某些 Markdown 標記，保留結構等
            
            # 保留標題結構，但簡化格式
            content = re.sub(r'^#{1,6}\s+', '# ', content, flags=re.MULTILINE)
            
            logger.debug(f"成功提取 Markdown 內容: {file_path}")
            return content, encoding
            
        except Exception as e:
            logger.error(f"Markdown 內容提取失敗: {file_path} - {str(e)}")
            raise ServiceError(f"Markdown 內容提取失敗: {str(e)}")
    
    async def process_knowledge_base(
        self, 
        knowledge_base: KnowledgeBase, 
        db: Session
    ) -> None:
        """處理知識庫（主要處理流程）"""
        try:
            logger.info(f"開始處理知識庫: {knowledge_base.name} (ID: {knowledge_base.id})")
            
            # 更新狀態為處理中
            knowledge_base.update_status(KnowledgeBaseStatus.PROCESSING)
            db.commit()
            db.refresh(knowledge_base)
            
            # 掃描目錄
            files_info = await self.scan_directory(knowledge_base.path)
            
            if not files_info:
                knowledge_base.update_status(
                    KnowledgeBaseStatus.ERROR, 
                    "指定目錄中沒有找到支援的文件"
                )
                db.commit()
                return
            
            # 處理每個文件
            total_chunks = 0
            processed_files = 0
            
            for file_info in files_info:
                try:
                    # 讀取文件內容
                    content = await self.read_file_content(file_info['path'])
                    
                    # 分塊處理
                    chunks = self.create_text_chunks(content, file_info['relative_path'])
                    
                    # 保存分塊到資料庫
                    for chunk_data in chunks:
                        chunk = DocumentChunk(
                            knowledge_base_id=knowledge_base.id,
                            document_path=chunk_data['document_path'],
                            chunk_index=chunk_data['chunk_index'],
                            content=chunk_data['content'],
                            file_size=file_info['size'],
                            file_type=file_info['extension']
                        )
                        db.add(chunk)
                    
                    total_chunks += len(chunks)
                    processed_files += 1
                    
                    # 定期提交以避免長時間鎖定
                    if processed_files % 10 == 0:
                        db.commit()
                        logger.debug(f"已處理 {processed_files}/{len(files_info)} 個文件")
                
                except Exception as e:
                    logger.warning(f"處理文件失敗，跳過: {file_info['path']} - {str(e)}")
                    continue
            
            # 更新知識庫統計
            knowledge_base.document_count = processed_files
            knowledge_base.total_chunks = total_chunks
            knowledge_base.update_status(KnowledgeBaseStatus.READY)
            
            db.commit()
            db.refresh(knowledge_base)
            
            logger.info(f"知識庫處理完成: {knowledge_base.name}, 文件數: {processed_files}, 分塊數: {total_chunks}")
            
        except Exception as e:
            logger.error(f"知識庫處理失敗: {str(e)}")
            
            # 更新錯誤狀態
            try:
                knowledge_base.update_status(KnowledgeBaseStatus.ERROR, str(e))
                db.commit()
            except SQLAlchemyError as db_error:
                logger.error(f"更新錯誤狀態失敗: {str(db_error)}")
            
            raise ServiceError(f"知識庫處理失敗: {str(e)}")
    
    async def get_processing_progress(
        self, 
        knowledge_base_id: str, 
        db: Session
    ) -> Dict[str, any]:
        """獲取處理進度"""
        try:
            knowledge_base = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == knowledge_base_id
            ).first()
            
            if not knowledge_base:
                raise ValidationError(f"知識庫不存在: {knowledge_base_id}")
            
            # 計算進度
            progress = {
                'knowledge_base_id': str(knowledge_base.id),
                'status': knowledge_base.status.value,
                'document_count': knowledge_base.document_count,
                'total_chunks': knowledge_base.total_chunks,
                'processing_started_at': knowledge_base.processing_started_at,
                'processing_completed_at': knowledge_base.processing_completed_at,
                'error_details': knowledge_base.error_details
            }
            
            return progress
            
        except Exception as e:
            logger.error(f"獲取處理進度失敗: {str(e)}")
            raise ServiceError(f"獲取處理進度失敗: {str(e)}")
    
    async def delete_knowledge_base_files(
        self, 
        knowledge_base: KnowledgeBase, 
        db: Session
    ) -> int:
        """刪除知識庫相關的所有分塊"""
        try:
            # 刪除所有分塊
            deleted_count = db.query(DocumentChunk).filter(
                DocumentChunk.knowledge_base_id == knowledge_base.id
            ).delete()
            
            db.commit()
            
            logger.info(f"已刪除知識庫 {knowledge_base.id} 的 {deleted_count} 個分塊")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"刪除知識庫分塊失敗: {str(e)}")
            db.rollback()
            raise DatabaseError(f"刪除知識庫分塊失敗: {str(e)}")


# 創建服務實例
document_processing_service = DocumentProcessingService()