class GameMsg(dict):
    def __init__(self, code=0, msg='Nothing.'):
        super().__init__()
        self['code'] = code
        self['msg'] = msg