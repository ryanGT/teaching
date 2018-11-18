import control
G_list = []


num0 = [1.,3.]
den0 = [ 1,-1,-6]
G0 = control.TransferFunction(num0,den0)
G_list.append(G0)
