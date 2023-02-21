import datetime
from bot import models


class NoLocationException(Exception):
    pass


async def get_user(username, first_name, last_name, id):
    user, created = await models.User.objects.aget_or_create(id=id)
    if created:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        await user.asave()
    return user


async def store_location(user, lat, lon, accuracy, when):
    location = models.UserLocation(
        user=user,
        latitude=lat,
        longitude=lon,
        accuracy_meters=accuracy,
        created_at=when,
    )
    await location.asave()
    return location


async def store_photo(user: models.User, photo_stream: bytes, when: datetime.datetime):
    # Find the location
    threshold = datetime.timedelta(minutes=5)
    freshness = datetime.datetime.now() - threshold
    latest_location = (
        await models.UserLocation.objects.all()
        .filter(user=user, created_at__lte=when)
        .filter(created_at__gte=freshness)
        .order_by("-created_at")
        .afirst()
    )
    if latest_location is None:
        raise NoLocationException()
    photo = models.Photo(
        user=user,
        content=photo_stream,
        created_at=when,
        location=latest_location,
    )
    # TODO should we pull data from the exif?
    # TODO I know storing photos in the DB sucks, but it's with the other data
    await photo.asave()
    return photo


async def store_chat(user_id: int, chat: str):

    if len(chat) > 20:
        return
    user = await models.User.objects.aget(id=user_id)
    user.phone = chat
    await user.asave()
