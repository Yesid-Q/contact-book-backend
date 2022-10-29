
def send_email(email: str, message: str = '') -> None:
    with open("log.txt", mode="w") as email_file:
        content = f"{email}: token {message}"
        email_file.writelines(content)
