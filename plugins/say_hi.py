def say_hi(pet, window):
    pet.set_state("begin_talking")
    window.play_random_sound()
    window.show_dialogue_bubble("Hi from plugin!", 5)

plugin = {
    "label": "Say Hi",
    "callback": say_hi
}
