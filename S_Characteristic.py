from pybleno import Characteristic


class S_Characteristic(Characteristic):

    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['notify'],
            'value': None
        })

        self._value = str(0).encode()
        self._updateValueCallback = None

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('S_Characteristic - onSubscribe')

        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('S_Characteristic - onUnsubscribe')

        self._updateValueCallback = None
