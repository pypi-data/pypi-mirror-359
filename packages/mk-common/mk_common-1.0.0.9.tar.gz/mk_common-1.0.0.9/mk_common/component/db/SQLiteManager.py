import sqlite3
import pandas as pd
from typing import List, Optional, Union, Dict, Tuple
from loguru import logger


class SQLiteManager:
    def __init__(self, db_name: str = 'example.db'):
        """初始化数据库连接"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        logger.info(f"成功连接到数据库 {db_name}")

    def create_table(self, table_name: str, create_sql: str):
        """
        创建表（必须传入表名和完整的创建SQL语句）
        :param table_name: 表名
        :param create_sql: 完整的CREATE TABLE SQL语句
        """
        # 验证SQL语句是否包含表名
        if table_name.lower() not in create_sql.lower():
            logger.error(f"创建语句中未包含指定的表名 '{table_name}'")
            raise ValueError(f"创建语句中未包含指定的表名 '{table_name}'")

        try:
            # 执行创建语句
            self.cursor.execute(create_sql)
            self.conn.commit()
            logger.info(f"表 '{table_name}' 已成功创建")
            return True
        except sqlite3.Error as e:
            logger.error(f"创建表失败: {e}")
            raise

    def drop_table(self, table_name: str, if_exists: bool = True):
        """
        删除表
        :param table_name: 要删除的表名
        :param if_exists: 是否添加IF EXISTS子句
        """
        if_exists_clause = "IF EXISTS " if if_exists else ""
        drop_sql = f"DROP TABLE {if_exists_clause}{table_name}"

        try:
            self.cursor.execute(drop_sql)
            self.conn.commit()
            logger.info(f"表 '{table_name}' 已成功删除")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除表失败: {e}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(check_sql, (table_name,))
        return self.cursor.fetchone() is not None

    def create_index(self, table_name: str, columns: Union[str, List[str]],
                     index_name: Optional[str] = None, unique: bool = False,
                     if_not_exists: bool = True):
        """
        创建索引
        :param table_name: 表名
        :param columns: 索引列名（单个或多个）
        :param index_name: 索引名称（可选，自动生成）
        :param unique: 是否创建唯一索引
        :param if_not_exists: 是否添加IF NOT EXISTS子句
        """
        # 处理列名
        if isinstance(columns, str):
            columns = [columns]

        # 生成索引名称（如果未提供）
        if not index_name:
            col_str = '_'.join(columns)
            index_name = f"idx_{table_name}_{col_str}"

        # 构建索引列字符串
        columns_str = ', '.join(columns)

        # 构建CREATE INDEX语句
        unique_str = "UNIQUE" if unique else ""
        if_exists = "IF NOT EXISTS" if if_not_exists else ""
        create_index_sql = (
            f"CREATE {unique_str} INDEX {if_exists} {index_name} "
            f"ON {table_name} ({columns_str})"
        )

        try:
            self.cursor.execute(create_index_sql)
            self.conn.commit()
            logger.info(f"成功创建索引 '{index_name}' 在表 '{table_name}' 的列 {columns}")
            return True
        except sqlite3.OperationalError as e:
            logger.error(f"创建索引失败: {e}")
            return False

    def drop_index(self, index_name: str):
        """删除索引"""
        drop_sql = f"DROP INDEX IF EXISTS {index_name}"
        try:
            self.cursor.execute(drop_sql)
            self.conn.commit()
            logger.info(f"索引 '{index_name}' 已删除")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除索引失败: {e}")
            return False

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """获取表的列信息"""
        return self.query_to_dataframe(f"PRAGMA table_info({table_name})")

    def get_indexes(self, table_name: str) -> pd.DataFrame:
        """获取表的索引信息"""
        return self.query_to_dataframe(f"PRAGMA index_list({table_name})")

    def get_index_info(self, index_name: str) -> pd.DataFrame:
        """获取索引的详细信息"""
        return self.query_to_dataframe(f"PRAGMA index_info({index_name})")

    def insert_dataframe(self, df: pd.DataFrame, table_name: str,
                         if_exists: str = 'append', index: bool = False):
        """
        将整个DataFrame插入到数据库表中
        :param df: 要插入的DataFrame
        :param table_name: 目标表名
        :param if_exists: {'fail', 'replace', 'append'} 表存在时的处理方式
        :param index: 是否将DataFrame索引作为一列插入
        """
        try:
            # 将DataFrame写入SQLite
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=index)
            logger.info(f"成功插入 {len(df)} 行数据到表 '{table_name}' (模式: {if_exists})")
            return True
        except ValueError as e:
            logger.error(f"插入DataFrame失败: {e}")
            return False

    def insert_record(self, table_name: str, data: dict):
        """
        插入单条记录
        :param table_name: 表名
        :param data: 列名和值的字典
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(insert_sql, tuple(data.values()))
            self.conn.commit()
            logger.info(f"插入数据到 {table_name}: {data}")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"插入记录失败: {e}")
            return None

    def update_data(self, table_name: str, set_values: dict, condition: str = ""):
        """
        更新数据
        :param table_name: 表名
        :param set_values: 要更新的列和值
        :param condition: WHERE条件语句
        """
        set_clause = ', '.join([f"{k} = ?" for k in set_values.keys()])
        update_sql = f"UPDATE {table_name} SET {set_clause}"

        if condition:
            update_sql += f" WHERE {condition}"

        params = tuple(set_values.values())
        try:
            self.cursor.execute(update_sql, params)
            self.conn.commit()
            affected_rows = self.cursor.rowcount
            logger.info(f"更新表 '{table_name}' {affected_rows} 行记录")
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"更新数据失败: {e}")
            return 0

    def delete_data(self, table_name: str, condition: str = ""):
        """
        删除数据
        :param table_name: 表名
        :param condition: WHERE条件语句
        """
        delete_sql = f"DELETE FROM {table_name}"
        if condition:
            delete_sql += f" WHERE {condition}"

        try:
            self.cursor.execute(delete_sql)
            self.conn.commit()
            affected_rows = self.cursor.rowcount
            logger.info(f"从表 '{table_name}' 删除 {affected_rows} 行记录")
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"删除数据失败: {e}")
            return 0

    def query_to_dataframe(self, query: str, params: Tuple = ()) -> pd.DataFrame:
        """
        执行查询并返回DataFrame
        :param query: SQL查询语句
        :param params: 查询参数元组
        :return: 包含查询结果的DataFrame
        """
        try:
            return pd.read_sql_query(query, self.conn, params=params)
        except sqlite3.Error as e:
            logger.error(f"查询失败: {e}")
            return pd.DataFrame()

    def table_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        将整个表转换为DataFrame
        :param table_name: 表名
        :return: 包含表数据的DataFrame
        """
        return self.query_to_dataframe(f"SELECT * FROM {table_name}")

    def execute_sql(self, sql: str, params: Tuple = ()):
        """执行任意SQL语句"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            logger.info(f"执行SQL: {sql}")
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"执行SQL失败: {e}")
            return 0

    def close_connection(self):
        """关闭数据库连接"""
        try:
            self.conn.close()
            logger.info("数据库连接已关闭")
        except sqlite3.Error as e:
            logger.error(f"关闭连接失败: {e}")

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close_connection()


# 使用示例
if __name__ == "__main__":
    # 配置loguru日志
    # logger.add("sqlite_operations.log", rotation="10 MB", retention="7 days", level="INFO")

    # 使用上下文管理器自动处理连接
    with SQLiteManager('company.db') as db:
        # 创建表 - 必须传入表名和完整的SQL语句
        employees_table = "employees"

        if db.table_exists(employees_table):
            logger.warning(f"表 {employees_table} 已存在，将删除重建")
            db.drop_table(employees_table)

        create_employees_sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            position TEXT,
            salary REAL,
            hire_date DATE,
            department_id INTEGER,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
        """
        db.create_table(employees_table, create_employees_sql)

        # 创建部门表
        departments_table = "departments"
        create_departments_sql = """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            manager_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        db.create_table(departments_table, create_departments_sql)

        # 插入部门数据
        departments = [
            {'name': '技术部', 'manager_id': 1},
            {'name': '设计部', 'manager_id': 2},
            {'name': '产品部', 'manager_id': 3}
        ]
        for dept in departments:
            db.insert_record(departments_table, dept)

        # 插入员工数据
        employees_df = pd.DataFrame({
            'name': ['张三', '李四', '王五', '赵六'],
            'email': ['zhang@example.com', 'li@example.com', 'wang@example.com', 'zhao@example.com'],
            'position': ['工程师', '设计师', '产品经理', '数据分析师'],
            'salary': [15000.0, 12000.0, 18000.0, 16000.0],
            'hire_date': ['2023-01-15', '2022-05-20', '2021-11-30', '2023-03-10'],
            'department_id': [1, 2, 3, 1]
        })
        db.insert_dataframe(employees_df, employees_table)

        # 创建索引
        db.create_index(employees_table, 'department_id', index_name='idx_employees_department')
        db.create_index(employees_table, ['position', 'salary'], index_name='idx_position_salary')

        # 删除临时表示例
        temp_table = "temp_data"
        if db.table_exists(temp_table):
            logger.warning(f"表 {temp_table} 已存在，将删除重建")
            db.drop_table(temp_table)

        # 创建临时表
        create_temp_sql = """
        CREATE TABLE temp_data (
            id INTEGER PRIMARY KEY,
            data_value TEXT
        )
        """
        db.create_table(temp_table, create_temp_sql)

        # 插入临时数据
        db.insert_record(temp_table, {'data_value': '测试数据'})

        # 查询临时数据
        logger.info("\n临时表数据:")
        print(db.table_to_dataframe(temp_table))

        # 删除临时表
        db.drop_table(temp_table)

        # 复杂查询示例
        logger.info("\n高薪员工信息:")
        high_salary_query = """
        SELECT 
            e.name AS employee_name, 
            e.position, 
            e.salary,
            d.name AS department_name
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE e.salary > 15000
        ORDER BY e.salary DESC
        """
        high_salary_employees = db.query_to_dataframe(high_salary_query)
        print(high_salary_employees)

        # 更新数据
        db.update_data(
            employees_table,
            {'salary': 17000.0},
            "name = '张三'"
        )

        # 删除数据
        db.delete_data(
            departments_table,
            "name = '设计部'"
        )

        # 最终数据
        logger.info("\n最终员工数据:")
        print(db.table_to_dataframe(employees_table))

        logger.info("\n最终部门数据:")
        print(db.table_to_dataframe(departments_table))