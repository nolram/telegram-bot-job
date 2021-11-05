import config

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import NumberAttribute, UnicodeAttribute


class PhoneIndex(GlobalSecondaryIndex):
    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()
    phone = UnicodeAttribute(hash_key=True)


class EmailIndex(GlobalSecondaryIndex):
    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        projection = AllProjection()
    email = UnicodeAttribute(hash_key=True)

class UserModel(Model):
    """
    A DynamoDB User
    """
    class Meta:
        table_name = config.DYNAMO_TABLE
    user_id = UnicodeAttribute(hash_key=True)
    platform = UnicodeAttribute(range_key=True)
    name = UnicodeAttribute()
    phone = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)

