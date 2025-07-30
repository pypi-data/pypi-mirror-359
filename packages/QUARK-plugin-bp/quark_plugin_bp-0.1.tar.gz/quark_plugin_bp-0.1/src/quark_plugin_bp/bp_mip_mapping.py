from dataclasses import dataclass
from typing import Any, override

from quark.core import Core, Data, Result
from quark.interface_types import Other

from quark_plugin_bp.utils import create_mip


@dataclass
class BpMipMapping(Core):
    @override
    def preprocess(self, data: Any) -> Result:
        self._mip_mapping = create_mip(data.data)
        return Data(Other(self._mip_mapping))

    @override
    def postprocess(self, data: Any) -> Result:
        return Data(Other(data.data[0]))
