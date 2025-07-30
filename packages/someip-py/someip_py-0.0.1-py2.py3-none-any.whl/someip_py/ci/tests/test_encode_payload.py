from someip_py import SOMEIPService


def test_encode_payload(service_id, method_id, structures):
    someip_service = SOMEIPService()
    print(someip_service.view(service_id, method_id))
    payload = someip_service.encode_payload(
        service_id, method_id, structures=structures
    )
    return someip_service.decode_payload(service_id, method_id, payload=payload)


if __name__ == "__main__":
    print(test_encode_payload(0x1001, 0x0012, {"SoundEffectSeN": 20}))
