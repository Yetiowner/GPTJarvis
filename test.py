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

Jarvis.init()
quit()

#print(chatbot.query("Quote what is said about Tony the Pony on question 1732348 on SO? Start from 'You can't parse [X]...', and translate it into french. Only say the first 5 words."))
#print(chatbot.query("How many answers are on stack overflow question 75221583?"))
#print(chatbot.query("What is the latest post from Rick Roals on quora? Quote him in full, and give me the link to the post."))
#print(chatbot.query("Give me the etymology of water using the wikipedia article for water."))
#print(chatbot.query("Is it the evening right now?"))
#print(chatbot.query("What is x if (e^(x^2))/x=5+x?"))
#print(chatbot.query("What is d/dx if f(x) = (e^(x^2))/x?"))
#print(chatbot.query("What is en passant?"))
#print(chatbot.query("What is the weather today? I live at 30, 30."))
#print(chatbot.query("Tell me a story."))
#print(chatbot.query("How many dogecoin is a dollar worth right now?"))
#print(chatbot.query("What is my IP address?"))
#print(chatbot.query("Where am I?")) # TODO fix
#print(chatbot.query("How many people live in the US right now according to google?"))
#print(chatbot.query("How many people have covid right now? Use google."))
#print(chatbot.query("Translate the entire rick roll lyrics into french"))
#print(chatbot.query("How does the queen move? Check from wikipedia"))
# Information test
#print(chatbot.query("What is my name?"))
#print(chatbot.query("What is your name? Also, what is my name?"))
# Programming test
print(Jarvis.query("Jarvis, build the mark 42"))
#print(Jarvis.query("Jarvis, do me a favour and blow mark 42"))