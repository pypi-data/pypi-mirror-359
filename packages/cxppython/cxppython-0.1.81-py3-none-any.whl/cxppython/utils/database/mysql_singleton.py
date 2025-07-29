import time
import asyncio
from typing import Iterable, List, Type, Any, Union, Dict

from urllib.parse import urlparse, parse_qs
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

# 保持模型基类不变
try:
    from sqlalchemy.orm import DeclarativeBase
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    DeclarativeBase = declarative_base()

# 遵循您的要求，保留此导入
import cxppython as cc

class Base(DeclarativeBase):
    pass

# 定义模型类型，用于类型提示
ModelType = Type[Base]


class MysqlDBSingleton:
    __instance = None

    # --- 资源定义 ---
    engine: Any = None
    session_factory: Any = None
    async_engine: Union[AsyncEngine, None] = None
    async_session_factory: Any = None

    def __init__(self, mysql_config: Union[str, Dict]):
        if MysqlDBSingleton.__instance is not None:
            raise Exception("This class is a singleton. Use MysqlDBSingleton.create() to initialize.")

        # --- 初始化同步资源 ---
        self.engine = self._create_engine(mysql_config)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, class_=Session)

        # --- 初始化异步资源 ---
        self.async_engine = self._create_async_engine(mysql_config)
        self.async_session_factory = sessionmaker(
            bind=self.async_engine, expire_on_commit=False, class_=AsyncSession
        )

        MysqlDBSingleton.__instance = self
        cc.logging.info("MysqlDBSingleton initialized with both sync and async support.")

    @staticmethod
    def create(mysql_config: Union[str, Dict]):
        """
        创建并初始化数据库单例。如果已存在，则什么也不做（幂等）。
        """
        if MysqlDBSingleton.__instance is None:
            MysqlDBSingleton(mysql_config)
        return MysqlDBSingleton.__instance

    @staticmethod
    def instance():
        """获取单例实例。"""
        if MysqlDBSingleton.__instance is None:
            raise Exception("Database instance not initialized. Call create() first.")
        return MysqlDBSingleton.__instance

    # --- 会话和连接 ---
    @staticmethod
    def session() -> Session:
        """获取一个同步 SQLAlchemy Session。"""
        return MysqlDBSingleton.instance().session_factory()

    @staticmethod
    def get_db_connection():
        """获取一个同步数据库连接。"""
        return MysqlDBSingleton.instance().engine.connect()

    @staticmethod
    def async_session() -> AsyncSession:
        """获取一个异步 SQLAlchemy AsyncSession。"""
        return MysqlDBSingleton.instance().async_session_factory()

    @staticmethod
    def get_async_db_connection():
        """获取一个异步数据库连接。"""
        return MysqlDBSingleton.instance().async_engine.connect()

    # --- 引擎创建与配置解析 ---
    def _create_engine(self, mysql_config):
        config_dict, echo = self._parse_config(mysql_config)
        return create_engine(
            'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config_dict),
            pool_size=100, max_overflow=10, pool_recycle=1800,
            pool_pre_ping=True, echo=echo
        )

    def _create_async_engine(self, mysql_config):
        config_dict, echo = self._parse_config(mysql_config)
        return create_async_engine(
            'mysql+aiomysql://{user}:{password}@{host}:{port}/{database}'.format(**config_dict),
            pool_size=100, max_overflow=10, pool_recycle=1800,
            pool_pre_ping=True, echo=echo
        )

    def _parse_config(self, config):
        echo = False
        config_dict = {}
        if isinstance(config, str):
            if not config.startswith("mysql://"):
                config = f"mysql://{config}"
            parsed = urlparse(config)
            config_dict = {
                "user": parsed.username, "password": parsed.password,
                "host": parsed.hostname, "port": parsed.port or 3306,
                "database": parsed.path.lstrip("/")
            }
            query_params = parse_qs(parsed.query)
            if "echo" in query_params:
                echo = query_params["echo"][0].lower() == "true"
        else:
            config_dict = config
            if "echo" in config:
                echo = config["echo"]
        return config_dict, echo

    # --- 错误判断辅助函数 ---
    @staticmethod
    def _is_retriable_error(err: Exception) -> bool:
        """检查是否为可重试的数据库错误（连接断开或死锁）。"""
        if not isinstance(err, (OperationalError, DatabaseError)):
            return False
        # MySQL 错误码: 2006 (gone away), 2013 (lost connection), 1213 (deadlock), 1205 (lock wait timeout)
        return "gone away" in str(err).lower() or \
               (hasattr(err.orig, 'args') and err.orig.args and err.orig.args[0] in (2006, 2013, 1213, 1205))

    # --- 核心数据库操作 ---

    @staticmethod
    def add(value: Base, retries: int = 3) -> None:
        """[同步] 添加单个 ORM 对象。失败时会引发异常。"""
        for attempt in range(retries):
            try:
                with MysqlDBSingleton.session() as session, session.begin():
                    session.add(value)
                return
            except (OperationalError, DatabaseError) as err:
                if MysqlDBSingleton._is_retriable_error(err) and attempt < retries - 1:
                    cc.logging.warning(f"[SYNC] Retriable error on add(), retrying {attempt + 1}/{retries}...")
                    time.sleep(0.5 * (attempt + 1))
                    continue
                # 重试次数用尽或遇到不可重试错误，则直接抛出
                raise err

    @staticmethod
    async def async_add(value: Base, retries: int = 3) -> None:
        """[异步] 添加单个 ORM 对象。失败时会引发异常。"""
        for attempt in range(retries):
            try:
                async with MysqlDBSingleton.async_session() as session, session.begin():
                    session.add(value)
                return
            except (OperationalError, DatabaseError) as err:
                if MysqlDBSingleton._is_retriable_error(err) and attempt < retries - 1:
                    cc.logging.warning(f"[ASYNC] Retriable error on add(), retrying {attempt + 1}/{retries}...")
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise err

    @staticmethod
    def bulk_save(objects: Iterable[Base], retries: int = 3) -> None:
        """[同步] 批量保存多个 ORM 对象。失败时会引发异常。"""
        for attempt in range(retries):
            try:
                with MysqlDBSingleton.session() as session, session.begin():
                    session.bulk_save_objects(objects)
                return
            except (OperationalError, DatabaseError) as err:
                if MysqlDBSingleton._is_retriable_error(err) and attempt < retries - 1:
                    cc.logging.warning(f"[SYNC] Retriable error on bulk_save(), retrying {attempt + 1}/{retries}...")
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise err

    @staticmethod
    async def async_bulk_save(objects: Iterable[Base], retries: int = 3) -> None:
        """[异步] 批量保存多个 ORM 对象。失败时会引发异常。"""
        for attempt in range(retries):
            try:
                async with MysqlDBSingleton.async_session() as session, session.begin():
                    session.add_all(objects)
                return
            except (OperationalError, DatabaseError) as err:
                if MysqlDBSingleton._is_retriable_error(err) and attempt < retries - 1:
                    cc.logging.warning(f"[ASYNC] Retriable error on bulk_save(), retrying {attempt + 1}/{retries}...")
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise err

    @staticmethod
    def batch_insert_records(
            session: Session, model: ModelType, data: List[Dict[str, Any]], batch_size: int = 50,
            ignore_existing: bool = True, commit_per_batch: bool = True, retries: int = 3
    ) -> int:
        """[同步] 批量插入记录，可选择忽略已存在的记录。"""
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if not batch: continue
            stmt = mysql_insert(model).values(batch)
            if ignore_existing:
                stmt = stmt.prefix_with("IGNORE")
            for attempt in range(retries):
                try:
                    result = session.execute(stmt)
                    total_inserted += result.rowcount
                    if commit_per_batch: session.commit()
                    break
                except (OperationalError, DatabaseError) as e:
                    session.rollback()
                    if MysqlDBSingleton._is_retriable_error(e) and attempt < retries - 1:
                        cc.logging.warning(f"[SYNC] Retriable error in batch_insert (attempt {attempt+1}), retrying...")
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    raise e
        return total_inserted

    @staticmethod
    async def async_batch_insert_records(
            session: AsyncSession, model: ModelType, data: List[Dict[str, Any]], batch_size: int = 50,
            ignore_existing: bool = True, commit_per_batch: bool = True, retries: int = 3
    ) -> int:
        """[异步] 批量插入记录，可选择忽略已存在的记录。"""
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if not batch: continue
            stmt = mysql_insert(model).values(batch)
            if ignore_existing:
                stmt = stmt.prefix_with("IGNORE")
            for attempt in range(retries):
                try:
                    result = await session.execute(stmt)
                    total_inserted += result.rowcount
                    if commit_per_batch: await session.commit()
                    break
                except (OperationalError, DatabaseError) as e:
                    await session.rollback()
                    if MysqlDBSingleton._is_retriable_error(e) and attempt < retries - 1:
                        cc.logging.warning(f"[ASYNC] Retriable error in batch_insert (attempt {attempt+1}), retrying...")
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                    raise e
        return total_inserted

    @staticmethod
    def batch_replace_records(
            session: Session, model: ModelType, data: List[Dict[str, Any]], update_fields: List[str],
            batch_size: int = 50, commit_per_batch: bool = True, retries: int = 3
    ) -> int:
        """[同步] 批量插入或更新记录 (UPSERT)，依赖主键或唯一约束。"""
        total_changed = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if not batch: continue
            stmt = mysql_insert(model).values(batch)
            set_dict = {field: stmt.inserted[field] for field in update_fields}
            stmt = stmt.on_duplicate_key_update(**set_dict)
            for attempt in range(retries):
                try:
                    result = session.execute(stmt)
                    total_changed += result.rowcount
                    if commit_per_batch: session.commit()
                    break
                except (OperationalError, DatabaseError) as e:
                    session.rollback()
                    if MysqlDBSingleton._is_retriable_error(e) and attempt < retries - 1:
                        cc.logging.warning(f"[SYNC] Retriable error in batch_replace (attempt {attempt+1}), retrying...")
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    raise e
        return total_changed

    @staticmethod
    async def async_batch_replace_records(
            session: AsyncSession, model: ModelType, data: List[Dict[str, Any]], update_fields: List[str],
            batch_size: int = 50, commit_per_batch: bool = True, retries: int = 3
    ) -> int:
        """[异步] 批量插入或更新记录 (UPSERT)，依赖主键或唯一约束。"""
        total_changed = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if not batch: continue
            stmt = mysql_insert(model).values(batch)
            set_dict = {field: stmt.inserted[field] for field in update_fields}
            stmt = stmt.on_duplicate_key_update(**set_dict)
            for attempt in range(retries):
                try:
                    result = await session.execute(stmt)
                    total_changed += result.rowcount
                    if commit_per_batch: await session.commit()
                    break
                except (OperationalError, DatabaseError) as e:
                    await session.rollback()
                    if MysqlDBSingleton._is_retriable_error(e) and attempt < retries - 1:
                        cc.logging.warning(f"[ASYNC] Retriable error in batch_replace (attempt {attempt+1}), retrying...")
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                    raise e
        return total_changed

    # --- 测试与清理 ---
    @staticmethod
    def test_connection():
        """测试同步数据库连接。"""
        try:
            with MysqlDBSingleton.get_db_connection() as connection:
                connection.execute(text("SELECT 1"))
            cc.logging.success(f"Sync DB connection successful! Engine: {MysqlDBSingleton.instance().engine.url}")
            return True
        except Exception as e:
            cc.logging.error(f"Sync DB connection failed: {e}", exc_info=True)
            return False

    @staticmethod
    async def async_test_connection():
        """测试异步数据库连接。"""
        try:
            async with MysqlDBSingleton.get_async_db_connection() as connection:
                await connection.execute(text("SELECT 1"))
            cc.logging.success(f"Async DB connection successful! Engine: {MysqlDBSingleton.instance().async_engine.url}")
            return True
        except Exception as e:
            cc.logging.error(f"Async DB connection failed: {e}", exc_info=True)
            return False

    @staticmethod
    def close():
        """同步清理资源，关闭所有引擎。"""
        instance = MysqlDBSingleton.__instance
        if instance:
            if instance.engine:
                instance.engine.dispose()
                cc.logging.info("Sync engine disposed.")
            if instance.async_engine:
                # 异步引擎的 dispose 是一个 awaitable 方法
                # 在实践中，通常在异步事件循环关闭前调用
                # asyncio.run(instance.async_engine.dispose())
                cc.logging.warning("Async engine should be disposed in an async context. "
                                   "Call `await MysqlDBSingleton.async_close()` for proper cleanup.")
            MysqlDBSingleton.__instance = None

    @staticmethod
    async def async_close():
        """异步方式关闭和清理所有资源。"""
        instance = MysqlDBSingleton.__instance
        if instance:
            if instance.engine:
                instance.engine.dispose()
                cc.logging.info("Sync engine disposed.")
            if instance.async_engine:
                await instance.async_engine.dispose()
                cc.logging.info("Async engine disposed.")
            MysqlDBSingleton.__instance = None

