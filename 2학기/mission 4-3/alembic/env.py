from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- 추가: 우리의 모델 메타데이터 참조 ---
from database import SQLALCHEMY_DATABASE_URL
from models import Base

config = context.config
fileConfig(config.config_file_name)

# --- 핵심: 자동 생성이 참조할 메타데이터 ---
target_metadata = Base.metadata

def run_migrations_offline():
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,   # 컬럼 타입 변경도 감지
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = SQLALCHEMY_DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
