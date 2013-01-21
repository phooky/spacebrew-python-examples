#!/usr/bin/python
import time

from spacebrew import SpaceBrew

# Construct a brew by passing in its name and the server you
# want to connect to.
brew1 = SpaceBrew("first brew",server="localhost")
# This brew will publish a string called "pub".
brew1.addPublisher("pub1","range")
brew1.addPublisher("pub2","boolean")
brew1.addPublisher("pub3")

# Construct a second brew, connecting to the same server.
brew2 = SpaceBrew("second brew",server="localhost")
# This brew will subscribe to a string called "sub".
brew2.addSubscriber("sub1","range")
brew2.addSubscriber("sub2","boolean")
brew2.addSubscriber("sub3")

# For any subscriber, you can define any number of functions
# that will get called with the sent value when a message arrives.
# Here's a simple example of a function that recieves a value.
def example(value):
    print "Got",value,type(value)
# We call "subscribe" to associate a function with a subscriber.
brew2.subscribe("sub1",example)
brew2.subscribe("sub2",example)
brew2.subscribe("sub3",example)

# Calling start on a brew starts it running in a separate thread.
brew1.start()
brew2.start()

# We'll publish a value every three seconds. While this is running,
# go to your admin interface and connect the subscriber to the publisher
# to see the values.
try:
    while True:
        time.sleep(3)
        # The publish method sends a value from the specified
        # publisher.
        brew1.publish('pub1',50)
        brew1.publish('pub2',True)
        brew1.publish('pub3','text')
except (KeyboardInterrupt, SystemExit) as e:
    # Calling stop on a brew disconnects it and waits for its
    # associated thread to finish.
    brew1.stop()
    brew2.stop()

