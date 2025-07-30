from someip_py.secure_upload import encode_aes


def test_encrypt():
    print(encode_aes("123"))


if __name__ == "__main__":
    test_encrypt()
