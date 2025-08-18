from random import randint, choice
from os.path import join, exists
from ui import DialogueBubble

class DialogueManager:
    def __init__(self, window, pet, config_dir):
        self.random_dialogues = []
        self.random_dialogue_functions = []
        self.dialogue_bubble = None
        self.config_dir = config_dir
        self.pet = pet
        self.window = window
        self.path = join(self.config_dir, "random_dialogues.json")

    def show_dialogue_bubble(self, message, duration=5):
        print(self.dialogue_bubble)
        if self.dialogue_bubble:
            try:
                print("dialogue output 1")
                self.dialogue_bubble.close_bubble()
            except Exception as e:
                print("dialogue output 2")
                err_msg = f"Error: {str(e)}"
                print(err_msg)
        anim = ["begin_talking", "shrug"]
        self.pet.set_state(choice(anim))

        bubble = DialogueBubble(message, duration=duration, parent=self.window)
        bubble.on_close_callback = lambda: self.pet.set_state("idle")
        pet_x, pet_y = self.window.get_position()
        pet_w, _ = self.window.get_size()
        bubble.move_to_pet(pet_x, pet_y, pet_w)
        self.dialogue_bubble = bubble

    def update_dialogue_bubble(self):
        if self.dialogue_bubble:
            pet_x, pet_y = self.window.get_position()
            pet_w, _ = self.window.get_size()
            self.dialogue_bubble.move_to_pet(pet_x, pet_y, pet_w)
        return True

    def load_random_dialogues(self):
        try:
            if exists(self.path):
                self.random_dialogues = self.window.json_handler(self.path)
            else:
                content = [{"dialogue": "Test dialogue :3"}, {"dialogue": f"Insert dialogues in {self.config_dir}/random_dialogues.json"}]
                self.window.json_handler(self.path, True, content)
                self.random_dialogues = content
        except Exception as e:
            print(f"Error loading random_dialogues.json: {e}")
            self.show_dialogue_bubble(f"Error loading random_dialogues.json: {e}", 10)

    def random_dialogue(self):
        if not self.random_dialogues:
            print("[Dialogue] No dialogues loaded from 'random_dialogues.json'.")
            return
        ran_func = choice(self.random_dialogue_functions) if self.random_dialogue_functions else None
        if randint(ran_func[1][0], ran_func[1][1]) == ran_func[1][0] and ran_func:
            try:
                print(f"[Random Dialogues] Running {ran_func}")
                ran_func[0]()
            except Exception as e:
                print(f"[Random Dialogues] Error trying to run {ran_func}: {e}")
        else:
            self.show_dialogue_bubble(choice(self.random_dialogues)["dialogue"], duration=10)
            self.window.sound_manager.play_random_sound()
    
    def add_func_to_random_dialogues(self, func, chances: list):
        try:
            self.random_dialogue_functions.append([func, chances])
        except Exception as e:
            print(f"Error while trying to add function to random dialogues: {e}")