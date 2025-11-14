from sqlalchemy import Column,BigInteger,Text,String,ForeignKey,TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UrlMapping(Base):
    __tablename__ = "url_mappings"
    id = Column(BigInteger,primary_key=True,autoincrement=True)
    long_url=Column(Text,nullable=False)
    short_code=Column(String(10),unique=True)
    user_id=Column(BigInteger,index=True)

class UrlStats(Base):
    __tablename__ = "url_stats"
    short_code=Column(
        String(10),
        ForeignKey("url_mappings.short_code",ondelete="CASCADE"),
        primary_key=True
        )
    click_count = Column(BigInteger,nullable=False,server_default="0")
    last_clicked_at = Column(TIMESTAMP)