
try:
    from utils import config
except ImportError:
    from ...utils import config

from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute, ListAttribute

class UserModel(Model):
    """
        A DynamoDB User
    """
    class Meta:
        table_name = config.DYNAMO_TABLE_USER
        host = config.DYNAMO_HOST
    user_id = UnicodeAttribute(hash_key=True, attr_name='pk')
    chat_type = UnicodeAttribute(range_key=True, attr_name='sk')
    name = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)
    working_model = NumberAttribute(null=True)
    interview_model = NumberAttribute(null=True)
    skills = ListAttribute(default=list)
    jobs_preference = ListAttribute(default=list)
    phone = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)


class HistoryChatModel(Model):
    """
        A DynamoDB History Chat
    """
    class Meta:
        table_name = config.DYNAMO_TABLE_HISTORY_CHAT
        host = config.DYNAMO_HOST
    user_id = UnicodeAttribute(hash_key=True, attr_name='pk')
    date_chat = UnicodeAttribute(range_key=True, attr_name='sk')
    last_state = NumberAttribute()
