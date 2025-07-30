from nonebot import logger
import pytest


@pytest.mark.asyncio
async def test_bilibili_favlist():
    from nonebot_plugin_resolver2.download import download_imgs_without_raise
    from nonebot_plugin_resolver2.parsers import BilibiliParser

    logger.info("开始解析B站收藏夹 https://space.bilibili.com/396886341/favlist?fid=311147541&ftype=create")
    # https://space.bilibili.com/396886341/favlist?fid=311147541&ftype=create
    fav_id = 311147541
    bilibili_parser = BilibiliParser()
    texts, urls = await bilibili_parser.parse_favlist(fav_id)

    assert texts
    logger.debug(texts)

    assert urls
    logger.debug(urls)

    files = await download_imgs_without_raise(urls)
    assert len(files) == len(urls)
    logger.success("B站收藏夹解析成功")


@pytest.mark.asyncio
async def test_bilibili_video():
    from nonebot_plugin_resolver2.parsers import BilibiliParser

    logger.info("开始解析B站视频 BV1VLk9YDEzB")
    bilibili_parser = BilibiliParser()
    video_info = await bilibili_parser.parse_video_info(bvid="BV1VLk9YDEzB")
    logger.debug(video_info)
    logger.success("B站视频 BV1VLk9YDEzB 解析成功")

    logger.info("开始解析B站视频 BV1584y167sD p40")
    video_info = await bilibili_parser.parse_video_info(bvid="BV1584y167sD", page_num=40)
    logger.debug(video_info)
    logger.success("B站视频 BV1584y167sD p40 解析成功")

    logger.info("开始解析B站视频 av605821754 p40")
    video_info = await bilibili_parser.parse_video_info(avid=605821754, page_num=40)
    logger.debug(video_info)
    logger.success("B站视频 av605821754 p40 解析成功")


@pytest.mark.asyncio
async def test_encode_h264_video():
    import asyncio
    from pathlib import Path

    from bilibili_api import HEADERS

    from nonebot_plugin_resolver2.download import download_file_by_stream, encode_video_to_h264, merge_av
    from nonebot_plugin_resolver2.parsers import BilibiliParser

    bvid = "BV1VLk9YDEzB"
    bilibili_parser = BilibiliParser()
    video_url, audio_url = await bilibili_parser.parse_video_download_url(bvid=bvid)
    v_path, a_path = await asyncio.gather(
        download_file_by_stream(video_url, file_name=f"{bvid}-video.m4s", ext_headers=HEADERS),
        download_file_by_stream(audio_url, file_name=f"{bvid}-audio.m4s", ext_headers=HEADERS),
    )

    video_path = Path(__file__).parent / f"{bvid}.mp4"
    await merge_av(v_path=v_path, a_path=a_path, output_path=video_path)
    video_h264_path = await encode_video_to_h264(video_path)
    assert not video_path.exists()
    assert video_h264_path.exists()


@pytest.mark.asyncio
async def test_no_audio_video():
    from nonebot_plugin_resolver2.parsers import BilibiliParser

    bilibili_parser = BilibiliParser()

    video_url, _ = await bilibili_parser.parse_video_download_url(bvid="BV1gRjMziELt")

    logger.debug(f"video_url: {video_url}")
