from subprocess import run
from pathlib import Path
from shutil import rmtree
from asyncio import sleep

from aiogram.types import Message, BufferedInputFile, InputMediaPhoto, MediaUnion

def download(url: str):
    code = url.split('?')[0].rstrip('/').rsplit('/', maxsplit=1)[-1]
    print('download', code)
    out = run(['uv', 'run', 'instaloader', '--no-metadata-json', '--no-compress-json', '--no-video-thumbnails', '--dirname-pattern', 'out', '--', f'-{code}'], capture_output=True, text=True).stderr
    print('out:', out)
    if 'Errors or warnings occurred:\n' in out:
        print('error:', out.split('Errors or warnings occurred:\n')[1])
        return out.split('Errors or warnings occurred:\n')[1]

async def reply(message: Message):
    path = Path('out')

    try:
        caption = None
        if list(path.glob('*.txt')):
            caption = next(path.glob('*.txt')).read_text()

        if caption and len(caption) > 1010:
            caption = caption[1010:] + '...'

        if list(path.glob('*.mp4')):
            print('reply video')
            video = next(path.glob('*.mp4'))
            await message.reply_video(BufferedInputFile(video.read_bytes(), video.name), caption=caption, supports_streaming=True)
            return

        photos = list(path.glob('*.jpg'))
        if len(photos) == 1:
            print('reply photo')
            await message.reply_photo(BufferedInputFile(photos[0].read_bytes(), photos[0].name), caption=caption)
        else:
            print('reply media group')
            media: list[MediaUnion] = [InputMediaPhoto(media=BufferedInputFile(photo.read_bytes(), photo.name), caption=caption if i == 0 else None) for i, photo in enumerate(photos)]
            # media[0].caption = caption
            to_send = []
            for i, photo in enumerate(media):
                to_send.append(photo)
                if (i + 1) % 10 == 0:
                    await message.reply_media_group(to_send, caption=caption)
                    await sleep(5)
                    to_send.clear()
            if to_send:
                await message.reply_media_group(to_send, caption=caption)

    finally:
        rmtree(path)