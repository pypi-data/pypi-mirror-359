import time

from someip_py import SOMEIPService
from someip_py.frame import SOMEIPFrame

service = SOMEIPService()


def cb(frame: SOMEIPFrame):
    print(frame)
    print(
        service.decode_payload(frame.service_id, frame.method_id, payload=frame.payload)
    )


if __name__ == "__main__":
    server = service.as_server(
        service="ADCU_HmiService",
        interfaces=["SettingDrivingInfoInf"],
        local_bind_address="10.114.124.27",
    )
    time.sleep(1)
    frame = service.as_client(
        "ADCU_HmiService",
        "SettingDrivingInfoInf",
        typ="sub",
        target_address="10.114.124.27",
        local_bind_address="198.18.36.250",
    )
    print(frame)
    service_id = service.origin["ADCU_HmiService"]["service_id"]
    eventgroup_id = service.origin["ADCU_HmiService"]["interface"][
        "SettingDrivingInfoInf"
    ]["eventgroup_id"]
    event_id = service.origin["ADCU_HmiService"]["interface"]["SettingDrivingInfoInf"][
        "method_id"
    ]
    server.update_notification(
        service_id,
        eventgroup_id,
        event_id,
        service.encode_payload(service_id, event_id, structures={"ALCSwitch": 50}),
    )
    frame = service.as_client(
        "ADCU_HmiService",
        "SettingDrivingInfoInf",
        typ="sub",
        target_address="10.114.124.27",
        local_bind_address="198.18.36.250",
    )
    print(frame)
