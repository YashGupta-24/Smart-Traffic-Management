from uagents import Agent, Model, Context
from uagents.setup import fund_agent_if_low
import asyncio

class AgentCall(Model):
    display_time :int
    status: bool

class ControlRequest(Model):
    calculated_time :int

control_agent = Agent(name='Control Agent', seed="I am the Control Agent", port=8080, endpoint="http://localhost:8080/submit")

fund_agent_if_low(control_agent.wallet.address()) #type: ignore

north_agent_address='agent1qda55m3247g8dm3nlkch7grg4jcecmhucy0sh5c0xq4z0stqlth7xuap7wv'
south_agent_address='agent1q0xdz5c9hw5wr0wqdsfe63mqzf66jwwa27sx5x3dcg8q6r65hskuxxv6upu'
east_agent_address='agent1q03krptv4w778hhf7u80g4k4au2j9p3nlzsh8s95u6hx4ezwux65xag7eua'
west_agent_address='agent1qgl3d04c7lq4pn2fd3ln6pjvdvnzx7qmhhkysaj4z64wszslxjjgq4n8zfr'

lower_time_limit=20
upper_time_limit=50

@control_agent.on_event('startup')
async def initialize(ctx: Context):
    # Initialize with East-West green, North-South red
    ctx.storage.set('agent_statuses', {
        'north': False,  # red
        'south': False,  # red
        'east': True,   # green
        'west': True    # green
    })
    
    # Send initial signals
    await send_signals_to_all_agents(ctx, lower_time_limit)
    ctx.logger.info('Initialization complete')

async def send_signals_to_all_agents(ctx: Context, display_time: int):
    agent_status = ctx.storage.get('agent_statuses')
    if agent_status is None:
        agent_status = {'north': False, 'south': False, 'east': True, 'west': True}
        ctx.storage.set('agent_statuses', agent_status)

    # Send signals to all agents simultaneously
    await asyncio.gather(
        ctx.send(north_agent_address, AgentCall(display_time=display_time, status=agent_status['north'])),
        ctx.send(south_agent_address, AgentCall(display_time=display_time, status=agent_status['south'])),
        ctx.send(east_agent_address, AgentCall(display_time=display_time, status=agent_status['east'])),
        ctx.send(west_agent_address, AgentCall(display_time=display_time, status=agent_status['west']))
    )

@control_agent.on_message(model=ControlRequest)
async def on_agent_call(ctx: Context, sender: str, msg: ControlRequest):
    try:
        display_times = ctx.storage.get('display_times')
        if display_times is None:
            display_times = []
        
        ctx.logger.info(f"Display time: {msg.calculated_time} from agent: {sender}")
        display_times.append(msg.calculated_time)
        ctx.storage.set('display_times', display_times)

        # Wait for responses from all agents before switching
        if len(display_times) == 2:  # All agents have responded
            # Calculate next timing
            max_time = max(display_times)
            next_time = max_time
            
            # Clamp time between limits
            if next_time > upper_time_limit:
                next_time = upper_time_limit
            elif next_time < lower_time_limit:
                next_time = lower_time_limit

            # Switch signal states
            agent_status = ctx.storage.get('agent_statuses')
            new_status = {
                'north': not agent_status['north'], # type: ignore
                'south': not agent_status['north'],  # Keep in sync with north # type: ignore
                'east': not agent_status['east'], # type: ignore
                'west': not agent_status['east']     # Keep in sync with east # type: ignore
            }
            ctx.storage.set('agent_statuses', new_status)
            # Send new signals to all agents
            await send_signals_to_all_agents(ctx, next_time)
        
            ctx.storage.set('display_times', [])

    except Exception as e:
        ctx.logger.error(f'Error in processing agent response: {str(e)}')

if __name__ == '__main__':
    control_agent.run()