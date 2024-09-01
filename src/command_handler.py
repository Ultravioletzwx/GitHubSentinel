# src/command_handler.py

import argparse

class CommandHandler:
    def __init__(self, github_client, subscription_manager, report_generator):
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator
        self.parser = self.create_parser()

    def create_parser(self):
        # 创建解析器对象
        parser = argparse.ArgumentParser(
            description='GitHub Sentinel Command Line Interface',
            formatter_class=argparse.RawTextHelpFormatter
        )
        # 添加子命令解析器
        subparsers = parser.add_subparsers(title='Commands', dest='command')
        # 添加 add 子命令解析器
        parser_add = subparsers.add_parser('add', help='Add a subscription')
        # 添加 add 子命令的参数
        parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
        # 设置 add 子命令的默认执行函数
        parser_add.set_defaults(func=self.add_subscription)
        # 添加 remove 子命令解析器
        parser_remove = subparsers.add_parser('remove', help='Remove a subscription')
        # 添加 remove 子命令的参数
        parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
        # 设置 remove 子命令的默认执行函数
        parser_remove.set_defaults(func=self.remove_subscription)
        # 添加 list 子命令解析器
        parser_list = subparsers.add_parser('list', help='List all subscriptions')
        # 设置 list 子命令的默认执行函数
        parser_list.set_defaults(func=self.list_subscriptions)
        # 添加 fetch 子命令解析器
        parser_fetch = subparsers.add_parser('fetch', help='Fetch updates immediately')
        # 添加 fetch 子命令的参数
        parser_fetch.add_argument('repo', type=str, help='The repository to fetch updates from (e.g., owner/repo)')
        # 设置 fetch 子命令的默认执行函数
        parser_fetch.set_defaults(func=self.fetch_updates)
        # 添加 export 子命令解析器
        parser_export = subparsers.add_parser('export', help='Export daily progress')
        # 添加 export 子命令的参数
        parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        # 设置 export 子命令的默认执行函数
        parser_export.set_defaults(func=self.export_daily_progress)
        # 添加 generate 子命令解析器
        parser_generate = subparsers.add_parser('generate', help='Generate daily report from markdown file')
        # 添加 generate 子命令的参数
        parser_generate.add_argument('file', type=str, help='The markdown file to generate report from')
        # 设置 generate 子命令的默认执行函数
        parser_generate.set_defaults(func=self.generate_daily_report)
        # 添加 help 子命令解析器
        parser_help = subparsers.add_parser('help', help='Show help message')
        # 设置 help 子命令的默认执行函数
        parser_help.set_defaults(func=self.print_help)
        return parser


    def add_subscription(self, args):
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription for repository: {args.repo}")

    def remove_subscription(self, args):
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription for repository: {args.repo}")

    def list_subscriptions(self, args):
        subscriptions = self.subscription_manager.list_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"  - {sub}")

    def fetch_updates(self, args):
        updates = self.github_client.fetch_updates(args.repo)
        for update in updates:
            print(update)

    # 从github上到处issue 和 pull_request 到md文件中
    def export_daily_progress(self, args):
        self.github_client.export_daily_progress(args.repo)
        print(f"Exported daily progress for repository: {args.repo}")

    def generate_daily_report(self, args):
        self.report_generator.generate_daily_report(args.file)
        print(f"Generated daily report from file: {args.file}")

    def print_help(self, args=None):
        self.parser.print_help()
