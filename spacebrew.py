import websocket
import threading
import json

typeMap = {
    "string" : basestring,
    "range" : int,
    "boolean" : bool
}

class SpaceBrew(object):
    # Define any runtime errors we'll need
    class ConfigurationError(Exception):
	def __init__(self, explanation):
	    self.explanation = explanation
	def __str__(self):
	    return repr(self.explanation)

    class TypeValidationError(Exception):
        def __init__(self, value, brewType):
            self.value = value
            self.brewType = brewType
        def __str__(self):
            return "{0} not of type {1} (python type {2})".format(self.value,self.brewType,type(self.value))

    class Slot(object):
        def validateType(self,brewType):
            if not brewType in typeMap.keys():
                raise SpaceBrew.ConfigurationError("Unrecognized type {0}".format(brewType))

        def validateValue(self, v):
            if not isinstance(v,typeMap[self.type]):
                raise SpaceBrew.TypeValidationError(value,self.type)

	def __init__(self, name, brewType, default = None):
	    self.name = name
	    self.type = brewType
            self.validateType(self.type)
	    self.value = None
            if default != None:
                validateValue(default)
	    self.default = default
	def makeConfig(self):
	    d = { 'name':self.name, 'type':self.type, 'default':self.default }
	    return d
		
    class Publisher(Slot):
	pass

    class Subscriber(Slot):
	def __init__(self, name, brewType, default = None):
	    super(SpaceBrew.Subscriber,self).__init__(name,brewType,default)
	    self.callbacks=[]
	def subscribe(self, target):
	    self.callbacks.append(target)
	def unsubscribe(self, target):
	    self.callbacks.remove(target)
	def disseminate(self, value):
	    for target in self.callbacks:
		target(value)

    def __init__(self, name, description="", server="sandbox.spacebrew.cc", port=9000):
	self.server = server
	self.port = port
	self.name = name
	self.description = description
	self.connected = False
	self.publishers = {}
	self.subscribers = {}

    def addPublisher(self, name, brewType="string", default=None):
	if self.connected:
	    raise SpaceBrew.ConfigurationError(self,"Can not add a new publisher to a running SpaceBrew instance (yet).")
	else:
	    self.publishers[name]=self.Publisher(name, brewType, default)
    
    def addSubscriber(self, name, brewType="string", default=None):
	if self.connected:
	    raise SpaceBrew.ConfigurationError(self,"Can not add a new subscriber to a running SpaceBrew instance (yet).")
	else:
	    self.subscribers[name]=self.Subscriber(name, brewType, default)

    def makeConfig(self):
	subs = map(lambda x:x.makeConfig(),self.subscribers.values())
	pubs = map(lambda x:x.makeConfig(),self.publishers.values())
	d = {'config':{
		'name':self.name,
		'description':self.description,
		'publish':{'messages':pubs},
		'subscribe':{'messages':subs},
		}}
	return d

    def on_open(self,ws):
	print "Opening brew."
	ws.send(json.dumps(self.makeConfig()))

    def on_message(self,ws,message):
	msg = json.loads(message)['message']
	sub=self.subscribers[msg['name']]
        try:
            sub.validateValue(msg['value'])
            sub.disseminate(msg['value'])
        except SpaceBrew.TypeValidationError as tve:
            print tve

    def on_error(self,ws,error):
	print "ERROR:",error

    def on_close(self,ws):
	print "Closing brew."

    def publish(self,name,value):
	publisher = self.publishers[name]
        publisher.validateValue(value)
	message = {'message': {
		'clientName':self.name,
		'name':publisher.name,
		'type':publisher.type,
		'value':value } }
	self.ws.send(json.dumps(message))

    def subscribe(self,name,target):
	subscriber = self.subscribers[name]
	subscriber.subscribe(target)

    # Retry indicates that if the connection drops
    # the brew should attempt to reconnect-- not yet
    # implemented
    def run(self,retry=False):
	ws = websocket.WebSocketApp("ws://{0}:{1}".format(self.server,self.port),
				    on_message = lambda ws, msg: self.on_message(ws, msg),
				    on_error = lambda ws, err: self.on_error(ws,err),
				    on_close = lambda ws: self.on_close(ws))
	self.ws = ws
	ws.on_open = lambda ws: self.on_open(ws)
	ws.run_forever()

    def start(self):
        def run(*args):
            self.run()
        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop(self):
	self.ws.close()
        self.thread.join()



if __name__ == "__main__":
    print """
This is the SpaceBrew module. 
See spacebrew_ex.py for usage examples.
"""
    
