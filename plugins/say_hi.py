def say_hi(pet, window):
    pet.set_state("begin_talking")
    window.sound_manager.play_random_sound()
    window.dialogue_manager.show_dialogue_bubble("Hi from plugin!", 5)

plugin = {
    "label": "Say Hi",
    "callback": say_hi
}
