import discord
import random
import datetime


class Embeds:
    def __init__(self):
        self.cooldown_choices = [
            "Woah, slow down man",
            "A little too quick there",
            "Too fast man",
            "Spamming is cool"
        ]
        self.time = datetime.datetime.utcnow().strftime('%Y:%m:%d %H:%M:%S')
        self.error_codes = {
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Page Not found",
            429: "Too many requests",
        }

    def OnError(self, command_name: str, time: str, reason: str):
        Embed = discord.Embed(title="Oh no an error occurred", color=discord.Color.red())
        Embed.add_field(name="Command Name: ", value=command_name)
        Embed.add_field(name="At: ", value=time)
        Embed.add_field(name="Reason", value=reason)
        return Embed

    def OnCooldown(self, error: str):
        cooldown_name = random.choice(self.cooldown_choices)
        Embed = discord.Embed(title=cooldown_name, description=f"You need to slow down and don't spam the "
                                                               f"bot\n Retry after {int(error.retry_after)}s",
                              color=discord.Color.blue())
        return Embed

    def OnApiError(self, command_name: str, status: int):
        Embed = discord.Embed(title="Oh no an error occurred", color=discord.Color.red(),
                              description="Sorry but something went wrong. DM Jerry.py#4249 if it keeps happening")
        Embed.add_field(name="Command Name: ", value=command_name)
        Embed.add_field(name="At: ", value=self.time)
        if status in self.error_codes:
            status_reason = self.error_codes[status]
            Embed.add_field(name="API Status", value=f"{status} - {status_reason}")
        else:
            Embed.add_field(name="API Status", value=f"{status}")
        return Embed

    @staticmethod
    def _error_codes():
        return {
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Page Not found",
            429: "Too many requests",
        }

    @staticmethod
    def _cooldown_messages():
        return [
            "Woah, slow down man",
            "A little too quick there",
            "Too fast man",
            "Spamming is cool"
        ]

    @staticmethod
    def _time():
        return datetime.datetime.utcnow().strftime('%Y:%m:%d %H:%M:%S')
