from math import pi
from tqdm import tqdm
import jax.numpy as jnp
import time
import jax
from jax import grad, vmap

from ripple import get_eff_pads, get_match_arr
from ripple.waveforms import IMRPhenomD, IMRPhenomD_utils
from ripple.waveforms import IMRPhenomP
import matplotlib.pyplot as plt
from ripple.constants import gt, MSUN

#plt.style.use("../plot_style.mplstyle")
import numpy as np
import cProfile
import lalsimulation as lalsim
from ripple import ms_to_Mc_eta
import lal
dist_mpc = 100
m1_test = 20*10**30
m2_test = 21*10**30
f_ref = 30
phi_ref = 0.0
incl = 0.0
s1x = 0.0
s1y = 0.0
s1z = 0.0
s2x = 0.0
s2y = 0.0
s2z = 0.0
M = m1_test + m2_test
f_l= f_ref
f_u = 400
fs = np.arange(f_ref, f_u, 0.01)
#IMRPhenomP.PhenomPcore(m1_test, m2_test, f_ref, phi_ref, incl, s1x, s1y, s1z, s2x, s2y, s2z)
#phenom, phasing =IMRPhenomP.PhenomPOneFrequency(fs, m1_test/MSUN, m2_test/MSUN, s1z, s2z, phi_ref, M/MSUN)
chi1_l, chi2_l, chip, thetaJN, alpha0, phi_aligned, zeta_polariz =IMRPhenomP.LALtoPhenomP(m1_test, m2_test, f_ref, phi_ref, incl, s1x, s1y, s1z, s2x, s2y, s2z)
#print(chi1_l, chi2_l, chip, thetaJN, alpha0, phi_aligned, zeta_polariz)
#print(phenom, phasing)
#hps, hcs = IMRPhenomP.PhenomPcore(fs, m1_test, m2_test, f_ref, phi_ref, dist_mpc, incl, s1x, s1y, s1z, s2x, s2y, s2z)
hpsD,_ = IMRPhenomP.PhenomPOneFrequency(fs, m2_test/MSUN, m1_test/MSUN, chi2_l, chi1_l, phi_ref, (m1_test+m2_test)/MSUN, dist_mpc)

#phi_ripple = np.unwrap(np.angle(hps))

#print(hps)
distance = dist_mpc * 1e6 * lal.PC_SI

approximant = lalsim.SimInspiralGetApproximantFromString("IMRPhenomPv2")
hp, hc = lalsim.SimInspiralChooseFDWaveform(
    m1_test,
    m2_test,
    s1x,
    s1y,
    s1z,
    s2x,
    s2y,
    s2z,
    distance,
    np.pi/2,
    phi_ref,
    0.0,
    0.0,
    0.0,
    0.01,
    f_ref,
    f_u,
    f_ref,
    None,
    approximant,
)

m1 = m1_test / MSUN
m2 = m2_test / MSUN
q = m2 / m1 # q>=1 
M = m1 + m2
chi_eff = (m1*chi1_l + m2*chi2_l) / M
chil = (1.0+q)/q * chi_eff

freq = np.arange(len(hp.data.data)) * 0.01
f_mask = (freq >= f_l) & (freq < f_u)
#plt.plot(fs, hcs, "--", label="ripple_hcs")
#plt.plot(fs, hcsD, "--", label="ripple_hcsD")
plt.plot(fs, hpsD, "--", label="ripple_hps")
print(hpsD)
#plt.plot(fs, hps/hpsD, "--", label="ripple_hpsD",alpha=0.5)
#print(hps[-1])
plt.plot(
    freq[f_mask], 2.0*hp.data.data[f_mask], label="lalsuite"
)
phi_lal = np.unwrap(np.angle(hp.data.data))[f_mask]

#plt.plot(fs, phi_lal-phi_ripple)
#print(phi_lal-phi_python)
#print(hp.data.data[f_mask])
plt.legend()
plt.show()
thetaJN = 0.58763
Y2m2 = IMRPhenomP.SpinWeightedY(thetaJN, 0 , -2, 2, -2)
Y2m1 = IMRPhenomP.SpinWeightedY(thetaJN, 0 , -2, 2, -1)
Y20 = IMRPhenomP.SpinWeightedY(thetaJN, 0 , -2, 2, -0)
Y21 = IMRPhenomP.SpinWeightedY(thetaJN, 0 , -2, 2, 1)
Y22 = IMRPhenomP.SpinWeightedY(thetaJN, 0 , -2, 2, 2)
Y2 = [Y2m2, Y2m1, Y20, Y21, Y22]

#A_test = jnp.array([1+2j, 4+5j, 3-0.3j])

angcoeffs = IMRPhenomP.ComputeNNLOanglecoeffs(q, chil, chip)
hp,hc = IMRPhenomP.PhenomPCoreTwistUp(100, 1, 0.25, 0.0, 0.0, 0.0, 1, angcoeffs, Y2, 0, 0)
print(hp, hc)
#A_trans = jnp.array(A_trans)
#print(A_trans/A_test)