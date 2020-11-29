
def test(is_type):
    a = "1"
    is_work = False
    if is_type == 1:
        try:
            is_work = True
        except Exception as e:
            print(e)
    else:
        try:
            b = a +1
            is_work = True
        except Exception as e:
            print(e)

    return is_work

print(test(2))