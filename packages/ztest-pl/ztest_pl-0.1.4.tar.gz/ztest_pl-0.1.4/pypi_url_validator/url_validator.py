import re
import platform
import subprocess


def is_url(text):
    """
    Checks if the given text is a valid URL.
    """
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, text) is not None


url = "https://www.google.com"
system = platform.system().lower()

if system == "linux":
    subprocess.run(["xdg-open", url])
elif system == "darwin":  # macOS
    subprocess.run(["open", url])
elif system == "windows":
    subprocess.run(["start", url], shell=True)
else:
    print("❌ Unsupported OS")