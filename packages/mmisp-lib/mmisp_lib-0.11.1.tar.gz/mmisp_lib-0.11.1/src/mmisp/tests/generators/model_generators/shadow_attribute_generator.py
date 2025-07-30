import random
import time

from mmisp.db.models.shadow_attribute import ShadowAttribute
from mmisp.lib.attributes import AttributeType
from mmisp.lib.uuid import uuid
from mmisp.tests.generators.object_generator import generate_random_date_str, generate_random_str


def generate_shadow_attribute(org_id: int, event_id: int, event_uuid: str, event_org_id: int) -> ShadowAttribute:
    type: AttributeType = random.choice(AttributeType.all_attributes)
    category: str = random.choice(list(type.categories))
    return ShadowAttribute(
        old_id=0,
        uuid=uuid(),
        org_id=org_id,
        event_id=event_id,
        event_uuid=event_uuid,
        event_org_id=event_org_id,
        type=type.dbkey,
        category=category,
        email="test@test.de",
        value1=generate_random_str(),
        value2=generate_random_str(),
        to_ids=bool(random.getrandbits),
        comment=generate_random_str(),
        deleted=False,
        proposal_to_delete=False,
        disable_correlation=False,
        timestamp=int(time.time()),
        first_seen=generate_random_date_str(),
        last_seen=generate_random_date_str(),
    )
