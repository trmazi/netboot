import unittest
from typing import List, Optional, Tuple
from unittest.mock import MagicMock, patch

# We import internal stuff here since we don't want to test the public
# interfaces.
from netboot.cabinet import Cabinet, CabinetStateEnum, CabinetRegionEnum


class TestCabinet(unittest.TestCase):
    def spawn_cabinet(
        self,
        state: Optional[CabinetStateEnum] = None,
        filename: Optional[str] = None,
    ) -> Tuple[Cabinet, MagicMock]:
        cabinet = Cabinet(
            ip="1.2.3.4",
            region=CabinetRegionEnum.REGION_USA,
            description="test",
            filename=filename,
            patches={},
            settings={},
            srams={},
        )
        host = MagicMock()
        host.ip = "1.2.3.4"
        cabinet._Cabinet__host = host  # type: ignore
        if state is not None:
            cabinet._Cabinet__state = (state, 0)  # type: ignore
        return (cabinet, host)

    def test_state_initial(self) -> None:
        logs: List[str] = []
        with patch('netboot.cabinet.log', new_callable=lambda: lambda log, newline: logs.append(log)):
            cabinet, _ = self.spawn_cabinet()
            self.assertTrue(cabinet.state[0], CabinetStateEnum.STATE_STARTUP)

            cabinet.tick()
            self.assertTrue(cabinet.state[0], CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_ON)
            self.assertEqual(["Cabinet 1.2.3.4 waiting for power on."], logs)

    def test_state_host_dead_no_transition(self) -> None:
        logs: List[str] = []
        with patch('netboot.cabinet.log', new_callable=lambda: lambda log, newline: logs.append(log)):
            cabinet, host = self.spawn_cabinet(state=CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_ON)
            host.alive = False

            cabinet.tick()
            self.assertTrue(cabinet.state[0], CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_ON)
            self.assertEqual([], logs)

    def test_state_host_alive_no_game_transition(self) -> None:
        logs: List[str] = []
        with patch('netboot.cabinet.log', new_callable=lambda: lambda log, newline: logs.append(log)):
            cabinet, host = self.spawn_cabinet(state=CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_ON)
            host.alive = True

            cabinet.tick()
            self.assertTrue(cabinet.state[0], CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_OFF)
            self.assertEqual(["Cabinet 1.2.3.4 has no associated game, waiting for power off."], logs)

    def test_state_host_alive_game_transition(self) -> None:
        logs: List[str] = []
        with patch('netboot.cabinet.log', new_callable=lambda: lambda log, newline: logs.append(log)):
            cabinet, host = self.spawn_cabinet(
                state=CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_ON,
                filename="abc.bin",
            )
            host.alive = True

            cabinet.tick()
            self.assertTrue(cabinet.state[0], CabinetStateEnum.STATE_WAIT_FOR_CABINET_POWER_OFF)
            self.assertEqual(["Cabinet 1.2.3.4 sending game abc.bin."], logs)
            host.send.assert_called_with("abc.bin", [], {})
