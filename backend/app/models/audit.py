from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    action = Column(String, nullable=False, index=True)  # e.g., "create_patient", "update_prescription"
    resource_type = Column(String, nullable=False, index=True)  # e.g., "patient", "appointment"
    resource_id = Column(Integer, nullable=True, index=True)
    
    details = Column(Text, nullable=True)  # JSON string with additional context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
