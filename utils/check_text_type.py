import re

def is_url(text: str) -> bool:
    # Regex URL
    url_pattern = re.compile(
        r'^(https?:\/\/)?'        # http:// or https://
        r'([\w\-]+\.)+[\w]{2,}'   # domain
        r'(\/[\w\-._~:\/?#\[\]@!$&\'()*+,;=%]*)?$'  # path
    )
    return bool(url_pattern.match(text.strip()))

def is_vietnamese(text: str) -> bool:
    # Kiểm tra xem có dấu tiếng Việt không
    pattern = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.IGNORECASE)
    return bool(pattern.search(text))