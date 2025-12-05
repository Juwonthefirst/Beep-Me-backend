from uuid import uuid4


def generate_attachment_path(filename: str):
    _, extension = filename.rsplit(".", 1)
    return f"uploads/attachment/{uuid4()}.{extension}"
