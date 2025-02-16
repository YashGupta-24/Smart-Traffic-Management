from uagents import Context, Model, Protocol
import asyncio
import random

class AgentCall(Model):
    display_time :int
    status: bool

class ControlRequest(Model):
    calculated_time :int

protocol = Protocol()

@protocol.on_message(model = AgentCall)
async def on_message(ctx:Context, sender: str, msg: AgentCall):
    if msg.status == True:
        for i in range(msg.display_time, 0, -1):
            ctx.logger.info(f"{i} GO")
            await asyncio.sleep(1)
        
    for i in range(msg.display_time, 0, -1):
        ctx.logger.info(f"{i} STOP")
        await asyncio.sleep(1)
        if(i==0):
            ctx.logger.info('I am scanning for the density of vehicles')
            ctx.logger.info('I have send the data to llm, and the response will be saved to the time_for_next_cycle')
    await ctx.send(sender, ControlRequest(calculated_time=random.randint(10,60)))
