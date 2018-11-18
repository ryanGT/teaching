import numpy as np

def create_fake_t(t):
    dt_vect = t[1:]-t[0:-1]
    dt = dt_vect.mean()
    N = len(t)
    nvect = np.arange(N)
    fake_t = dt*nvect
    return fake_t
