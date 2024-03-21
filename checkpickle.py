'''
import pickle

def load_pickle(file_path = "game_state.pkl"):
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            return data
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("Error occurred while loading pickle file:", e)
        return None

def display_pickle_contents(file_path = "game_state.pkl"):
    data = load_pickle(file_path)
    if data is not None:
        print("Contents of pickle file:")
        print(data)


def save_pickle(data,file_path="game_state.pkl"):
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
            print("Changes saved successfully.")
    except Exception as e:
        print("Error occurred while saving pickle file:", e)

def modify_game_state(new_game_state,file_path="game_state.pkl" ):
    data = load_pickle(file_path)
    if data is not None:
        data['game_state'] = new_game_state
        save_pickle(data, file_path)

if __name__ == "__main__":
    #file_path = input("Enter the path to the pickle file: ")
    modify_game_state(0)
    display_pickle_contents()
'''