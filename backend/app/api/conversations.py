from fastapi import APIRouter

from app.services.conversation_state import ConversationStateService

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get("/users/{user_id}/state")
def get_user_state(user_id: str):
    state = ConversationStateService()
    return state.get_user_state(user_id=user_id)


@router.get("/users/{user_id}/sessions/{session_id}/history")
def get_conversation_history(user_id: str, session_id: str):
    state = ConversationStateService()
    return {
        "user_id": user_id,
        "session_id": session_id,
        "history": state.get_history(user_id=user_id, session_id=session_id),
    }
