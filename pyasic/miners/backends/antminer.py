# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

import logging
from pathlib import Path
from typing import List, Optional

from pyasic.config import MinerConfig, MiningModeConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRate
from pyasic.errors import APIError
from pyasic.miners.backends.bmminer import BMMiner
from pyasic.miners.backends.cgminer import CGMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.rpc.antminer import AntminerRPCAPI
from pyasic.ssh.antminer import AntminerModernSSH
from pyasic.web.antminer import AntminerModernWebAPI, AntminerOldWebAPI

ANTMINER_MODERN_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_get_blink_status", "get_blink_status")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_get_conf", "get_miner_conf")],
        ),
        str(DataOptions.IS_SLEEP): DataFunction(
            "_is_sleep",
            [],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class AntminerModern(BMMiner):
    """Handler for AntMiners with the modern web interface, such as S19"""

    _web_cls = AntminerModernWebAPI
    web: AntminerModernWebAPI

    _rpc_cls = AntminerRPCAPI
    rpc: AntminerRPCAPI

    _ssh_cls = AntminerModernSSH
    ssh: AntminerModernSSH

    data_locations = ANTMINER_MODERN_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_am_modern(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_am_modern(user_suffix=user_suffix))
        # if data:
        #     if data.get("code") == "M000":
        #         return
        #
        # for i in range(7):
        #     data = await self.get_config()
        #     if data == self.config:
        #         break
        #     await asyncio.sleep(1)

    async def upgrade_firmware(self, file: Path, keep_settings: bool = True) -> str:
        """
        Upgrade the firmware of the AntMiner device.

        Args:
            file (Path): Path to the firmware file.
            keep_settings (bool): Whether to keep the current settings after the update.

        Returns:
            str: Result of the upgrade process.
        """
        if not file:
            raise ValueError("File location must be provided for firmware upgrade.")

        try:
            result = await self.web.update_firmware(
                file=file, keep_settings=keep_settings
            )

            if result.get("success"):
                logging.info(
                    "Firmware upgrade process completed successfully for AntMiner."
                )
                return "Firmware upgrade completed successfully."
            else:
                error_message = result.get("message", "Unknown error")
                logging.error(f"Firmware upgrade failed. Response: {error_message}")
                return f"Firmware upgrade failed. Response: {error_message}"
        except Exception as e:
            logging.error(
                f"An error occurred during the firmware upgrade process: {e}",
                exc_info=True,
            )
            raise

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            if data.get("code") == "B000":
                self.light = True
        return self.light

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            if data.get("code") == "B100":
                self.light = False
        return self.light

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def update_pwd(self, cur_pwd: str, new_pwd: str) -> bool:
        data = await self.web.update_pwd(cur_pwd=cur_pwd, new_pwd=new_pwd)
        if data:
            if data.get("code") == "P000":
                return True
        return False

    async def stop_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.sleep()
        await self.send_config(cfg)
        return True

    async def resume_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.normal()
        await self.send_config(cfg)
        return True

    async def _get_hostname(self, web_get_system_info: dict = None) -> Optional[str]:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return web_get_system_info["hostname"]
            except KeyError:
                pass

    async def _get_mac(self, web_get_system_info: dict = None) -> Optional[str]:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return web_get_system_info["macaddr"]
            except KeyError:
                pass

        try:
            data = await self.web.get_network_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def _get_errors(self, web_summary: dict = None) -> List[MinerErrorData]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        errors = []
        if web_summary is not None:
            try:
                for item in web_summary["SUMMARY"][0]["status"]:
                    try:
                        if not item["status"] == "s":
                            errors.append(X19Error(error_message=item["msg"]))
                    except KeyError:
                        continue
            except LookupError:
                pass
        return errors

    async def _get_hashboards(self) -> List[HashBoard]:
        boards_list = []
        try:
            rpc_stats = await self.rpc.stats(new_api=True)
        except APIError:
            # Если данные не получены, возвращаем пустой список
            return boards_list

        if not rpc_stats:
            return boards_list

        try:
            # Извлекаем информацию по платам из цепочки
            chain = rpc_stats.get("STATS", [])[0].get("chain", [])
            for board in chain:
                # Если по каким-то причинам отсутствует индекс – пропускаем запись
                if "index" not in board:
                    continue

                # Создаём базовый объект hashboard с указанным индексом и ожидаемым числом чипов
                hb = HashBoard(
                    slot=board["index"],
                    expected_chips=self.expected_chips,
                    missing=True  # будем помечать как "не найденную" до успешного заполнения данных
                )

                # Заполняем hashrate, если доступен
                if "rate_real" in board and board["rate_real"] is not None:
                    hb.hashrate = self.algo.hashrate(
                        rate=board["rate_real"], unit=self.algo.unit.GH
                    ).into(self.algo.unit.default)

                # Заполняем число ASIC'ов (чипов), если данные есть
                if "asic_num" in board and board["asic_num"] is not None:
                    hb.chips = board["asic_num"]

                # Температура PCB (если присутствуют ненулевые значения)
                temp_pcb = board.get("temp_pcb")
                if temp_pcb:
                    valid_temps = [temp for temp in temp_pcb if temp != 0]
                    if valid_temps:
                        hb.temp = sum(valid_temps) / len(valid_temps)

                # Температура чипов (если присутствуют ненулевые значения)
                temp_chip = board.get("temp_chip")
                if temp_chip:
                    valid_chip_temps = [temp for temp in temp_chip if temp != 0]
                    if valid_chip_temps:
                        hb.chip_temp = sum(valid_chip_temps) / len(valid_chip_temps)

                # Серийный номер, если он присутствует
                if "sn" in board:
                    hb.serial_number = board["sn"]

                # Если хотя бы одно из ключевых полей получено (например, hashrate или chips),
                # считаем, что данные по плате имеются, и помечаем, что плата не отсутствует.
                if hb.hashrate is not None or hb.chips is not None:
                    hb.missing = False

                # Добавляем плату в список только если данные получены (т.е. плата не помечена как missing)
                if not hb.missing:
                    boards_list.append(hb)
        except Exception:
            # При ошибке обработки возвращаем те платы, которые уже удалось собрать
            return boards_list

        return boards_list

    async def _get_fault_light(
        self, web_get_blink_status: dict = None
    ) -> Optional[bool]:
        if self.light:
            return self.light

        if web_get_blink_status is None:
            try:
                web_get_blink_status = await self.web.get_blink_status()
            except APIError:
                pass

        if web_get_blink_status is not None:
            try:
                self.light = web_get_blink_status["blink"]
            except KeyError:
                pass
        return self.light

    async def _get_expected_hashrate(
        self, rpc_stats: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                expected_rate = rpc_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = rpc_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                return self.algo.hashrate(
                    rate=float(expected_rate), unit=self.algo.unit.from_str(rate_unit)
                ).into(self.algo.unit.default)
            except LookupError:
                pass

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
        hostname: str = None,
    ):
        if not hostname:
            hostname = await self.get_hostname()
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=2,
        )

    async def set_dhcp(self, hostname: str = None):
        if not hostname:
            hostname = await self.get_hostname()
        await self.web.set_network_conf(
            ip="", dns="", gateway="", subnet_mask="", hostname=hostname, protocol=1
        )

    async def set_hostname(self, hostname: str):
        cfg = await self.web.get_network_info()
        dns = cfg["conf_dnsservers"]
        gateway = cfg["conf_gateway"]
        ip = cfg["conf_ipaddress"]
        subnet_mask = cfg["conf_netmask"]
        protocol = 1 if cfg["conf_nettype"] == "DHCP" else 2
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=protocol,
        )

    async def _is_mining(self, web_get_conf: dict = None) -> Optional[bool]:
        if web_get_conf is None:
            try:
                web_get_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_conf is not None:
            try:
                if str(web_get_conf["bitmain-work-mode"]).isdigit():
                    return (
                        False if int(web_get_conf["bitmain-work-mode"]) == 1 else True
                    )
                return False
            except LookupError:
                pass

    async def _is_sleep(self, web_get_conf: dict = None) -> Optional[bool]:
        if web_get_conf is None:
            try:
                web_get_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_conf is not None:
            try:
                if str(web_get_conf["bitmain-work-mode"]).isdigit():
                    return (
                        True if int(web_get_conf["bitmain-work-mode"]) == 1 else False
                    )
                return False
            except LookupError:
                pass

    async def _get_uptime(self, rpc_stats: dict = None) -> Optional[int]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return int(rpc_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass

    async def _get_pools(self, rpc_pools: dict = None) -> List[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for pool_info in pools:
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        get_failures=pool_info.get("Get Failures"),
                        remote_failures=pool_info.get("Remote Failures"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=pool_info.get("POOL"),
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data


ANTMINER_OLD_DATA_LOC = DataLocations(
    **{
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_get_blink_status", "get_blink_status")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_get_conf", "get_miner_conf")],
        ),
        str(DataOptions.IS_SLEEP): DataFunction(
            "_is_sleep",
            [WebAPICommand("web_get_conf", "get_miner_conf")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class AntminerOld(CGMiner):
    """Handler for AntMiners with the old web interface, such as S17"""

    _web_cls = AntminerOldWebAPI
    web: AntminerOldWebAPI

    data_locations = ANTMINER_OLD_DATA_LOC

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_am_old(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_am_old(user_suffix=user_suffix))

    async def _get_mac(self) -> Optional[str]:
        try:
            data = await self.web.get_system_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def fault_light_on(self) -> bool:
        # this should time out, after it does do a check
        await self.web.blink(blink=True)
        try:
            data = await self.web.get_blink_status()
            if data:
                if data["isBlinking"]:
                    self.light = True
        except KeyError:
            pass
        return self.light

    async def fault_light_off(self) -> bool:
        await self.web.blink(blink=False)
        try:
            data = await self.web.get_blink_status()
            if data:
                if not data["isBlinking"]:
                    self.light = False
        except KeyError:
            pass
        return self.light

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def _get_fault_light(
        self, web_get_blink_status: dict = None
    ) -> Optional[bool]:
        if self.light:
            return self.light

        if web_get_blink_status is None:
            try:
                web_get_blink_status = await self.web.get_blink_status()
            except APIError:
                pass

        if web_get_blink_status is not None:
            try:
                self.light = web_get_blink_status["isBlinking"]
            except KeyError:
                pass
        return self.light

    async def _get_hostname(self, web_get_system_info: dict = None) -> Optional[str]:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return web_get_system_info["hostname"]
            except KeyError:
                pass

    async def _get_fans(self, rpc_stats: dict = None) -> List[Fan]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        fans_data = [Fan() for _ in range(self.expected_fans)]
        if rpc_stats is not None:
            try:
                fan_offset = -1

                for fan_num in range(1, 8, 4):
                    for _f_num in range(4):
                        f = rpc_stats["STATS"][1].get(f"fan{fan_num + _f_num}")
                        if f and not f == 0 and fan_offset == -1:
                            fan_offset = fan_num + 2
                if fan_offset == -1:
                    fan_offset = 3

                for fan in range(self.expected_fans):
                    fans_data[fan].speed = rpc_stats["STATS"][1].get(
                        f"fan{fan_offset+fan}", 0
                    )
            except LookupError:
                pass
        return fans_data

    async def _get_hashboards(self, rpc_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                board_offset = -1
                boards = rpc_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    for i in range(
                        board_offset, board_offset + self.expected_hashboards
                    ):
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.expected_chips
                        )

                        chip_temp = boards[1].get(f"temp{i}")
                        if chip_temp:
                            hashboard.chip_temp = round(chip_temp)

                        temp = boards[1].get(f"temp2_{i}")
                        if temp:
                            hashboard.temp = round(temp)

                        hashrate = boards[1].get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = self.algo.hashrate(
                                rate=float(hashrate), unit=self.algo.unit.GH
                            ).into(self.algo.unit.default)

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except LookupError:
                return [
                    HashBoard(slot=i, expected_chips=self.expected_chips)
                    for i in range(self.expected_hashboards)
                ]

        return hashboards

    async def _is_mining(self, web_get_conf: dict = None) -> Optional[bool]:
        if web_get_conf is None:
            try:
                web_get_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_conf is not None:
            try:
                return False if int(web_get_conf["bitmain-work-mode"]) == 1 else True
            except LookupError:
                pass

        rpc_summary = None
        try:
            rpc_summary = await self.rpc.summary()
        except APIError:
            pass

        if rpc_summary is not None:
            if not rpc_summary == {}:
                return True
            else:
                return False

    async def _is_sleep(self, web_get_conf: dict = None) -> bool:
        """
        Определяет, находится ли майнер в режиме "sleep" на основе параметра "bitmain-work-mode".

        Если значение "bitmain-work-mode" равно 1, возвращается True, иначе False.
        В случае ошибки получения конфигурации или отсутствия нужного ключа возвращается False.

        :param web_get_conf: (необязательный) словарь с конфигурацией майнера.
        :return: True, если режим равен 1, иначе False.
        """
        # if web_get_conf is None:
        #     try:
        #         web_get_conf = await self.web.get_miner_conf()
        #     except APIError:
        #         return False
        #
        # try:
        #     mode_str = str(web_get_conf["bitmain-work-mode"])
        #     if mode_str.isdigit():
        #         mode = int(mode_str)
        #         return True if mode == "1" else False
        #     return False
        # except (KeyError, LookupError, ValueError):
        #     return False
        return True

    async def _get_uptime(self, rpc_stats: dict = None) -> Optional[int]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return int(rpc_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass
