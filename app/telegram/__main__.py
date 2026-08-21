from app.config.settings import get_settings
from app.telegram.bot import run_polling


if __name__ == "__main__":
    run_polling(get_settings())
