with open("status.txt") as f:
    text = f.read().split("\n")
    collected = [[]]
    index = 0
    count = 0
    for i in text:
        if count == 3:
            count = 0
            index += 1
            collected.append([])
        count += 1
        collected[index].append(i)

    for collect in collected:
        raw_name, desc, _ = collect
        status, name = raw_name.split(" ", maxsplit=1)
        name = name.replace("(WebDAV)", "")
        status = int(status)
        cls = "ClientSideError" if status < 500 else "ServerSideError"
        output = f'''
class {name.replace(' ', '')}({cls}):
    """{desc}"""

    status_code = {status}
'''
        print(output)
