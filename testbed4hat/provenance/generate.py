import logging
from pathlib import Path

from ..testbed4hat.serge import SergeGame


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Path initialisations
    data_folder = Path("data")
    csv_folder = Path("csv")
    target_folder = Path("target")

    session_id = "wargame-l6nngxlk"
    db_filepath = data_folder / f"{session_id}.json"
    log_file_handler = logging.FileHandler(target_folder / f"{session_id}.log")
    logger.addHandler(log_file_handler)

    world = SergeGame(session_id)

    # loading the data
    initial_wargame, documents = read_game_db(db_filepath)
    documents.sort(key=lambda doc: doc.timestamp)
    # skipping all the first consecutive InfoMessage except the last one to use the latest game state before it starts
    k: int = 0
    while k + 1 < len(documents) and documents[k + 1].messageType == "InfoMessage":
        logger.debug(
            "[Skipping %s at %s]", documents[k].messageType, documents[k].timestamp
        )
        k += 1
    world.init_game(documents[k].data)
    world.process_documents(documents[k:])

    # export the bindings
    world.write_bindings(csv_folder / f"{session_id}.csv")
