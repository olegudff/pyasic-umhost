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

from enum import Enum


class MinerMake(str, Enum):
    WHATSMINER = "Whatsminer"
    ANTMINER = "Antminer"
    AVALONMINER = "Avalonminer"
    INNOSILICON = "Innosilicon"
    GOLDSHELL = "Goldshell"
    AURADINE = "Auradine"
    EPIC = "ePIC"
    BITAXE = "BitAxe"
    LUCKYMINER = "Luckyminer"
    ICERIVER = "IceRiver"
    HAMMER = "Hammer"
    VOLCMINER = "Volcminer"
    ELPHAPEX = "Elphapex"
    BRAIINS = "Braiins"

    def __str__(self):
        return self.value
