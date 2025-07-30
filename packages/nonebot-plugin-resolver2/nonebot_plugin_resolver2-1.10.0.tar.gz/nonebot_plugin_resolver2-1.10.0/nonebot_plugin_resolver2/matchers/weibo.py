from nonebot import on_keyword
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.rule import Rule

from ..config import NICKNAME
from ..download import download_imgs_without_raise, download_video
from ..exception import handle_exception
from ..parsers import WeiBoParser
from .filter import is_not_in_disabled_groups
from .helper import get_img_seg, get_video_seg, send_segments

weibo_parser = WeiBoParser()

weibo = on_keyword(keywords={"weibo.com", "m.weibo.cn"}, rule=Rule(is_not_in_disabled_groups))


@weibo.handle()
@handle_exception()
async def _(event: MessageEvent):
    message = event.message.extract_plain_text().strip()
    video_info = await weibo_parser.parse_share_url(message)

    ext_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
        "referer": "https://weibo.com/",
    }

    await weibo.send(f"{NICKNAME}解析 | 微博 - {video_info.title} - {video_info.author}")
    if video_info.video_url:
        video_path = await download_video(video_info.video_url, ext_headers=ext_headers)
        await weibo.finish(get_video_seg(video_path))
    if video_info.pic_urls:
        image_paths = await download_imgs_without_raise(video_info.pic_urls, ext_headers=ext_headers)
        if image_paths:
            await send_segments([get_img_seg(path) for path in image_paths])
