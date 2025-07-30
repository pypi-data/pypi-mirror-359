import random
import string
from typing import Any

from sqlalchemy import func

from mmisp.api_schemas.attributes import GetAttributeTag
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.db.models.tag import Tag
from mmisp.plugins.enrichment.data import NewTag
from mmisp.plugins.models.attribute import AttributeTagWithRelationshipType
from mmisp.tests.generators.object_generator import generate_random_str


def generate_number() -> int:
    number = random.randint(1, 4)
    return number


def generate_ids() -> str:
    id_str = random.randint(1, 10)
    return str(id_str)


def generate_ids_as_str() -> str:
    return str(generate_ids())


def random_string_with_punctuation(length: int = 10) -> str:
    return random_string(length - 1).join(random.choice(string.punctuation))


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_hexcolour(length: int = 3) -> str:
    return "#" + "".join(random.choices(string.hexdigits, k=length))


def generate_valid_required_tag_data() -> TagCreateBody:
    return TagCreateBody(
        name=random_string(),
        colour=random_hexcolour(6),
        exportable=bool(random.getrandbits),
    )


def generate_valid_tag_data() -> TagCreateBody:
    return TagCreateBody(
        name=random_string(),
        colour=random_hexcolour(6),
        exportable=bool(random.getrandbits),
        org_id=generate_ids_as_str(),
        user_id=generate_ids_as_str(),
        hide_tag=bool(random.getrandbits),
        numerical_value=generate_number(),
        inherited=bool(random.getrandbits),
    )


def generate_get_attribute_tag_response() -> GetAttributeTag:
    return GetAttributeTag(
        id=generate_ids_as_str(),
        name=random_string(),
        colour=random_hexcolour(6),
        numerical_value=generate_number(),
        is_galaxy=bool(random.getrandbits),
        local=bool(random.getrandbits),
    )


def generate_attribute_tag_with_relationship_type() -> AttributeTagWithRelationshipType:
    tag: GetAttributeTag = generate_get_attribute_tag_response()
    return AttributeTagWithRelationshipType(
        **tag.dict(), relationship_local=bool(random.getrandbits), relationship_type=random_string()
    )


def generate_exising_new_tag() -> NewTag:
    return NewTag(tag_id=generate_ids(), local=bool(random.getrandbits), relationship_type=generate_random_str())


def generate_new_new_tag() -> NewTag:
    return NewTag(
        tag=generate_valid_tag_data(), local=bool(random.getrandbits), relationship_type=generate_random_str()
    )


def generate_invalid_tag_data() -> Any:
    input_list = [
        random_string(),
        random_hexcolour(6),
        bool(random.getrandbits),
    ]
    random_list = [0, 1, 2]
    for number in random.sample(random_list, random.randint(1, len(input_list) - 1)):
        input_list[number] = None

    return {"name": input_list[0], "colour": input_list[1], "exportable": input_list[2]}


def generate_tags(db, number: int = 10) -> list:
    tag_ids = []
    for _ in range(number):
        new_tag = Tag(**generate_valid_tag_data().dict())
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        tag_ids.append(new_tag.id)

    return tag_ids


def get_non_existing_tags(db, number: int = 10) -> list:
    tag_ids = []
    largest_id = db.query(func.max(Tag.id)).scalar()
    print(largest_id)
    if not largest_id:
        largest_id = 1
    for i in range(1, number + 1):
        tag_ids.append(largest_id + i * random.randint(1, 9))
    print(tag_ids)
    return tag_ids


def get_invalid_tags(number: int = 10) -> list:
    length = 5
    invalid_tags = []
    for _ in range(number):
        invalid_tags.append("".join(random.choices(string.ascii_letters, k=length)))
    return invalid_tags


def remove_tags(db, ids: list[int]) -> None:
    for id in ids:
        tag = db.get(Tag, id)
        db.delete(tag)
        db.commit()
