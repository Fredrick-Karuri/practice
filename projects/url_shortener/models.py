from sqlalchemy import Column,BigInteger,Text,String,ForeignKey,DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UrlMapping(Base):
    __tablename__ = "url_mappings"
    id = Column(BigInteger,primary_key=True,autoincrement=True)
    long_url=Column(Text,nullable=False)
    short_code=Column(String(10),unique=True,nullable=True,index=True)
    user_id=Column(BigInteger,index=True,nullable=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

class UrlStats(Base):
    __tablename__ = "url_stats"
    short_code=Column(
        String(10),
        ForeignKey("url_mappings.short_code",ondelete="CASCADE"),
        primary_key=True
        )
    click_count = Column(BigInteger,nullable=False,default="0")
    last_clicked_at = Column(DateTime(timezone=True),nullable=True)