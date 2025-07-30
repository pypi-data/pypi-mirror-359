from io import TextIOBase
from json import dump
from pathlib import Path

from more_itertools import last

from tumblrbot.utils.common import PreviewLive, UtilClass
from tumblrbot.utils.models import Post


class PostDownloader(UtilClass):
    def paginate_posts(self, blog_name: str, before: int, completed: int, fp: TextIOBase, live: PreviewLive) -> None:
        task_id = live.progress.add_task(f"Downloading posts from '{blog_name}'...", total=None, completed=completed)

        while True:
            response = self.tumblr.retrieve_published_posts(blog_name, before).json()["response"]
            live.progress.update(task_id, total=response["blog"]["posts"])

            if posts := response["posts"]:
                for post in posts:
                    dump(post, fp)
                    fp.write("\n")

                    model = Post.model_validate(post)
                    before = model.timestamp

                    live.progress.update(task_id, advance=1)
                    live.custom_update(model)
            else:
                break

    def get_data_path(self, blog_name: str) -> Path:
        return (self.config.training.data_directory / blog_name).with_suffix(".jsonl")

    def get_data_paths(self) -> list[Path]:
        return list(map(self.get_data_path, self.config.training.blog_names))

    def download(self) -> None:
        self.config.training.data_directory.mkdir(parents=True, exist_ok=True)

        with PreviewLive() as live:
            for blog_name in self.config.training.blog_names:
                data_path = self.get_data_path(blog_name)
                lines = data_path.read_text("utf_8").splitlines() if data_path.exists() else []

                with data_path.open("a", encoding="utf_8") as fp:
                    self.paginate_posts(
                        blog_name,
                        Post.model_validate_json(last(lines, "{}")).timestamp,
                        len(lines),
                        fp,
                        live,
                    )
