import asyncssh
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SSHClient:
    """SSH隧道客户端，用于数据库连接"""
    
    def __init__(self):
        # SSH配置
        self.ssh_host = settings.ssh_host
        self.ssh_port = settings.ssh_port
        self.ssh_username = settings.ssh_username
        self.ssh_password = settings.ssh_password
        self.ssh_key_path = settings.ssh_key_path
        
        # 隧道配置
        self.remote_host = settings.ssh_remote_host
        self.remote_port = settings.ssh_remote_port
        self.local_port = settings.ssh_local_port
        
        # 验证必需配置
        if not all([self.ssh_host, self.ssh_username]):
            raise ValueError("SSH host and username are required")
        if not (self.ssh_password or self.ssh_key_path):
            raise ValueError("SSH password or key path is required")
        
        self.connection = None
        self.tunnel = None
        
    async def connect(self) -> bool:
        """建立SSH连接和端口转发"""
        try:
            connect_kwargs = {
                'host': self.ssh_host,
                'port': self.ssh_port,
                'username': self.ssh_username,
                'known_hosts': None,
            }
            
            if self.ssh_password:
                connect_kwargs['password'] = self.ssh_password
            else:
                connect_kwargs['client_keys'] = [self.ssh_key_path]
                
            # 建立SSH连接
            self.connection = await asyncssh.connect(**connect_kwargs)
            
            # 创建端口转发隧道
            self.tunnel = await self.connection.forward_local_port(
                '127.0.0.1', self.local_port,  # 本地绑定
                self.remote_host, self.remote_port  # 远程目标
            )
            
            logger.info(f"SSH tunnel established: localhost:{self.local_port} -> {self.remote_host}:{self.remote_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish SSH tunnel: {e}")
            await self.disconnect()  # 清理部分连接
            return False
    
    async def disconnect(self):
        """断开SSH连接和隧道"""
        if self.tunnel:
            self.tunnel.close()
            self.tunnel = None
            
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()
            self.connection = None
            logger.info("SSH tunnel closed")
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connection is not None and not self.connection.is_closing()
