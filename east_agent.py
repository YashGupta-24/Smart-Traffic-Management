from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from protocol import protocol
# import random
# import asyncio

# class AgentCall(Model):
#     display_time :int
#     status: bool

# class ControlRequest(Model):
#     calculated_time :int
    
east_agent = Agent(name="East Agent", seed="I am the east agent", port=8083, endpoint="http://localhost:8083/submit")

fund_agent_if_low(east_agent.wallet.address()) #type: ignore

east_agent.include(protocol)

# control_agent_address='agent1q07zrmw5pcnj0aktmsrdzyl6clp4h7xlddszdartfdezwmdyxjsl7v6ahdf'

# @east_agent.on_message(model = AgentCall)
# async def on_message(ctx:Context, sender: str, msg: AgentCall):
#     if msg.status ==True:
#         for i in range(msg.display_time, 0, -1):
#             ctx.logger.info(f"{i} GO")
#             await asyncio.sleep(1)
        
    
#     for i in range(msg.display_time, 0, -1):
#         ctx.logger.info(f"{i} STOP")
#         await asyncio.sleep(1)
#         if(i==0):
#             ctx.logger.info('I am scanning for the density of vehicles')
#             ctx.logger.info('I have send the data to llm, and the response will be saved to the time_for_next_cycle')
#     await ctx.send(sender, ControlRequest(calculated_time=random.randint(0,15)))

if __name__ == '__main__':
    east_agent.run()