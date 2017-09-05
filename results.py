class box_results():

    def __init__(self, box_id, things=True):
        self.box_id = box_id
        self.csv_array = []
        self.trialNum
        self.acceptSide
        self.seekSideSwaps
        self.numSideSwaps
        self.timeToAccept
        self.rejectTime
        self.acceptTime
        self.shockModeTime
        self.shockedTime

    def start(self):
        for x in range(10):
            self.csv_array.append()

    def change_box_id(self):
        self.box_id = 10