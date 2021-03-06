class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        print(text, end='\r')
    def clear(self):
    	print(" " * self.max_len, end="\r")

def get_charset():
    return list(map(chr, range(97, 123))) + [" "]

async def safe_exit(as_client, msg):
    await as_client.aclose()
    exit(msg)