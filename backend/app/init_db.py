import logging

from app.auth_utils import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Doctor, Patient  # noqa: F401 — 触发建表

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def init() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建/更新完成")

    db = SessionLocal()
    try:
        if not db.query(Doctor).filter(Doctor.username == "admin").first():
            db.add(Doctor(
                username="admin",
                password_hash=hash_password("admin123"),
                name="系统管理员",
                role="admin",
            ))
            logger.info("默认 admin 账号已创建  用户名: admin  密码: admin123")

        if not db.query(Doctor).filter(Doctor.username == "doctor").first():
            db.add(Doctor(
                username="doctor",
                password_hash=hash_password("doctor123"),
                name="默认医师",
                role="doctor",
            ))
            logger.info("默认 doctor 账号已创建  用户名: doctor  密码: doctor123")

        db.commit()
        logger.info("初始化完成")
    finally:
        db.close()


if __name__ == "__main__":
    init()