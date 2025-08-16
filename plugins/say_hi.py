def say_hi(pet, window):
    pet.set_state("begin_talking")
    window.show_dialogue_bubble("Hi from plugin!", 5)

plugin = {
    "label": "Say Hi",
    "callback": say_hi
}
