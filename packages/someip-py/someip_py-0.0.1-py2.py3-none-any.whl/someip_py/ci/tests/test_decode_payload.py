from someip_py import SOMEIPService


def test_decode_payload(service_id, method_id, payload):
    someip_service = SOMEIPService()
    return someip_service.decode_payload(service_id, method_id, payload=payload)


if __name__ == "__main__":
    print(
        test_decode_payload(
            0x1001,
            0x0046,
            bytes.fromhex(
                "c066800000000000c06680000000000000000000000000000000000000000000c076800000000000c08f40000000000044b0c6d6000000000000000000000000000000000000000000000000"
            ),
        )
    )
