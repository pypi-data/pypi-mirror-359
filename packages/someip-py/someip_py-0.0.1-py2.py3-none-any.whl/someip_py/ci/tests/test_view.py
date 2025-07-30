from someip_py import SOMEIPService


def test_view(service_id, method_id):
    someip_service = SOMEIPService()
    return someip_service.view(service_id, method_id)


if __name__ == "__main__":
    print(test_view(0x1001, 0x0046))
