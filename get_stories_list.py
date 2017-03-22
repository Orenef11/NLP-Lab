import pycurl
from io import BytesIO

HOST = r"http://www.shortstoryproject.com/he"
USERAGENT = r"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
ACTION_PHP = r"http://www.shortstoryproject.com/wp-content/themes/maaboret2016/action.php"


def urlget(header, response):
    print('Get function start')
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, HOST)
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    curl.setopt(pycurl.HEADERFUNCTION, header.write)
    curl.setopt(pycurl.WRITEFUNCTION, response.write)
    curl.setopt(pycurl.COOKIEJAR, 'cookie.txt')
    curl.setopt(pycurl.COOKIEFILE, 'cookie.txt')
    curl.perform()
    curl.close()
    print('Get function end')


def urlpost(header, response):
    print('Post function start')
    curl = pycurl.Curl()
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.URL, ACTION_PHP)
    curl.setopt(pycurl.USERAGENT, USERAGENT)
    curl.setopt(pycurl.HTTPHEADER, ["Connection: keep-alive", "Expect:"])
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    curl.setopt(pycurl.HEADERFUNCTION, header.write)
    curl.setopt(pycurl.WRITEFUNCTION, response.write)
    curl.setopt(pycurl.COOKIEJAR, 'cookie.txt')
    curl.setopt(pycurl.COOKIEFILE, 'cookie.txt')
    curl.setopt(pycurl.HTTPPOST, [("posts", "1000000"), ("offset", "0"), ("lang", "he")])
    curl.perform()
    curl.close()
    print('Post function end')


def main():
    header = BytesIO()
    response = BytesIO()
    print('Get main page & cookie')
    urlget(header, response)
    for line in header.getvalue().splitlines():
        print(line.decode())
    str_response = response.getvalue().decode()
    print(str_response)

    print()
    print()

    header = BytesIO()
    response = BytesIO()
    print('Post library page loader')
    urlpost(header, response)
    for line in header.getvalue().splitlines():
        print(line.decode())
    str_response = response.getvalue()
    with open('stories_list.html', 'wb') as file:
        file.write(str_response)


if __name__ == '__main__':
    main()
