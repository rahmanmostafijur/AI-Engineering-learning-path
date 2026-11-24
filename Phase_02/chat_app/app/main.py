from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from llm import get_reply
from models import Conversation, Message, User
from schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from sqlalchemy.orm import Session

app = FastAPI()

bearer_scheme = HTTPBearer()


@app.get("/")
def home():
    return {"message": "Chat app running"}


@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ache re bhai age thekei")
    hashed = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="abeh bhul email or pass dichosh")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    email = decode_access_token(credentials.credentials)
    if email is None:
        raise HTTPException(
            status_code=401, detail="abeh tor token er meyed nai abar login kor"
        )
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/me", response_model=UserResponse)
def me(current_user: str = Depends(get_current_user)):
    return current_user


@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = Conversation(title=data.title, user_id=current_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@app.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    )
    return conversations


@app.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == current_user.id
        )
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    user_message = Message(
        conversation_id=conversation.id, role="user", content=data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.id)
        .all()
    )
    messages = [{"role": m.role, "content": m.content} for m in history]
    reply = get_reply(messages)
    assistant_message = Message(
        conversation_id=conversation.id, role="assistant", content=reply
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message


@app.get(
    "/conversations/{conversation_id}/messages", response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.id)
        .all()
    )
    return messages
