from uagents import Agent, Model, Context
from uagents.setup import fund_agent_if_low

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
    ctx.storage.set('agent_statuses',{'north':False, 'south':False, 'east':True, 'west':True})

    agent_status = ctx.storage.get('agent_statuses')
    if agent_status is None:
        agent_status = {'north':False,'south':False, 'east':True, 'west':True}
        ctx.storage.set('agent_statuses', agent_status)
    
    await ctx.send(north_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['north']))
    await ctx.send(south_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['south']))
    await ctx.send(east_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['east']))
    await ctx.send(west_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['west']))

    ctx.logger.info('Initialization complete')

    agent_status['north']=not agent_status['north']
    agent_status['south']=not agent_status['south']
    agent_status['east']=not agent_status['east']
    agent_status['west']=not agent_status['west']

    ctx.storage.set('agent_statuses', agent_status)
    ctx.storage.set('display_times',[])

@control_agent.on_message(model = ControlRequest)
async def on_agent_call(ctx:Context, sender: str, msg: ControlRequest):
    try:
        display_time = ctx.storage.get('display_times')

        if display_time is None:
            display_time = []
        else:
            ctx.logger.info(f"Display time: {msg.calculated_time} from agent: {sender}")
            display_time.append(msg.calculated_time)
            ctx.storage.set('display_times', display_time)

    except:
        ctx.logger.error('Error in storing display times')
    
    if display_time is not None and len(display_time) == 2:

        display_time.sort()
        ctx.storage.set('display_times', display_time)
        agent_status = ctx.storage.get('agent_statuses')

        if agent_status is None:
            agent_status = {'north':False,'south':False, 'east':True, 'west':True}
            ctx.storage.set('agent_statuses', agent_status)

        if display_time[-1]>upper_time_limit:
            await ctx.send(north_agent_address, AgentCall(display_time=upper_time_limit, status=agent_status['north']))
            await ctx.send(south_agent_address, AgentCall(display_time=upper_time_limit, status=agent_status['south']))
            await ctx.send(east_agent_address, AgentCall(display_time=upper_time_limit, status=agent_status['east']))
            await ctx.send(west_agent_address, AgentCall(display_time=upper_time_limit, status=agent_status['west']))
        
        elif display_time[-1]<lower_time_limit:
            await ctx.send(north_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['north']))
            await ctx.send(south_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['south']))
            await ctx.send(east_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['east']))
            await ctx.send(west_agent_address, AgentCall(display_time=lower_time_limit, status=agent_status['west']))
        
        else:
            await ctx.send(north_agent_address, AgentCall(display_time=display_time[-1], status=agent_status['north']))
            await ctx.send(south_agent_address, AgentCall(display_time=display_time[-1], status=agent_status['south']))
            await ctx.send(east_agent_address, AgentCall(display_time=display_time[-1], status=agent_status['east']))
            await ctx.send(west_agent_address, AgentCall(display_time=display_time[-1], status=agent_status['west']))

        agent_status['north']=not agent_status['north']
        agent_status['south']=not agent_status['south']
        agent_status['east']=not agent_status['east']
        agent_status['west']=not agent_status['west']

        ctx.storage.set('agent_statuses', agent_status)
        ctx.storage.set('display_times',[])

if __name__ == '__main__':
    control_agent.run()