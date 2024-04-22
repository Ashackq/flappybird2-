import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "flappy_bird.db"


def db_init():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS SCORE(
        game_id INTEGER PRIMARY KEY,
        name VARCHAR(30),
        highscore INTEGER DEFAULT 0
        )
    """
    )
    connection.commit()
    connection.close()


def db_del():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS SCORE")
    connection.commit()
    connection.close()


def db_print():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM SCORE")
    results = cursor.fetchall()
    if not results:
        print("No data found in the database.")
    else:
        print("Game ID\tPlayer Name\tHigh Score")
        print("-------\t------------\t-----------")
        for row in results:
            game_id, name, highscore = row
            print(f"{game_id}\t{name}\t\t{highscore}")
    connection.close()


def save_game_state(score, game_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT highscore FROM SCORE WHERE game_id = ?", (game_id,))
    highscore = cursor.fetchone()
    if highscore is None or score > highscore[0]:
        # Update with new high score
        cursor.execute(
            "UPDATE SCORE SET highscore = ? WHERE game_id = ?", (score, game_id)
        )
    connection.commit()
    connection.close()


def db_save(game_id, name):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO SCORE (game_id, name, highscore) VALUES (?, ?, ?)",
        (game_id, name, 0),
    )
    connection.commit()
    connection.close()


def load_game_state(game_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
        SELECT name,highscore
        FROM SCORE
        WHERE game_id = ?
    """,
            (game_id,),
        )
        result = cursor.fetchone()
        if result is None:
            return None, 0

        name, highscore = result

        return name, highscore

    except sqlite3.Error as e:
        print("Error occurred while loading game state:", e)
        raise
    finally:
        connection.close()


def get_highscores():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT name, highscore FROM SCORE")
    results = cursor.fetchall()
    connection.close()

    names = [row[0] for row in results]
    highscores = [row[1] for row in results]
    return names, highscores


def plot_highscores():
    names, highscores = get_highscores()

    # Create the bar chart
    plt.figure(figsize=(10, 6))  # Adjust figure size as desired
    plt.bar(names, highscores, color="skyblue")
    plt.xlabel("Player Name")
    plt.ylabel("Highscore")
    plt.title("Flappy Bird Highscores")
    plt.xticks(rotation=45, ha="right")  # Rotate player names for better readability

    # Display the plot
    plt.tight_layout()
    plt.show()

