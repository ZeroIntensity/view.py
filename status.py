with open("./status.txt") as f:
    lines = f.read().split("\n")
    skip_next = False
    for index, value in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        next = lines[index + 1]
        status, name = value.split(" ", maxsplit=1)
        name = name.replace("-", "").replace(" ", "_").upper()
        print(name, "=", status)
        print('"""\n' + next + '\n"""')
        print()
        skip_next = True
