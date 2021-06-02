import managers


class YouTube:

    @staticmethod
    async def info(y_id: str, format=None) -> dict:
        youtube = managers.YouTube(y_id, format)
        result = await youtube.get_info()
        result['filtered_formats'] = youtube.filter_formats()
        if format:
            result['status'], result['url'] = youtube.check_status()
        return result
