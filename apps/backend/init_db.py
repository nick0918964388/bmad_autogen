#!/usr/bin/env python3
"""
資料庫初始化腳本
用於建立資料庫表格和初始資料
"""

import sys
import os
import argparse
from pathlib import Path

# 加入 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.database import init_db, drop_db, check_db_connection, get_db_info
from src.core.config import settings
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='智能助理應用程式資料庫初始化工具')
    parser.add_argument('--drop', action='store_true', help='刪除所有現有表格')
    parser.add_argument('--check', action='store_true', help='僅檢查資料庫連接')
    parser.add_argument('--info', action='store_true', help='顯示資料庫連接資訊')
    parser.add_argument('--force', action='store_true', help='強制執行操作（跳過確認）')
    
    args = parser.parse_args()
    
    # 顯示資料庫資訊
    if args.info:
        logger.info("資料庫連接資訊:")
        info = get_db_info()
        for key, value in info.items():
            logger.info(f"  {key}: {value}")
        return
    
    # 檢查資料庫連接
    if args.check:
        logger.info("檢查資料庫連接...")
        if check_db_connection():
            logger.info("✅ 資料庫連接成功")
            return
        else:
            logger.error("❌ 資料庫連接失敗")
            sys.exit(1)
    
    # 檢查基本連接
    logger.info("檢查資料庫連接...")
    if not check_db_connection():
        logger.error("❌ 資料庫連接失敗，請檢查資料庫設定")
        sys.exit(1)
    
    logger.info("✅ 資料庫連接成功")
    
    # 刪除現有表格
    if args.drop:
        if not args.force:
            confirm = input("⚠️  確定要刪除所有資料庫表格嗎？這將清除所有資料！(y/N): ")
            if confirm.lower() != 'y':
                logger.info("操作已取消")
                return
        
        logger.info("正在刪除資料庫表格...")
        if drop_db():
            logger.info("✅ 資料庫表格刪除成功")
        else:
            logger.error("❌ 資料庫表格刪除失敗")
            sys.exit(1)
    
    # 建立資料庫表格
    logger.info("正在初始化資料庫...")
    if init_db():
        logger.info("✅ 資料庫初始化成功")
        logger.info("🎉 所有資料庫表格已建立完成！")
    else:
        logger.error("❌ 資料庫初始化失敗")
        sys.exit(1)
    
    # 建立預設管理員帳號（如果需要的話）
    try:
        from src.services.auth_service import AuthService
        from src.core.database import SessionLocal
        
        db = SessionLocal()
        auth_service = AuthService(db)
        
        # 檢查是否已有管理員帳號
        admin_email = "admin@smart-assistant.com"
        existing_admin = auth_service.get_user_by_email(admin_email)
        
        if not existing_admin:
            logger.info("建立預設管理員帳號...")
            admin_user = auth_service.create_user(
                email=admin_email,
                password="admin123",
                full_name="系統管理員"
            )
            if admin_user:
                logger.info(f"✅ 預設管理員帳號已建立")
                logger.info(f"   電子郵件: {admin_email}")
                logger.info(f"   密碼: admin123")
                logger.info("   ⚠️  請在生產環境中變更預設密碼")
            else:
                logger.warning("❌ 建立預設管理員帳號失敗")
        else:
            logger.info("ℹ️  管理員帳號已存在，跳過建立")
        
        db.close()
        
    except Exception as e:
        logger.error(f"建立管理員帳號時發生錯誤: {e}")
    
    logger.info("🚀 資料庫設定完成，應用程式已準備就緒！")

if __name__ == "__main__":
    main()