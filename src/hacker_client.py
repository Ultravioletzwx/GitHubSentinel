import requests
import os
from datetime import date
from logger import LOG


class HackerNewsClient:
    def __init__(self):
        self.base_url = 'https://hacker-news.firebaseio.com/v0'

    def fetch_latest_stories(self, count=30):
        LOG.debug("开始获取最新的新闻文章")
        try:
            response = requests.get(f'{self.base_url}/newstories.json')
            response.raise_for_status()
            story_ids = response.json()
            LOG.debug(f"获取到 {len(story_ids)} 个新闻文章ID")

            stories = []
            for story_id in story_ids[:count]:
                story_url = f'{self.base_url}/item/{story_id}.json'
                story_response = requests.get(story_url)
                story_response.raise_for_status()
                story_info = story_response.json()
                stories.append({
                    'title': story_info.get('title'),
                    'url': story_info.get('url', 'No URL')
                })
            LOG.info("成功获取最新的新闻文章")
            return stories
        except Exception as e:
            LOG.error(f"获取新闻文章失败：{str(e)}")
            return []

    def export_to_markdown(self, stories):
        today = date.today().isoformat()
        directory = os.path.join('daily_progress', f'hacker_news')
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f'{today}_hacker_news_stories.md')

        LOG.debug(f"开始将新闻文章写入Markdown文件：{filename}")
        try:
            with open(filename, 'w') as file:
                file.write(f'# Hacker News Latest Stories ({today})\n\n')
                for story in stories:
                    file.write(f"- [{story['title']}]({story['url']})\n")
            LOG.info(f"Markdown文件已生成：{filename}")
            return filename
        except Exception as e:
            LOG.error(f"写入Markdown文件失败：{str(e)}")
            return None

if __name__ == '__main__':
    # 使用示例
    client = HackerNewsClient()
    stories = client.fetch_latest_stories()
    client.export_to_markdown(stories)