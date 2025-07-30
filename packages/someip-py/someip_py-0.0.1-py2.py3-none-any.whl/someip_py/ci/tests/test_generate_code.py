from someip_py import SOMEIPService


def test_generate_code(path, output=None):
    someip_service = SOMEIPService(platform="V30")
    someip_service.generate_services(path, output=output)


if __name__ == "__main__":
    test_generate_code(
        r"c:\Users\seer.Wu\Downloads\服务矩阵5.4_PB1.7_KV1.1(3.0)\01_服务矩阵包\SOC端服务",
        output="auto_generate_code",
    )
