import logging
from typing import Optional, Any

from media.media_manager import delete_media, Media


class StateTime:
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0

    def __init__(self, data: dict[str, Any] = None):
        if data is None:
            data = {}

        self.update(data)

    def sum(self, name: str, value: int):
        last_value = getattr(self, name)
        new_value = last_value + value
        if new_value < 0:
            new_value = 0
        setattr(self, name, new_value)
        logging.info(getattr(self, name))

    def update(self, data: dict[str, Any]):
        simple_args = ['year', 'month', 'day', 'hour', 'minute']
        for arg in simple_args:
            if arg in data:
                setattr(self, arg, data[arg])

    def reset(self):
        simple_args = ['year', 'month', 'day', 'hour', 'minute']
        for arg in simple_args:
            setattr(self, arg, 0)

    def dict(self):
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute
        }


class StateTimeData(StateTime):
    amount: int = 1

    def __init__(self, data: dict[str, Any] = None):
        if data is None:
            data = {}

        super().__init__(data)

        if "amount" in data:
            self.amount = data["amount"]
            if self.amount < 1:
                self.amount = 1

    def reset(self):
        super().reset()
        self.amount = 1

    def dict(self):
        data = super().dict()
        return {
            **data,
            "amount": self.amount
        }


class StatePost:
    text: Optional[str] = None
    caption: Optional[str] = None
    media: Optional[str] = None
    media_type: Optional[Media] = None

    create: bool = False
    period: Optional[StateTime] = StateTime()
    frequency: Optional[StateTime] = StateTime()
    period_time: float = 0
    frequency_time: float = 0

    def __init__(self, data: dict[str, Any]):
        simple_args = ['text', 'create', 'period_time', 'frequency_time', 'caption', 'media']
        for arg in simple_args:
            if arg in data:
                setattr(self, arg, data[arg])

        if media_type := data.get('media_type'):
            self.media_type = Media(media_type)

        if period := data.get('period'):
            self.period = StateTime(period)

        if frequency := data.get('frequency'):
            self.frequency = StateTime(frequency)

    def dict(self):
        return {
            "text": self.text,
            "caption": self.caption,
            "media": self.media,
            "media_type": self.media_type.value if self.media_type else None,

            "create": self.create,
            "period_time": self.period_time,
            "frequency_time": self.frequency_time,
            "period": None if self.period is None else self.period.dict(),
            "frequency": None if self.frequency is None else self.frequency.dict()
        }


class StateChat:
    name: str

    def __init__(self, data: dict[str, Any]):
        if 'name' in data:
            self.name = data['name']

    def dict(self):
        return {
            "name": self.name
        }


class StateUser:
    user_id: int
    name: str
    username: str

    def __init__(self, data: dict[str, Any] = None):
        if not data:
            data = {}

        simple_args = ['user_id', 'name', 'username']
        for arg in simple_args:
            if arg in data:
                setattr(self, arg, data[arg])

    def dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "username": self.username
        }


class StateSession:
    info: Optional[StateUser] = StateUser()
    is_blocked: bool = False

    _selected_post: Optional[StatePost] = None
    selected_post_name: Optional[str] = None

    timer_message_id: Optional[int] = None
    time_data: Optional[StateTimeData] = StateTimeData()

    posts: Optional[dict[str, StatePost]] = {}
    chats: Optional[dict[int, StateChat]] = {}

    def __init__(self, data: dict[str, Any] = None):
        if data is None:
            data = {}

        if 'info' in data:
            self.info = StateUser(data['info'])

        if 'time_data' in data:
            self.time_data = StateTimeData(data['time_data'])

        if 'posts' in data:
            for key, post in data['posts'].items():
                self.posts[key] = StatePost(post)

        if 'chats' in data:
            for key, chat in data['chats'].items():
                self.chats[key] = StateChat(chat)

        simple_args = ['selected_post_name', 'timer_message_id', 'user_id', 'name', 'username', 'is_blocked']
        for arg in simple_args:
            if arg in data:
                setattr(self, arg, data[arg])

    @property
    def selected_post(self):
        if not self.selected_post_name or self.selected_post_name not in self.posts:
            return None
        return self.posts[self.selected_post_name]

    def add_post(self, name: str, post: StatePost):
        self.posts[name] = post

    def delete_post(self, name: str):
        post = self.posts.pop(name)
        if post.media:
            delete_media(post.media, post.media_type)

    def dict(self):
        posts = None if self.posts is None else {key: post.dict() for key, post in self.posts.items()}
        chats = None if self.chats is None else {key: chat.dict() for key, chat in self.chats.items()}

        return {
            'info': self.info.dict(),
            'is_blocked': self.is_blocked,
            'selected_post_name': self.selected_post_name,
            'timer_message_id': self.timer_message_id,
            'time_data': None if self.time_data is None else self.time_data.dict(),
            'posts': posts,
            'chats': chats
        }


class StateAuth:
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    code_hash: Optional[str] = None
    code: Optional[int] = None

    def __init__(self, data: dict[str, Any] = None):
        if data is None:
            data = {}

        simple_args = ['name', 'phone', 'password', 'code_hash', 'code']
        for arg in simple_args:
            if arg in data:
                setattr(self, arg, data[arg])

    def dict(self):
        return {
            'name': self.name,
            'phone': self.phone,
            'password': self.password,
            'code_hash': self.code_hash,
            'code': self.code
        }


class State:
    _selected_user: Optional[StateSession] = None
    selected_user_name: Optional[str] = None

    sessions: Optional[dict[str, StateSession]] = {}
    auth: Optional[StateAuth] = StateAuth()

    def __init__(self, data: dict[str, Any] = None):
        if data is None:
            data = {}

        if 'sessions' in data:
            for key, session in data['sessions'].items():
                self.sessions[key] = StateSession(session)

        if 'auth' in data:
            self.auth = StateAuth(data['auth'])

        if 'selected_user_name' in data:
            self.selected_user_name = data['selected_user_name']

    @property
    def selected_user(self):
        if not self.selected_user_name or self.selected_user_name not in self.sessions:
            return None
        return self.sessions[self.selected_user_name]

    def clear_auth(self):
        self.auth = StateAuth()

    def add_session(self, name, session: StateSession):
        if self.selected_user_name in self.sessions:
            posts = self.sessions[name].posts
            session.posts = posts

        self.sessions[name] = session

    def delete_session(self, name):
        if name in self.sessions:
            del self.sessions[name]

    def dict(self):
        sessions = None if self.sessions is None else {key: session.dict() for key, session in self.sessions.items()}

        return {
            'selected_user_name': self.selected_user_name,
            'sessions': sessions,
            'auth': self.auth.dict()
        }

