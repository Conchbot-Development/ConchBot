from tortoise import fields
from tortoise.models import Model


class TagModel(Model):
    guild_id = fields.IntField()
    author_id = fields.IntField()
    name = fields.TextField()
    content = fields.TextField()
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    uses = fields.IntField()

    def __str__(self):
        return self.content
