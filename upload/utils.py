from uuid import uuid4


def generate_attachment_path(filename: str):
    _, extension = filename.rsplit(".", 1)
    return f"uploads/attachment/{uuid4()}.{extension}"


def generate_group_avatar_url():
    return f"uploads/avatars/{uuid4()}.webp"


def generate_profile_picture_url():
    return f"uploads/profiles/{uuid4()}.webp"
