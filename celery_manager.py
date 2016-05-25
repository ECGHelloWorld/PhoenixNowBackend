# celery -A celery_manager worker -B
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import sessionmaker
from db import User
from app import engine

BACKEND_URL = 'db+sqlite:///celerydb.sqlite'

app = Celery('tasks', backend=BACKEND_URL, broker='amqp://localhost')

app.conf.update(
    CELERYBEAT_SCHEDULE = {
        # Resets signins at 7am EDT everyday
        'reset-signins-every-day': {
            'task': 'tasks.reset_signins',
            'schedule': crontab(minute=0, hour=11)
        }
    },
    CELERY_TIMEZONE = 'UTC'
)

@app.task
def reset_signins():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    for user in users:
        user.signedin = False
    session.commit()
