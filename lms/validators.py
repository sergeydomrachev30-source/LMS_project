from rest_framework import serializers


class YouTubeValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)
        if url:
            if "youtube.com" not in url:
                raise serializers.ValidationError(
                    "Ссылка должна вести только на youtube.com"
                )
