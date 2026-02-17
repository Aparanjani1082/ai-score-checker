try:
    with open("file4.txt", "r") as f:
        print(f.read())
except FileNotFoundError:
    with open("file4.txt", "w") as f:
        f.write("hello welcome")
        print(f.write)