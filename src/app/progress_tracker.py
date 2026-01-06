"""
进度追踪器
追踪任务执行进度和统计信息
"""
from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskProgress:
    """任务进度"""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    current: int = 0
    total: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100

    @property
    def elapsed_time(self) -> Optional[float]:
        """已用时间（秒）"""
        if not self.start_time:
            return None

        end = self.end_time or datetime.now()
        delta = end - self.start_time
        return delta.total_seconds()

    @property
    def estimated_remaining_time(self) -> Optional[float]:
        """预计剩余时间（秒）"""
        if not self.start_time or self.current == 0:
            return None

        elapsed = self.elapsed_time
        if elapsed is None:
            return None

        avg_time_per_item = elapsed / self.current
        remaining_items = self.total - self.current
        return avg_time_per_item * remaining_items

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'current': self.current,
            'total': self.total,
            'progress_percentage': self.progress_percentage,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'total_tokens': self.total_tokens,
            'estimated_cost': self.estimated_cost,
            'elapsed_time': self.elapsed_time,
            'estimated_remaining_time': self.estimated_remaining_time,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'metadata': self.metadata,
        }


class ProgressTracker:
    """进度追踪器"""

    def __init__(
        self,
        task_id: str,
        total: int,
        callback: Optional[Callable[[TaskProgress], None]] = None
    ):
        """
        初始化进度追踪器

        Args:
            task_id: 任务ID
            total: 总数量
            callback: 进度更新回调函数
        """
        self.progress = TaskProgress(task_id=task_id, total=total)
        self.callback = callback

    def start(self):
        """开始任务"""
        self.progress.status = TaskStatus.RUNNING
        self.progress.start_time = datetime.now()
        self._notify()

    def update(
        self,
        current: int,
        success: bool = True,
        tokens: int = 0,
        error: Optional[str] = None
    ):
        """
        更新进度

        Args:
            current: 当前进度
            success: 是否成功
            tokens: 使用的token数
            error: 错误信息
        """
        self.progress.current = current

        if success:
            self.progress.success_count += 1
        else:
            self.progress.failed_count += 1

        self.progress.total_tokens += tokens

        if error:
            self.progress.error_message = error

        # 估算成本（基于OpenAI GPT-4定价）
        # 输入: $0.03/1K tokens, 输出: $0.06/1K tokens
        # 这里简化为平均 $0.045/1K tokens
        self.progress.estimated_cost = (self.progress.total_tokens / 1000) * 0.045

        self._notify()

    def increment(self, success: bool = True, tokens: int = 0):
        """
        增量更新

        Args:
            success: 是否成功
            tokens: 使用的token数
        """
        self.update(
            current=self.progress.current + 1,
            success=success,
            tokens=tokens
        )

    def complete(self):
        """完成任务"""
        self.progress.status = TaskStatus.COMPLETED
        self.progress.end_time = datetime.now()
        self._notify()

    def fail(self, error_message: str):
        """任务失败"""
        self.progress.status = TaskStatus.FAILED
        self.progress.error_message = error_message
        self.progress.end_time = datetime.now()
        self._notify()

    def cancel(self):
        """取消任务"""
        self.progress.status = TaskStatus.CANCELLED
        self.progress.end_time = datetime.now()
        self._notify()

    def set_metadata(self, key: str, value):
        """设置元数据"""
        self.progress.metadata[key] = value
        self._notify()

    def _notify(self):
        """通知回调"""
        if self.callback:
            self.callback(self.progress)

    def get_summary(self) -> str:
        """获取进度摘要"""
        lines = [
            f"任务ID: {self.progress.task_id}",
            f"状态: {self.progress.status.value}",
            f"进度: {self.progress.current}/{self.progress.total} ({self.progress.progress_percentage:.1f}%)",
            f"成功: {self.progress.success_count}, 失败: {self.progress.failed_count}",
            f"Token使用: {self.progress.total_tokens}",
            f"预估成本: ${self.progress.estimated_cost:.4f}",
        ]

        if self.progress.elapsed_time:
            lines.append(f"已用时间: {self.progress.elapsed_time:.1f}秒")

        if self.progress.estimated_remaining_time:
            lines.append(f"预计剩余: {self.progress.estimated_remaining_time:.1f}秒")

        if self.progress.error_message:
            lines.append(f"错误: {self.progress.error_message}")

        return "\n".join(lines)

    def print_progress_bar(self, width: int = 50):
        """
        打印进度条

        Args:
            width: 进度条宽度
        """
        percentage = self.progress.progress_percentage
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)

        print(f"\r进度: |{bar}| {percentage:.1f}% ({self.progress.current}/{self.progress.total})", end='', flush=True)

        if self.progress.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            print()  # 换行
