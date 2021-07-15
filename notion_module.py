from notion.client import NotionClient
from notion.block import SubsubheaderBlock, TextBlock
from notion.collection import CollectionRowBlock
from settings import main_page_url
from os import environ
from dotenv import load_dotenv


class NotionHandler:
    def __init__(self):
        load_dotenv('.env')
        self.token_v2 = environ["token_v2"]

    def get_tasks(self) -> list[CollectionRowBlock]:
        client = NotionClient(self.token_v2)
        main_page = client.get_block(main_page_url)
        tasks = main_page.collection.get_rows()
        return tasks

    @staticmethod
    def get_msg(task: CollectionRowBlock) -> str:
        msg = task.title + "\n"
        for item in task.children:
            try:
                if isinstance(item, SubsubheaderBlock):
                    msg += "# " + item.title + "\n"
                if isinstance(item, TextBlock):
                    msg += "- " + item.title + "\n"
            except Exception as e:
                pass
        return msg


if __name__ == "__main__":
    nh = NotionHandler()
    for task in nh.get_tasks():
        print(nh.get_msg(task))
