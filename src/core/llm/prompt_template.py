"""
提示词模板系统
支持动态变量替换和few-shot示例
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re
import json


@dataclass
class FewShotExample:
    """Few-shot示例"""
    input: Dict[str, Any]
    output: str


@dataclass
class PromptTemplate:
    """提示词模板"""
    template: str                                   # 模板字符串
    system_prompt: Optional[str] = None            # 系统提示词
    variables: List[str] = field(default_factory=list)  # 变量列表
    few_shot_examples: List[FewShotExample] = field(default_factory=list)  # Few-shot示例
    output_format: Optional[str] = None            # 期望的输出格式
    description: Optional[str] = None              # 模板描述

    def __post_init__(self):
        """初始化后自动提取变量"""
        if not self.variables:
            self.variables = self._extract_variables()

    def _extract_variables(self) -> List[str]:
        """从模板中提取变量名"""
        # 匹配 {variable_name} 格式的变量
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.template)
        return list(set(variables))  # 去重

    def render(self, data: Dict[str, Any], include_examples: bool = True) -> str:
        """
        渲染提示词

        Args:
            data: 数据字典，包含变量的值
            include_examples: 是否包含few-shot示例

        Returns:
            str: 渲染后的提示词

        Raises:
            ValueError: 缺少必需的变量
        """
        # 检查所有变量是否都提供了
        missing_vars = set(self.variables) - set(data.keys())
        if missing_vars:
            raise ValueError(f"缺少必需的变量: {missing_vars}")

        # 构建完整提示词
        parts = []

        # 添加输出格式说明
        if self.output_format:
            parts.append(f"请按照以下格式返回结果: {self.output_format}\n")

        # 添加few-shot示例
        if include_examples and self.few_shot_examples:
            parts.append("以下是一些示例:\n")
            for i, example in enumerate(self.few_shot_examples, 1):
                parts.append(f"\n示例 {i}:")
                parts.append(f"输入: {json.dumps(example.input, ensure_ascii=False)}")
                parts.append(f"输出: {example.output}\n")
            parts.append("\n现在请处理以下数据:\n")

        # 渲染模板
        rendered = self.template.format(**data)
        parts.append(rendered)

        return "\n".join(parts)

    def render_batch(
        self,
        data_list: List[Dict[str, Any]],
        include_examples: bool = True
    ) -> str:
        """
        批量渲染提示词（将多行数据放在一个提示词中）

        Args:
            data_list: 数据字典列表
            include_examples: 是否包含few-shot示例

        Returns:
            str: 渲染后的提示词
        """
        parts = []

        # 添加说明
        parts.append(f"请处理以下 {len(data_list)} 条数据:\n")

        # 添加输出格式说明
        if self.output_format:
            parts.append(f"对于每条数据，请按照以下格式返回结果: {self.output_format}\n")

        # 添加few-shot示例
        if include_examples and self.few_shot_examples:
            parts.append("示例格式:")
            example = self.few_shot_examples[0]
            parts.append(f"输入: {json.dumps(example.input, ensure_ascii=False)}")
            parts.append(f"输出: {example.output}\n")

        # 渲染每条数据
        for i, data in enumerate(data_list, 1):
            parts.append(f"\n--- 数据 {i} ---")
            rendered = self.template.format(**data)
            parts.append(rendered)

        return "\n".join(parts)

    def add_example(self, input_data: Dict[str, Any], output: str):
        """
        添加few-shot示例

        Args:
            input_data: 输入数据
            output: 期望的输出
        """
        self.few_shot_examples.append(FewShotExample(input=input_data, output=output))

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否包含所有必需的变量

        Args:
            data: 数据字典

        Returns:
            bool: 数据是否有效
        """
        return all(var in data for var in self.variables)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'template': self.template,
            'system_prompt': self.system_prompt,
            'variables': self.variables,
            'few_shot_examples': [
                {'input': ex.input, 'output': ex.output}
                for ex in self.few_shot_examples
            ],
            'output_format': self.output_format,
            'description': self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """从字典创建"""
        examples = [
            FewShotExample(input=ex['input'], output=ex['output'])
            for ex in data.get('few_shot_examples', [])
        ]

        return cls(
            template=data['template'],
            system_prompt=data.get('system_prompt'),
            variables=data.get('variables', []),
            few_shot_examples=examples,
            output_format=data.get('output_format'),
            description=data.get('description'),
        )


class PromptTemplateLibrary:
    """提示词模板库"""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}

    def add(self, name: str, template: PromptTemplate):
        """添加模板"""
        self._templates[name] = template

    def get(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self._templates.get(name)

    def list(self) -> List[str]:
        """列出所有模板名称"""
        return list(self._templates.keys())

    def load_from_file(self, file_path: str):
        """从文件加载模板"""
        import yaml

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        template = PromptTemplate.from_dict(data)
        name = data.get('name', 'unnamed')
        self.add(name, template)

    def save_to_file(self, name: str, file_path: str):
        """保存模板到文件"""
        import yaml

        template = self.get(name)
        if not template:
            raise ValueError(f"模板不存在: {name}")

        data = template.to_dict()
        data['name'] = name

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
