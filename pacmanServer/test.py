
class Observable:
    def __init__(self):
        super().__init__()
        self._observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
            return True
        return False

    def notify(self, msg):
        print(msg)
        for observer in self._observers:
            print("Observer")
            print(msg)
            print()
            observer.observe_callback(msg)

    def reset(self):
        del self._observers[:]

class Observer:
    def observe_callback(self,msg):
        pass

class Game(Observable):
    def __init__(self):
        super().__init__()
        print("init")

    def test(self,msg):
        self.notify(msg)

class Event(Observer):
    def observe_callback(self,msg):
        print("NOTIFY")
        print(msg)
        print()


spel = Game()
spel.register(Event())
spel.test("Test")
spel.test("1234")