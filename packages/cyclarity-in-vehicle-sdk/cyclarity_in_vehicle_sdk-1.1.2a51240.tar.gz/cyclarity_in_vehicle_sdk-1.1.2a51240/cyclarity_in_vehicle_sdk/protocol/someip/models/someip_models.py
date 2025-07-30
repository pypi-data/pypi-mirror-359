from typing import Optional
from enum import IntEnum, IntFlag
from pydantic import BaseModel, Field, IPvAnyAddress
from cyclarity_in_vehicle_sdk.utils.custom_types.hexbytes import HexBytes
from cyclarity_in_vehicle_sdk.utils.custom_types.enum_by_name import pydantic_enum_by_name

@pydantic_enum_by_name
class Layer4ProtocolType(IntEnum):
    UDP = 0x11
    TCP = 0x6

class SOMEIP_EVTGROUP_INFO(BaseModel):
    """Model containing information regarding SOME/IP event group
    """
    eventgroup_id: int = Field(description="The Eventgroup ID")
    initial_data: Optional[HexBytes] = Field(default=None, 
                                             description="Initial data associated with the eventgroup if got received")
    
    def __str__(self):
        return (f"Event group ID: {hex(self.eventgroup_id)}" 
                + (f", Data[{len(self.initial_data)}]: {self.initial_data.hex()[:20]}" if self.initial_data else ""))


class SOMEIP_METHOD_INFO(BaseModel):
    """Model containing information regarding SOME/IP method
    """
    method_id: int = Field(description="The Method ID") 
    payload: HexBytes = Field(description="The payload associated with the method")

    def __str__(self):
        return (f"Method ID: {hex(self.method_id)}" 
                + (f", Payload[{len(self.payload)}]: {self.payload[:20]}" if self.payload else ""))

class SOMEIP_ENDPOINT_OPTION(BaseModel):
    """Model containing information regarding SOME/IP endpoint
    """
    endpoint_addr: str = Field(description="The SOME/IP end point IP address")
    port: int = Field(description="The SOME/IP end point port")
    port_type: Layer4ProtocolType = Field(description="The SOME/IP end point protocol type either UDP or TCP")

    def __str__(self):
        return f"Endpoint address: {self.endpoint_addr}, Port: {self.port}, Transport type: {self.port_type.name}"

class SOMEIP_SERVICE_INFO(BaseModel):
    """Model containing information regarding service
    """
    service_id: int = Field(description="The Service ID")
    instance_id: int = Field(description="The instance ID")
    major_ver: int = Field(description="Major version of the service")
    minor_ver: int = Field(description="Minor version of the service")
    ttl: int = Field(description="Life time of the entry in seconds")
    endpoints: list[SOMEIP_ENDPOINT_OPTION] = Field(default=[],
                                                    description="List of endpoints offered by the service")

    def __str__(self):
        return (f"Service ID: {hex(self.service_id)}, "
                f"Instance ID: {hex(self.instance_id)}, "
                f"Version: {self.major_ver}.{self.minor_ver}, "
                f"TTL: {self.ttl}, "
                + ("Endpoints:\n" + f'\n'.join(str(ep) for ep in self.endpoints)) if self.endpoints else ""
                )


class SomeIpSdOptionFlags(IntFlag):
    Reboot = 0x80
    Unicast = 0x40 
    ExplicitInitialData = 0x20