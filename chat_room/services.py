from livekit import api
from channels.db import database_sync_to_async
from chat_room.models import CallHistory


async def decline_call(user_id: int, call_id: str):
    try:
        async with api.LiveKitAPI() as client:
            await client.room.delete_room(api.DeleteRoomRequest(room=call_id))

        callHistoryModel = await database_sync_to_async(CallHistory.objects.get)(
            id=int(call_id)
        )
        await database_sync_to_async(callHistoryModel.decline_call)(user_id)
    except api.twirp_client.TwirpError as error:
        print("Error deleting livekit room:", error)

    except CallHistory.DoesNotExist:
        print("CallHistory with id", call_id, "does not exist")

    except Exception as error:
        print("Error deleting livekit room:", error)
