def password_validcheck(pwd):
    if len(pwd) < 8:
        return False

    if pwd.isalnum():
        return False
    else:
        return True
