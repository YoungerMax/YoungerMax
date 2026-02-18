from dataclasses import dataclass
from datetime import datetime
from typing import List
import requests
import bs4
import dateutil


EMOJI_MAPPING = {'A': '💿', 'B': '🏁', 'C': '🔑', 'D': '💻', 'E': '🤖', 'F': '🗜', 'G': '📅', 'H': '📂', 'I': '📏', 'J': '🧪', 'K': '🔨', 'L': '📤', 'M': '📦', 'N': '🗂', 'O': '🗃', 'P': '📊', 'Q': '📚', 'R': '🗄', 'S': '🧠', 'T': '📝', 'U': '🔌', 'V': '🛰', 'W': '🎮', 'X': '📉', 'Y': '🧯', 'Z': '🚨', 'a': '📈', 'b': '📥', 'c': '📡', 'd': '🔁', 'e': '🧩', 'f': '🔓', 'g': '💾', 'h': '📋', 'i': '👾', 'j': '🌐', 'k': '🧬', 'l': '🔬', 'm': '📎', 'n': '🔧', 'o': '🔋', 'p': '🚀', 'q': '🔄', 'r': '📀', 's': '📁', 't': '🔍', 'u': '📌', 'v': '⚡', 'w': '⚙', 'x': '⏳', 'y': '🧮', 'z': '🔒'}

@dataclass(frozen=True)
class Post:
    title: str
    link: str
    description: str
    pubDate: datetime
    content: str

@dataclass(frozen=True)
class Repo:
    name: str
    description: str

def try_select_one(tag: bs4.Tag, selector: str) -> str:
    element = tag.find(selector)

    if not element:
        raise ValueError(f"{selector} not found")
    
    return element.text.strip()


def get_posts() -> List[Post]:
    rss_url = 'https://lincolnmaxwell.com/rss.xml'
    response = requests.get(rss_url)
    soup = bs4.BeautifulSoup(response.text, 'xml')
    posts: List[Post] = []

    for item in soup.select('item'):
        title = try_select_one(item, 'title')
        link = try_select_one(item, 'link')
        description = try_select_one(item, 'description')
        content = try_select_one(item, 'content:encoded')
        pubDate = dateutil.parser.parse(try_select_one(item, 'pubDate'))

        posts.append(Post(title, link, description, pubDate, content))
    
    posts.sort(key=lambda x: x.pubDate, reverse=True)

    return posts

def format_recent_blog_posts(posts: List[Post]) -> str:
    """Posts are sorted from newest to oldest."""
    lines = []

    for post in posts:
        emoji = EMOJI_MAPPING.get(post.title[0], '🧑')
        formatted_date = post.pubDate.strftime('%b %-d, %Y')

        lines.append(f"- {emoji} [**{post.title}**]({post.link}) - {post.description}")

    return '\n'.join(lines)

def format_about_me(posts: List[Post]) -> str:
    for post in posts:
        if post.link == 'https://lincolnmaxwell.com/p/about-me/':
            return post.content
    
    raise LookupError('about me post not found')

posts = get_posts()

with open('README.template.md', 'rt') as template_reader:
    template = template_reader.read()

    output = template.format_map({
        'latest_blog_posts': format_recent_blog_posts(posts),
        'about_me': format_about_me(posts)
    })

    print(output)