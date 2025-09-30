import time

class SignalController:
    def __init__(self, initial_green='NS', green_duration=15):
        self.current_state = initial_green
        self.green_duration = green_duration
        self.remaining = green_duration
        self.last_switch = time.time()
        self.forced_state = None
        self.forced_until = None

    def force_state(self, state, duration=30):
        self.forced_state = state
        self.forced_until = time.time() + duration
        self.current_state = state
        self.last_switch = time.time()
        self.remaining = duration

    def reset_auto(self):
        self.forced_state = None
        self.forced_until = None
        self.last_switch = time.time()

    def compute_scores(self, counts):
        ns = counts.get('N',0) + counts.get('S',0)
        ew = counts.get('E',0) + counts.get('W',0)
        score_ns = ns * 1
        score_ew = ew * 1
        if counts.get('ambulance',0) > 0:
            score_ns += 1000
        return score_ns, score_ew

    def update(self, counts):
        now = time.time()
        if self.forced_state is not None:
            if self.forced_until is None or now < self.forced_until:
                self.current_state = self.forced_state
                self.remaining = max(0, int(self.forced_until - now)) if self.forced_until else self.green_duration
                return
            else:
                self.reset_auto()
        elapsed = now - self.last_switch
        if counts.get('accident', False):
            self.remaining = max(self.remaining, 30)
            self.last_switch = now
            return
        score_ns, score_ew = self.compute_scores(counts)
        if elapsed > self.green_duration:
            self.last_switch = now
            if score_ns >= score_ew:
                self.current_state = 'NS'
            else:
                self.current_state = 'EW'
            self.remaining = self.green_duration
        self.remaining = max(0, int(self.green_duration - (time.time() - self.last_switch)))
