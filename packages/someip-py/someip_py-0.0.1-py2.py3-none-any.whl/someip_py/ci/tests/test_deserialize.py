from someip_py.service_interface.V2x.ADCU_HmiService.AlarmInfoInf import AlarmInfo
from someip_py.service_interface.V2x.ADCU_HmiService.AvpEgoPositionInMapInf import (
    IdtAvpEgoPositionInMap,
)
from someip_py.service_interface.V2x.ADCU_HmiService.FeatureStateInf import FeatureState
from someip_py.service_interface.V2x.ADCU_HmiService.FeatureStateInf2 import (
    FeatureState2,
)
from someip_py.service_interface.V2x.ADCU_HmiService.GNSSMsgInf import IdtGNSSMsg
from someip_py.service_interface.V2x.ADCU_HmiService.IntegAdpuConfigInf import (
    IntegAdpuConfig,
)
from someip_py.service_interface.V2x.ADCU_HmiService.TrafficRedWarningInf import (
    TrafficRedWarningInfo,
)
from someip_py.service_interface.V2x.ADCU_HmiService.VehicleRegionInf import (
    IdtVehicleRegion,
)

if __name__ == "__main__":
    # 0x8136
    s = FeatureState2().deserialize(
        bytes.fromhex("00000012000a00000000000b00000000000c00000000")
    )
    print(s)
    # 0x8070
    s = IdtVehicleRegion().deserialize(bytes.fromhex("00"))
    print(s)
    # 0x8067
    s = TrafficRedWarningInfo().deserialize(bytes.fromhex("00000000"))
    print(s)
    # 0x8047
    s = IdtAvpEgoPositionInMap().deserialize(
        bytes.fromhex("48b6eaa0ca52f208000000000000000000000000000000003f800000000000")
    )
    print(s)
    # 0x8046
    s = IdtGNSSMsg().deserialize(
        bytes.fromhex(
            "c066800000000000c06680000000000000000000000000000000000000000000c076800000000000c08f40000000000044b0c6d6000000000000000000000000000000000000000000000000"
        )
    )
    print(s)
    # 0x8044
    s = IntegAdpuConfig().deserialize(bytes.fromhex("01"))
    print(s)
    # 0x8014
    s = FeatureState().deserialize(
        bytes.fromhex(
            "01010000000000000000000000000201010100010002000000020000000000000000000000000000000100000001ffff00000000000000000000000000000000000000000000000000000003000000000001000000000000000300010000000000000000000000000000000000000000"
        )
    )
    print(s)
    # 0x8012
    s = AlarmInfo().deserialize(bytes.fromhex("0000000000000000000000000000ffffff"))
    print(s)
