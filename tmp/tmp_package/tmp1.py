


class A:
    def __init__(self):
        pass

    def fire_event(self):
        from tmp.tmp import CheckboxEvent
        event = CheckboxEvent()
        event.fire()