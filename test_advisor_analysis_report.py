"""测试顾问分析报告生成功能"""

import asyncio
import sys
import os
import traceback
from datetime import date
from app.db.database import Database
from app.core.event_bus import ProductionEventBus
from app.services.redis_service import RedisService
from app.services.call_records_service import CallRecordsService
from app.services.aibox_service import Aiboxservice
from app.core.logger import get_logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = get_logger(__name__)


async def test_advisor_analysis_report():
    """
    测试顾问分析报告生成功能
    
    功能测试：
    1. 从数据库获取顾问统计数据
    2. 获取前十条转录数据
    3. 生成AI分析报告
    4. 保存报告文件
    """

    # 初始化数据库连接
    database = Database()
    await database.initialize()

    # 初始化事件总线
    event_bus = ProductionEventBus()
    await event_bus.start()

    # 初始化Redis服务
    redis_service = RedisService(event_bus)
    await redis_service.initialize()

    # 初始化通话记录服务
    call_records_service = CallRecordsService(
        event_bus=event_bus, database=database, redis_service=redis_service
    )
    await call_records_service.initialize()

    # 初始化AI Box服务
    aibox_service = Aiboxservice(event_bus=event_bus, database=database, call_records_service=call_records_service)
    await aibox_service.initialize()

    try:
        # 测试生成当天顾问报告
        target_date = date.today()
        
        logger.info("=== 测试当天顾问分析报告生成 ===")
        logger.info("日期: %s", target_date)
        
        all_reports = await aibox_service.generate_advisor_analysis_report(
            target_date=target_date
        )
        
        if all_reports:
            logger.info("✅ 当天顾问报告生成成功，共 %d 个报告:", len(all_reports))
            for advisor_id, report_path in all_reports.items():
                logger.info("  顾问ID %s: %s", advisor_id, report_path)
        else:
            logger.warning("❌ 当天顾问报告生成失败")

    except Exception as e:  # pylint: disable=broad-except
        logger.error("测试过程中发生错误: %s", e)
        logger.error("错误堆栈: %s", traceback.format_exc())

    finally:
        # 清理资源
        await database.close()
        await event_bus.stop()


if __name__ == "__main__":
    asyncio.run(test_advisor_analysis_report())
