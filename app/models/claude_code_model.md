# ORM 代码风格与生成规范（MySQL 专用）

目标
- 输入：MySQL CREATE TABLE 语句
- 输出：SQLAlchemy 2.x ORM 模型（Declarative + Annotated Mapped）
- 方言：MySQL 8.x
- 重点要求：优先使用数据库侧自动时间戳；func.now() 并附加 pylint 注释

生成规则（必须遵守）
1) 基本结构
- 使用 SQLAlchemy 2.x 注解写法：
  - from sqlalchemy.orm import Mapped, mapped_column
  - 类型从 sqlalchemy 导入：BigInteger, Integer, SmallInteger, String, Date, DateTime, ForeignKey, Index, UniqueConstraint, func
  - DECIMAL 使用 sqlalchemy.types.DECIMAL 或 Numeric
- 类名：表名转为 PascalCase（下划线分词首字母大写），如 advisor_call_duration_stats -> AdvisorCallDurationStats
- __tablename__ 与 SQL 表名一致
- 继承 Base（假定用户项目里已有 Base），不要在此文件中定义 Base

2) 字段映射与类型
- 常用类型映射：
  - BIGINT -> BigInteger
  - INT/INTEGER -> Integer
  - SMALLINT -> SmallInteger
  - VARCHAR(n) -> String(n)
  - DECIMAL(p,s) -> DECIMAL(p, s) 或 Numeric(p, s)
  - DATE -> Date
  - DATETIME/TIMESTAMP -> DateTime(timezone=True)
- 非空：NOT NULL -> nullable=False；省略 NOT NULL -> 默认 nullable=True
- 默认值：
  - DEFAULT 0/0.00 等常量 -> server_default="0"/"0.00"（注意是字符串）
  - DEFAULT CURRENT_TIMESTAMP -> server_default=func.now()  # pylint: disable=not-callable
  - ON UPDATE CURRENT_TIMESTAMP -> server_onupdate=func.now()  # pylint: disable=not-callable
- 主键：
  - id 主键列 -> mapped_column(BigInteger, primary_key=True)
  - 若 SQL 中包含 AUTO_INCREMENT，仅在注释中保持含义，不额外添加 ORM 端 autoincrement 显式参数，除非必要

3) 时间戳字段（强制规范）
- created_at 字段：
  - DateTime(timezone=True),
  - server_default=func.now()，并在该行末尾添加注释：# pylint: disable=not-callable
- updated_at 字段：
  - DateTime(timezone=True),
  - server_default=func.now(), server_onupdate=func.now()，并在该行末尾添加注释：# pylint: disable=not-callable
- 统一按 UTC 语义处理；注释中可标注“UTC”

4) 注释与命名
- 列注释：SQL COMMENT 转为 comment="..."
- 表注释：可保留在类级注释（docstring）中，或忽略不生成额外代码
- 命名约定：
  - 索引命名：idx_xxx
  - 唯一键命名：uk_xxx
  - 外键命名（如存在）：fk_from_to（建议）
- 类字段名与列名保持与 SQL 一致（snake_case）

5) 约束与索引
- UNIQUE KEY uk_xxx(col1, col2) -> UniqueConstraint("col1", "col2", name="uk_xxx")
- KEY idx_xxx(col) -> Index("idx_xxx", "col")
- 外键（若 SQL 有 FOREIGN KEY）：
  - ForeignKey("ref_table.id", onupdate="CASCADE", ondelete="RESTRICT") 按 SQL 定义映射
  - 为外键列创建索引（若 SQL 原本已建则按原样输出）

6) 其余细节
- 金额/百分比使用 DECIMAL 指定精度，必须保留 server_default 文字字面值（如 "0.00"）
- 计数/时长（秒）使用 BigInteger，默认 "0"
- 明确 nullable、server_default、comment，避免省略
- 不生成 relationship，除非 SQL 中存在明确的外键关系并且有必要
- 不引入应用侧 now() 或 Python 端默认时间，严格使用数据库侧自动时间戳
- 保持字段定义顺序与 SQL 中一致

7) 输出格式
- 仅输出 Python 代码块（单个类），并保证可直接粘贴使用
- 代码顶部导入需最小化、完整可运行
- 不输出多余解释性文字

示例输入（片段）
CREATE TABLE advisor_call_duration_stats (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
  advisor_id SMALLINT NOT NULL COMMENT '顾问ID',
  stats_date DATE NOT NULL COMMENT '统计日期',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY uk_advisor_date (advisor_id, stats_date),
  KEY idx_advisor_id (advisor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问通话时长统计表';

示例输出（必须贴合以上规范）
```python
from datetime import datetime
from sqlalchemy import BigInteger, SmallInteger, String, Date, DateTime, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from app.db.database import Base


class AdvisorCallDurationStats(Base):
    __tablename__ = "advisor_call_duration_stats"
    """顾问通话时长统计表"""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    advisor_id: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="顾问ID")
    stats_date: Mapped[datetime] = mapped_column(Date, nullable=False, comment="统计日期")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间(UTC)"
    )  # pylint: disable=not-callable

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        comment="更新时间(UTC)"
    )  # pylint: disable=not-callable

    __table_args__ = (
        UniqueConstraint("advisor_id", "stats_date", name="uk_advisor_date"),
        Index("idx_advisor_id", "advisor_id"),
    )
```

质量校验清单（生成时自检）
- 时间戳是否使用 server_default/server_onupdate=func.now() 且带 # pylint: disable=not-callable
- 每列是否有明确的 nullable、server_default（如 SQL 有默认）与 comment
- DECIMAL 是否保留精度与文字 server_default（如 "0.00"）
- 约束/索引是否完整映射，命名是否一致
- 字段顺序与 SQL 是否一致

--- 文件结束 ---

用法建议
- 在与 Claude/其他模型对话时，先贴上该 md 文件；随后粘贴你的 SQL。它将按此规范直接输出 ORM 类代码。
- 如你的项目 Base 路径不同，修改 from app.db.database import Base 为你的实际导入路径即可。