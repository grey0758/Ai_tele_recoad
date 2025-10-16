"""
微信机器人服务层

提供微信消息发送相关的业务逻辑处理
"""

import httpx
from app.core.event_bus import ProductionEventBus
from app.services.base_service import BaseService
from app.models.events import Event, EventType, EventPriority
from app.core.logger import get_logger
from app.core.config import settings
from app.core.exceptions import ExternalRequestException

logger = get_logger(__name__)


class WechatBotService(BaseService):
    """微信机器人服务类"""

    def __init__(self, event_bus: ProductionEventBus):
        super().__init__(event_bus=event_bus, service_name="WechatBotService")
        self.event_bus = event_bus

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        """注册事件监听器"""
        await self._register_listener(EventType.SEND_WECHAT_MESSAGE, self.handle_send_wechat_message, priority=EventPriority.HIGH)

    async def send_wechat_message(
        self, data: dict
    ) -> str:
        """
        发送微信消息

        Args:
            to_wxid: 接收者的微信ID
            message: 要发送的消息内容

        Returns:
            str: 发送是否成功
        """
        url = settings.wechat_bot_url

        headers = {"Content-Type": "application/json"}

        # 将token放到params字段中
        params = {"token": settings.wechat_bot_token}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url, headers=headers, json=data, params=params
                )

                if response.status_code == 200:
                    message = f"微信消息发送成功: to_wxid={data.get('to_wxid')}"
                    logger.info(message)
                    return message
                else:
                    error_message = f"微信消息发送失败: status_code={response.status_code}, response={response.text}"
                    logger.error(error_message)
                    raise ExternalRequestException(error_message)

        except Exception as e:  # pylint: disable=broad-except
            error_message = f"微信消息发送异常: to_wxid={data.get('to_wxid')}, error={str(e)}"
            logger.error(error_message)
            raise ExternalRequestException(error_message) from e

    async def handle_send_wechat_message(self, event: Event) -> str:
        """处理微信消息发送事件"""
        try:
            if not event.data:
                error_msg = "微信消息发送事件数据为空"
                logger.error(error_msg)
                return error_msg
                
            data = event.data
            
            result = await self.send_wechat_message(data)
            logger.info("微信消息发送事件处理成功: %s", result)
            return result
            
        except Exception as e:
            error_msg = f"处理微信消息发送事件失败: {str(e)}"
            logger.error(error_msg)
            return error_msg
