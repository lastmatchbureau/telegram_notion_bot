from notion.client import NotionClient
from notion.block import SubsubheaderBlock, TextBlock, FileBlock, TodoBlock, NumberedListBlock, ColumnListBlock, \
    Block, CollectionViewBlock, DividerBlock, ImageBlock
from notion.collection import CollectionRowBlock
from settings import main_page_url
from os import environ
from dotenv import load_dotenv


class NotionHandler:
    __REALIZED_BLOCKS = (SubsubheaderBlock, TextBlock, TodoBlock, FileBlock, NumberedListBlock, ColumnListBlock,
                         DividerBlock, CollectionViewBlock, ImageBlock)
    __BOLD_SYMBOL_START = "<b>"
    __BOLD_SYMBOL_END = "</b>"
    __TODO_TRUE_SMBL = " ✅"
    __TODO_FALSE_SMBL = " ❌"
    __END_LINE_SMBL = "\n"

    def __init__(self):
        load_dotenv('.env')
        self.token_v2 = environ["token_v2"]
        self.client = NotionClient(self.token_v2)

    @staticmethod
    def __get_attrs_from_item_schema(item: CollectionRowBlock) -> dict:
        attrs = {}
        for dict_attr in item.schema:
            attrs.update({dict_attr["name"]: dict_attr["slug"]})
        return attrs

    def __divider_wrapper(self, item: DividerBlock) -> str:
        return self.__END_LINE_SMBL

    def __image_wrapper(self, item: ImageBlock):
        return f"{item.caption}: {item.get_browseable_url()}" + self.__END_LINE_SMBL

    def __table_query_wrapper(self, item: CollectionRowBlock) -> str:
        txt = ""
        attrs = self.__get_attrs_from_item_schema(item)
        for name, slug in attrs.items():
            txt += f"{name}: {item.__getattr__(slug)}" + self.__END_LINE_SMBL
        return txt

    def __ss_header_wrapper(self, item: SubsubheaderBlock) -> str:
        return self.__txt_to_bold(item.title) + self.__END_LINE_SMBL

    def __txt_wrapper(self, item: TextBlock) -> str:
        return item.title + self.__END_LINE_SMBL

    def __todo_wrapper(self, item: TodoBlock) -> str:
        txt = ""
        if item.checked:
            txt += item.title + self.__TODO_TRUE_SMBL + self.__END_LINE_SMBL
        else:
            txt += item.title + self.__TODO_FALSE_SMBL + self.__END_LINE_SMBL
        return txt

    def __file_wrapper(self, item: FileBlock) -> str:
        return item.title + " url: " + item.get_browseable_url() + self.__END_LINE_SMBL

    def __num_list_wrapper(self, item: NumberedListBlock) -> str:
        return item.title_plaintext + self.__END_LINE_SMBL

    def __collection_view_wrapper(self, item: CollectionViewBlock) -> str:
        txt = self.__txt_to_bold(item.title) + self.__END_LINE_SMBL
        for row in item.collection.get_rows():
            if row.title != "" or row.title is not None:
                txt += self.__table_query_wrapper(row)
        return txt

    def __item_is_used(self, item: Block) -> bool:
        return isinstance(item, self.__REALIZED_BLOCKS)

    def __txt_to_bold(self, txt: str) -> str:
        return f"{self.__BOLD_SYMBOL_START}{txt}{self.__BOLD_SYMBOL_END}"

    def __convert_2_txt_md(self, item: Block) -> str:
        """
        Function to convert Blocks from notion-py to markdown text using private class wrappers:
        __{block_name}_wrapper(item: Block) -> str:

        Function works only with Blocks that in __REALIZED_BLOCKS

        :param item:
        :return txt:
        """
        txt = ""
        if isinstance(item, SubsubheaderBlock):
            txt += self.__ss_header_wrapper(item)
        elif isinstance(item, TextBlock):
            txt += self.__txt_wrapper(item)
        elif isinstance(item, TodoBlock):
            txt += self.__todo_wrapper(item)
        elif isinstance(item, FileBlock):
            txt += self.__file_wrapper(item)
        elif isinstance(item, CollectionViewBlock):
            txt += self.__collection_view_wrapper(item)
        elif isinstance(item, DividerBlock):
            txt += self.__divider_wrapper(item)
        elif isinstance(item, NumberedListBlock):
            txt += self.__num_list_wrapper(item)
        elif isinstance(item, ImageBlock):
            txt += self.__image_wrapper(item)
        return txt

    def __unpack_block(self, block: Block) -> str:
        msg = ''
        for child in block.children:
            for child_inner in child.children:
                if self.__item_is_used(item=child_inner):
                    msg += self.__convert_2_txt_md(child_inner)
                else:
                    msg += self.__unpack_block(child_inner)
        return msg

    def __get_msg(self, task: CollectionRowBlock) -> str:
        msg = self.__txt_to_bold(task.title) + self.__END_LINE_SMBL
        for item in task.children:
            if self.__item_is_used(item):
                msg += self.__convert_2_txt_md(item)
            elif isinstance(item, ColumnListBlock):
                msg += self.__unpack_block(item)

            else:
                print(f"unknown instance: {type(item)} : {item.__repr__()}")

        return msg

    def get_tasks(self) -> tuple[str]:
        processed_tasks = tuple()
        main_page = self.client.get_block(main_page_url)
        tasks = main_page.collection.get_rows()
        for task in tasks:
            task_msg = self.__get_msg(task)
            processed_tasks += tuple(task_msg)
            print(task_msg)
        return processed_tasks

    def get_task(self) -> str:
        main_page = self.client.get_block(main_page_url)
        tasks = main_page.collection.get_rows()
        for task in tasks:
            task_msg = self.__get_msg(task)
            yield task_msg


if __name__ == "__main__":
    nh = NotionHandler()
    for task in nh.get_tasks():
        print(task)
