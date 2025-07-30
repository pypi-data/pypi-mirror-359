__copyright__ = """
Copyright (C)  2022 Rage Uday Kiran

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd
from PAMI.extras.dbStats.TransactionalDatabase import TransactionalDatabase
from PAMI.correlatedPattern.basic import CoMinePlus
from .abstract import PatternMiner
from typing import Union

class CorrelatedPatternMining(PatternMiner):
    def _create_database(self):
        return TransactionalDatabase(self.inputFile)

    def run(self, minSupport: int, minAllConf: Union[int, float]):
        self.miner = CoMinePlus.CoMinePlus(iFile=self.inputFile, minSup=minSupport, minAllConf=minAllConf)
        self.miner.mine()
        self.miner.printResults()