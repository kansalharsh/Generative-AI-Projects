from livekit.agents import Agent, function_tool, RunContext
import enum
from typing import Annotated
import logging
#from db_driver import DatabaseDriver

"""
#### To be added later####
logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"

########################################################
 """   

class AssistantFnc(Agent):
    def __init__(self, instructions: str, welcome_message: str = ""):
        super().__init__(instructions=instructions)
        self.welcome_message = welcome_message
        # Initialize car details
        # self._car_details = {
        #     CarDetails.VIN: "",
        #     CarDetails.Make: "",
        #     CarDetails.Model: "",
        #     CarDetails.Year: ""
        # }
    
    async def on_enter(self) -> None:
        """Called when the agent becomes active in a session."""
        if self.welcome_message:
            await self.session.generate_reply(instructions=self.welcome_message)
    
