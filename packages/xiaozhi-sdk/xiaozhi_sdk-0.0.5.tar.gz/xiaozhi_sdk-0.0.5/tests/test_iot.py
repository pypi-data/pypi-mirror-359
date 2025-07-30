import os
import sys
import uuid

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk.iot import OtaDevice


@pytest.mark.asyncio
async def test_main():
    serial_number = ""
    license_key = ""
    mac_address = ""
    ota_url = "http://localhost:3080/api/ota"
    ota_url = None
    ota = OtaDevice(mac_addr=mac_address, client_id=str(uuid.uuid4()), serial_number=serial_number, ota_url=ota_url)
    res = await ota.activate_device()
    if not res.get("activation"):
        return
    await ota.check_activate(res["activation"]["challenge"], license_key)
