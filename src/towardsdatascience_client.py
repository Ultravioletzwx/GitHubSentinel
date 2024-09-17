from logger import LOG  # 导入日志模块
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

class TowardsDataScienceClient:
    def __init__(self,proxy_address=None):
        LOG.info("初始化TowardsDataScienceClient")
        self.driver_path = os.getenv('Edge_driver')
        self.proxy_address = proxy_address
        self.driver = None

    def setup_driver(self):
        LOG.info("设置Edge WebDriver")
        edge_options = Options()
        edge_options.add_argument("--headless")  # 在无头模式下运行
        edge_options.add_argument("--disable-gpu")

        if self.proxy_address:
            LOG.info(f"设置代理服务器: {self.proxy_address}")
            edge_options.add_argument(f'--proxy-server={self.proxy_address}')

        service = Service(self.driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)
        return driver

    def _fetch_full_page_content(self, url, target_count=30, max_scroll_attempts=10):
        LOG.info(f"获取页面内容: {url}")
        self.driver.get(url)
        article_set = set()

        # 模拟滚动加载页面
        for _ in range(max_scroll_attempts):
            if len(article_set) >= target_count:
                LOG.info(f"达到了所需的文章数量: {target_count}")
                break

            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(3)

            new_articles = set(a.get_attribute('href') for a in
                               self.driver.find_elements(By.CSS_SELECTOR, 'a[data-action="open-post"]'))
            new_page_loaded = bool(new_articles - article_set)
            article_set.update(new_articles)

            # if not new_page_loaded:
            #     LOG.warning("没有新的页面加载")
            #     break

        return self.driver.page_source

    def _parse_articles(self, html_content, min_count=30):
        LOG.info("解析文章内容")
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []

        article_containers = soup.find_all('div', class_='postArticle')
        for container in article_containers:
            if len(articles) >= min_count:
                break

            link_tag = container.find('a', {'data-action': 'open-post'})
            if link_tag:
                full_link = link_tag['href']
                h3_tag = link_tag.find_next('h3')
                h4_tag = link_tag.find_next('h4')

                title = h3_tag.get_text(strip=True) if h3_tag else "No Title"
                description = h4_tag.get_text(strip=True) if h4_tag else "No Description"

                articles.append({
                    'title': title,
                    'description': description,
                    'link': full_link
                })

        LOG.info(f"解析到了{len(articles)}篇文章")
        return articles

    def get_articles(self, section_name, min_count=30):
        LOG.info(f"获取{section_name}文章")
        url = f'https://towardsdatascience.com/{section_name}'
        page_content = self._fetch_full_page_content(url)
        return self._parse_articles(page_content, min_count)

    def export_to_markdown(self, articles, section_name):
        LOG.info(f"导出{section_name}文章到Markdown文件")
        date = datetime.now().strftime('%Y-%m-%d')
        dir_path = os.path.join('towards_data_science', date)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f'{section_name}.md')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Towards Data Science {section_name.capitalize()} Articles - {date}\n\n")
            for idx, article in enumerate(articles, start=1):
                file.write(
                    f"{idx}. **{article['title']}**\n    - [{article['description']}]({article['link']})\n")

        LOG.info(f"{section_name.capitalize()}文章已导出至：{file_path}")
        return file_path

    def close(self):
        LOG.info("关闭浏览器")
        self.driver.quit()


if __name__ == "__main__":
    proxy_address = 'http://127.0.0.1:7890'

    client = TowardsDataScienceClient(proxy_address=proxy_address)

    try:
        latest_articles = client.get_articles('latest', min_count=30)
        client.export_to_markdown(latest_articles, 'latest')

        trending_articles = client.get_articles('trending', min_count=30)
        client.export_to_markdown(trending_articles, 'trending')

    finally:
        client.close()