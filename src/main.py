import argparse
from config import Config
from scheduler import Scheduler
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from subscription_manager import SubscriptionManager
import threading
import shlex

def run_scheduler(scheduler):
    scheduler.start()

def add_subscription(args, subscription_manager):
    subscription_manager.add_subscription(args.repo)
    print(f"Added subscription: {args.repo}")

def remove_subscription(args, subscription_manager):
    subscription_manager.remove_subscription(args.repo)
    print(f"Removed subscription: {args.repo}")

def list_subscriptions(subscription_manager):
    subscriptions = subscription_manager.get_subscriptions()
    print("Current subscriptions:")
    for sub in subscriptions:
        print(f"- {sub}")

def fetch_updates(github_client, subscription_manager, report_generator):
    subscriptions = subscription_manager.get_subscriptions()
    updates = github_client.fetch_updates(subscriptions)
    report = report_generator.generate(updates)
    print("Updates fetched:")
    print(report)

def print_help():
    help_text = """
GitHub Sentinel Command Line Interface

Available commands:
  add <repo>       Add a subscription (e.g., owner/repo)
  remove <repo>    Remove a subscription (e.g., owner/repo)
  list             List all subscriptions
  fetch            Fetch updates immediately
  help             Show this help message
  exit             Exit the tool
  quit             Exit the tool
"""
    print(help_text)

def main():
    # 初始化配置对象
    config = Config()
    # 初始化GitHub客户端对象
    github_client = GitHubClient(config.github_token)
    # 初始化通知器对象
    notifier = Notifier(config.notification_settings)
    # 初始化报告生成器对象
    report_generator = ReportGenerator()
    # 初始化订阅管理器对象
    subscription_manager = SubscriptionManager(config.subscriptions_file)

    # 初始化调度器对象
    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval
    )

    # 创建并启动调度器线程
    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='GitHub Sentinel Command Line Interface')
    # 添加子解析器
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # 添加添加订阅的解析器
    parser_add = subparsers.add_parser('add', help='Add a subscription')
    parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
    # 设置添加订阅的回调函数
    parser_add.set_defaults(func=lambda args: add_subscription(args, subscription_manager))

    # 添加删除订阅的解析器
    parser_remove = subparsers.add_parser('remove', help='Remove a subscription')
    parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
    # 设置删除订阅的回调函数
    parser_remove.set_defaults(func=lambda args: remove_subscription(args, subscription_manager))

    # 添加列出所有订阅的解析器
    parser_list = subparsers.add_parser('list', help='List all subscriptions')
    # 设置列出所有订阅的回调函数
    parser_list.set_defaults(func=lambda args: list_subscriptions(subscription_manager))

    # 添加立即获取更新的解析器
    parser_fetch = subparsers.add_parser('fetch', help='Fetch updates immediately')
    # 设置立即获取更新的回调函数
    parser_fetch.set_defaults(func=lambda args: fetch_updates(github_client, subscription_manager, report_generator))

    # 添加显示帮助信息的解析器
    parser_help = subparsers.add_parser('help', help='Show this help message')
    # 设置显示帮助信息的回调函数
    parser_help.set_defaults(func=lambda args: print_help())

    # 程序启动时打印帮助信息
    # 打印帮助信息
    print_help()

    while True:
        try:
            # 获取用户输入
            user_input = input("GitHub Sentinel> ")
            # 如果用户输入为exit或quit，则退出程序
            if user_input in ["exit", "quit"]:
                print("Exiting GitHub Sentinel...")
                break
            # 解析用户输入的命令行参数
            args = parser.parse_args(shlex.split(user_input))
            # 如果用户输入了有效的命令，则执行相应的回调函数
            if args.command is not None:
                args.func(args)
            else:
                # 如果用户输入了无效的命令，则打印帮助信息
                parser.print_help()
        except Exception as e:
            # 如果程序出现异常，则打印异常信息
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
