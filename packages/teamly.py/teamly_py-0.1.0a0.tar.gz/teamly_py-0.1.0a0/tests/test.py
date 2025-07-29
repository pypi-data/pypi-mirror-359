import teamly

client = teamly.Client()

@client.event
async def on_ready():
    print("Ready!")

client.run("tly_083815ad4fd7ee2f.mbs5sqvm.m3jnkm305vf8h86q.1oh")
