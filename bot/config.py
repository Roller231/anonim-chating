from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return (
            f"mysql+aiomysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}?charset=utf8mb4"
        )


@dataclass
class Config:
    bot_token: str
    bot_username: str
    db: DbConfig


def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        bot_username=os.getenv("BOT_USERNAME", "anonimnyychatbot"),
        db=DbConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            name=os.getenv("DB_NAME", "anonim_chat"),
        ),
    )
