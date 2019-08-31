_id = ['1', '2', '3','4']
transport = ['http','tcp','https','dns']
agent = ['10.10.1.1','10.10.1.2','10.10.1.3','10.10.1.4']
username = ['DESKTOP-123\\user','root','blackleitus','user']
os = ['windows/amd64','linux/amd64','windows/amd64','linux/amd64']
seen = ['2019-08-31 13:10:08','2019-08-31 13:10:08','2019-08-31 13:10:08','2019-08-31 13:10:08']
titles = ['ID', 'Transport', 'Agent', 'Username','Operating System','Last Seen']
data = [titles] + list(zip(_id, transport, agent, username,os,seen))

def sessions():
	print("\t")
	for i, d in enumerate(data):
		line = f'{str(d[0]).ljust(18)}| {"| ".join(str(x).ljust(17) for x in d if d.index(x) > 0)}'
		print(line)
		if i == 0:
			sep = '-' * 18 + '+'
			line = ''.join(sep for x in d)
			print(line)
	print("\t")
