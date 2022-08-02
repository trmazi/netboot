from typing import Optional

from .interface import OutletInterface
from .snmp import SNMPOutlet


class AP7900Outlet(OutletInterface):
    def __init__(self, *, host: str, outlet: int) -> None:
        if outlet < 1 or outlet > 8:
            raise Exception("Out of bounds outlet number!")

        self.snmp = SNMPOutlet(
            host=host,
            query_oid=f"1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.{outlet}",
            query_on_value=1,
            query_off_value=2,
            update_oid=f"1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.{outlet}",
            update_on_value=1,
            update_off_value=2,
        )

    def getState(self) -> Optional[bool]:
        return self.snmp.getState()

    def setState(self, state: bool) -> None:
        return self.snmp.setState(state)
