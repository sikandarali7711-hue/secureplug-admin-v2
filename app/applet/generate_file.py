import re

with open('/app/applet/index.html', 'r') as f:
    orig = f.read()

# Let's inspect the file and replace what's needed cleanly
print("Original size:", len(orig))
