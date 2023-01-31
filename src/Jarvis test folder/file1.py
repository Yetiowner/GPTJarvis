import Jarvis

val = 0

@Jarvis.runnable
def explode(suit_number):
    """Detonates suit. @param suit_number: int representing suit number"""
    print(f"{suit_number} goes boom!")
    print(val)

@Jarvis.runnable
def build(suit_number):
    """Creates and builds suit. @param suit_number: int representing suit number"""
    print(f"Created suit number {suit_number}!")
    print(val)

print("asdfasdf")
