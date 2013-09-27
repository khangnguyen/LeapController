################################################################################
# Author: Khang Nguyen                                                         #
# Written: September 2013                                                      #
################################################################################

import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from appscript import *
from osax import *

class ItunesListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"
        self.itunes = app('itunes')
        self.osax = OSAX()
        self.swipes = {}
    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        if not frame.hands.is_empty:
            # Gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    # Calculate the angle swept since the last frame
                    swept_angle = 0
                    if circle.state != Leap.Gesture.STATE_START:
                        previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                        swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                    print "Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                            gesture.id, self.state_string(gesture.state),
                            circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

                    volumeSettings = self.osax.get_volume_settings()
                    currentVolume = volumeSettings[k.output_volume]
                    # Max vlue volumeSettings returns is 100
                    # But max value set_volume takes is 7
                    currentVolume = currentVolume * 7.0 / 100
                    if clockwiseness == 'clockwise':
                        self.osax.set_volume(currentVolume + 0.1)
                    else:
                        self.osax.set_volume(currentVolume - 0.1)

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s" % (
                            gesture.id, self.state_string(gesture.state), swipe.position)
                    
                    if not self.swipes.get(gesture.id):
                        self.swipes[gesture.id] = {}
                    
                    gestures = self.swipes.get(gesture.id)
    
                    if self.state_string(gesture.state) == "STATE_START":
                        gestures['STATE_START'] = gesture
                    if self.state_string(gesture.state) == "STATE_STOP":                        
                        gestures['STATE_STOP'] = gesture
                    if gestures.get('STATE_START') and gestures.get('STATE_STOP'):
                        startGesture = SwipeGesture(gestures['STATE_START'])
                        stopGesture = SwipeGesture(gestures['STATE_STOP'])
                        if startGesture.position[0] - stopGesture.position[0] > 70:
                            self.itunes.next_track()
                        elif startGesture.position[0] - stopGesture.position[0] < -70:
                            self.itunes.previous_track()
                        print "START x", startGesture.position[0]
                        print "STOP x", stopGesture.position[0]
                    

                if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                    keytap = KeyTapGesture(gesture)
                    print "Key Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            keytap.position, keytap.direction )

                if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                    screentap = ScreenTapGesture(gesture)
                    print "Screen Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            screentap.position, screentap.direction )
                    playerState = self.itunes.player_state()
                    if playerState == k.playing:
                        self.itunes.pause()
                    if playerState == k.paused:
                        self.itunes.play()

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create an itunes listener and controller
    listener = ItunesListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
