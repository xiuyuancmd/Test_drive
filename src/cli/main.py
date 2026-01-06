#!/usr/bin/env python3
"""
LLM Excel Processor - 命令行工具
"""
import os
import sys
import click
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.app import ConfigManager, TaskManager
from src.core.llm import PromptTemplate


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """LLM Excel Processor - 基于大语言模型的Excel文档处理工具"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='输入文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--config', '-c', help='配置文件路径')
@click.option('--provider', default='openai', help='LLM提供商 (openai, claude等)')
@click.option('--model', default='gpt-3.5-turbo', help='模型名称')
@click.option('--prompt', help='提示词模板')
@click.option('--mode', default='row', type=click.Choice(['row', 'batch', 'stream']), help='处理模式')
@click.option('--batch-size', default=10, help='批处理大小')
@click.option('--api-key', help='API密钥（也可通过环境变量设置）')
def process(input, output, config, provider, model, prompt, mode, batch_size, api_key):
    """
    处理文件

    示例:
    \b
    llm-excel-processor process -i data.xlsx -o result.xlsx --prompt "分析: {text}"
    llm-excel-processor process -i data.xlsx -o result.xlsx -c config.yaml
    """
    try:
        # 如果提供了配置文件，使用配置文件
        if config:
            if not os.path.exists(config):
                click.echo(f"❌ 配置文件不存在: {config}", err=True)
                sys.exit(1)

            click.echo(f"📋 加载配置文件: {config}")
            config_manager = ConfigManager()
            config_manager.load_from_file(config)

        else:
            # 创建默认配置
            click.echo("📋 使用命令行参数创建配置")

            if not prompt:
                click.echo("❌ 请提供提示词模板 (--prompt) 或配置文件 (--config)", err=True)
                sys.exit(1)

            # 获取API密钥
            if not api_key:
                api_key = os.getenv(f"{provider.upper()}_API_KEY")
                if not api_key:
                    click.echo(f"❌ 请设置API密钥 (--api-key 或环境变量 {provider.upper()}_API_KEY)", err=True)
                    sys.exit(1)

            config_dict = {
                'task': {
                    'name': f'Process {os.path.basename(input)}',
                    'description': 'CLI任务'
                },
                'input': {
                    'file': input
                },
                'processing': {
                    'mode': mode,
                    'batch_size': batch_size
                },
                'llm': {
                    'provider': provider,
                    'model': model,
                    'api_key': api_key,
                    'prompt_template': prompt,
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                'output': {
                    'file': output,
                    'format': os.path.splitext(output)[1].lstrip('.')
                },
                'retry': {
                    'enabled': True,
                    'max_attempts': 3
                }
            }

            config_manager = ConfigManager()
            config_manager.load_from_dict(config_dict)

        # 执行任务
        click.echo("\n" + "="*50)
        click.echo("🚀 开始执行任务")
        click.echo("="*50 + "\n")

        task_manager = TaskManager(config_manager)
        result = task_manager.execute()

        # 显示结果摘要
        click.echo("\n" + "="*50)
        click.echo("✅ 任务执行完成")
        click.echo("="*50)
        click.echo(f"\n任务ID: {result['task_id']}")
        click.echo(f"总行数: {result['total_rows']}")
        click.echo(f"成功: {result['success_count']}")
        click.echo(f"失败: {result['failed_count']}")
        click.echo(f"Token使用: {result['total_tokens']}")
        click.echo(f"预估成本: ${result['estimated_cost']:.4f}")
        click.echo(f"用时: {result['elapsed_time']:.1f}秒")
        click.echo(f"输出文件: {result['output_file']}\n")

    except Exception as e:
        click.echo(f"\n❌ 执行失败: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='config.yaml', help='输出配置文件路径')
def init_config(output):
    """
    创建默认配置文件

    示例:
    \b
    llm-excel-processor init-config
    llm-excel-processor init-config -o my_config.yaml
    """
    try:
        config_manager = ConfigManager()
        default_config = ConfigManager.create_default_config()
        config_manager.load_from_dict(default_config)
        config_manager.save_to_file(output)

        click.echo(f"✅ 配置文件已创建: {output}")
        click.echo("\n请编辑配置文件，然后使用以下命令处理文件:")
        click.echo(f"  llm-excel-processor process -c {output}")

    except Exception as e:
        click.echo(f"❌ 创建配置文件失败: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_providers():
    """列出支持的LLM提供商"""
    from src.core.llm import LLMProviderFactory

    providers = LLMProviderFactory.get_supported_providers()

    click.echo("支持的LLM提供商:\n")
    for provider in providers:
        click.echo(f"  • {provider}")

    click.echo("\n使用示例:")
    click.echo("  llm-excel-processor process -i data.xlsx -o result.xlsx --provider openai --model gpt-4")


@cli.command()
def list_formats():
    """列出支持的文件格式"""
    from src.core.parsers import ParserFactory
    from src.core.output import OutputWriterFactory

    input_formats = ParserFactory.get_supported_formats()
    output_formats = OutputWriterFactory.get_supported_formats()

    click.echo("支持的输入格式:\n")
    for fmt in input_formats:
        click.echo(f"  • {fmt}")

    click.echo("\n支持的输出格式:\n")
    for fmt in output_formats:
        click.echo(f"  • {fmt}")


@cli.command()
@click.argument('config_file')
def validate_config(config_file):
    """
    验证配置文件

    示例:
    \b
    llm-excel-processor validate-config config.yaml
    """
    try:
        if not os.path.exists(config_file):
            click.echo(f"❌ 配置文件不存在: {config_file}", err=True)
            sys.exit(1)

        click.echo(f"🔍 验证配置文件: {config_file}")

        config_manager = ConfigManager()
        config_manager.load_from_file(config_file)

        click.echo("✅ 配置文件有效\n")
        click.echo(f"任务名称: {config_manager.task_config.name}")
        click.echo(f"输入文件: {config_manager.input_config.file}")
        click.echo(f"输出文件: {config_manager.output_config.file}")
        click.echo(f"处理模式: {config_manager.processing_config.mode}")
        click.echo(f"LLM提供商: {config_manager.llm_config.provider}")
        click.echo(f"模型: {config_manager.llm_config.model}")

    except Exception as e:
        click.echo(f"❌ 配置文件无效: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
