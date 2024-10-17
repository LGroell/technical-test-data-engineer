from .config import engine
from .get_data import main
from .models import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    main()
