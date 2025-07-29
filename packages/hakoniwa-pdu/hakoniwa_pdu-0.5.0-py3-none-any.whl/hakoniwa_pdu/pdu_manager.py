from typing import Optional
import os
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.impl.data_packet import DataPacket
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig  # ← 追加
from hakoniwa_pdu.impl.pdu_convertor import PduConvertor
import importlib.resources

class PduManager:
    def __init__(self):
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self.comm_service: Optional[ICommunicationService] = None
        self.b_is_initialized = False

    def get_default_offset_path(self) -> str:
        # インストール済パッケージ内の offset ディレクトリパスを取得
        return str(importlib.resources.files("hakoniwa_pdu.resources.offset"))

    def initialize(self, config_path: str, comm_service: ICommunicationService):
        if comm_service is None:
            raise ValueError("CommService is None")

        # JSONファイルからPduChannelConfigを生成
        pdu_config = PduChannelConfig(config_path)

        # CommunicationBufferにPduChannelConfigを渡して初期化
        self.comm_buffer = CommunicationBuffer(pdu_config)
        self.comm_service = comm_service
        self.b_is_initialized = True
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        self.pdu_convertor = PduConvertor(hako_binary_path, pdu_config)
        print("[INFO] PduManager initialized")

    def is_service_enabled(self) -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        current_state = self.comm_service.is_service_enabled()
        self.b_last_known_service_state = current_state
        return current_state

    async def start_service(self, uri: str = "") -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        if self.comm_service.is_service_enabled():
            print("[INFO] Service is already running")
            return False
        result = await self.comm_service.start_service(self.comm_buffer, uri)
        self.b_last_known_service_state = result
        if result:
            print(f"[INFO] Service started successfully at {uri}")
        else:
            print("[ERROR] Failed to start service")
        return result

    async def stop_service(self) -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            return False
        result = await self.comm_service.stop_service()
        self.b_last_known_service_state = not result
        return result

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        return self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        return self.comm_buffer.get_pdu_size(robot_name, pdu_name)

    async def flush_pdu_raw_data(self, robot_name: str, pdu_name: str, pdu_raw_data: bytearray) -> bool:
        if not self.is_service_enabled() or self.comm_service is None:
            return False
        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return False
        return await self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

    def read_pdu_raw_data(self, robot_name: str, pdu_name: str) -> Optional[bytearray]:
        if not self.is_service_enabled():
            return None
        return self.comm_buffer.get_buffer(robot_name, pdu_name)

    async def declare_pdu_for_read(self, robot_name: str, pdu_name: str) -> bool:
        return await self._declare_pdu(robot_name, pdu_name, is_read=True)

    async def declare_pdu_for_write(self, robot_name: str, pdu_name: str) -> bool:
        return await self._declare_pdu(robot_name, pdu_name, is_read=False)

    async def declare_pdu_for_readwrite(self, robot_name: str, pdu_name: str) -> bool:
        return (self.declare_pdu_for_read(robot_name, pdu_name) and
                self.declare_pdu_for_write(robot_name, pdu_name))

    async def _declare_pdu(self, robot_name: str, pdu_name: str, is_read: bool) -> bool:
        if not self.is_service_enabled():
            print("[WARN] Service is not enabled")
            return False

        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            print(f"[WARN] Unknown PDU: {robot_name}/{pdu_name}")
            return False

        magic_number = 0x52455044 if is_read else 0x57505044
        pdu_raw_data = bytearray(magic_number.to_bytes(4, byteorder='little'))
        return await self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

    def log_current_state(self):
        print("PduManager State:")
        print(f"  - Initialized: {self.b_is_initialized}")
        print(f"  - CommBuffer Valid: {self.comm_buffer is not None}")
        print(f"  - CommService Valid: {self.comm_service is not None}")
        print(f"  - Last Known Service State: {self.b_last_known_service_state}")