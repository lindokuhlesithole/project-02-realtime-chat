from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    messageId: str
    conversationId: str
    senderId: str
    recipientId: str
    content: str
    timestamp: str
    status: str = "sent"

@dataclass
class Connection:
    connectionId: str
    userId: str
    connectedAt: str
