# -*- coding: utf-8 -*-

import scipy as sp
import scipy.special as spc
import scipy.signal as sig
import numpy as np

class SpectralSubtraction():
    def __init__(self,winsize,window,coefficient=5.0,ratio=1.0):
        self._window=window
        self._coefficient=coefficient
        self._ratio=ratio

    def compute(self,signal,noise):
        n_spec = sp.fft(noise*self._window)
        n_pow = sp.absolute(n_spec)**2.0
        return self.compute_by_noise_pow(signal,n_pow)

    def compute_by_noise_pow(self,signal,n_pow):
        s_spec = sp.fft(signal*self._window)
        s_amp = sp.absolute(s_spec)
        s_phase = sp.angle(s_spec)
        s_amp2 = s_amp**2.0
        amp = s_amp2 - n_pow*self._coefficient
        # amp = s_amp**2.0 - (1 + np.std(n_pow) / n_pow) * n_pow * 2
        
        amp = sp.maximum(amp, 0.01 * s_amp2)
        amp = sp.sqrt(amp)
        amp = self._ratio*amp + (1.0-self._ratio)*s_amp
        spec = amp * sp.exp(s_phase*1j)
        return sp.real(sp.ifft(spec))

class SpectrumReconstruction(object):
    def __init__(self,winsize,window,constant=0.001,ratio=1.0,alpha=0.99):
        self._window=window
        self._G = sp.zeros(winsize,sp.float32)
        self._prevGamma = sp.zeros(winsize,sp.float32)
        self._alpha = alpha
        self._prevAmp = sp.zeros(winsize,sp.float32)
        self._ratio=ratio
        self._constant=constant 

    def compute(self,signal,noise):
        n_spec = sp.fft(noise*self._window)
        n_pow = sp.absolute(n_spec)**2.0
        return self.compute_by_noise_pow(signal,n_pow)

    def _calc_aposteriori_snr(self,s_amp,n_pow):
        return s_amp**2.0/n_pow

    def _calc_apriori_snr(self,gamma):
        return self._alpha*self._G**2.0 * self._prevGamma + (1.0-self._alpha)*sp.maximum(gamma-1.0, 0.0)#a priori s/n ratio

    def _calc_apriori_snr2(self,gamma,n_pow):
        return self._alpha*(self._prevAmp**2.0/n_pow) + (1.0-self._alpha)*sp.maximum(gamma-1.0, 0.0)#a priori s/n ratio

class MMSE_STSA(SpectrumReconstruction):
    def __init__(self,winsize,window,constant=0.001,ratio=1.0,alpha=0.99):
        self._gamma15=spc.gamma(1.5)
        super(self.__class__,self).__init__(winsize,window,constant=constant,ratio=ratio,alpha=alpha)

    def compute_by_noise_pow(self,signal,n_pow):
        s_spec = sp.fft(signal*self._window)
        s_amp = sp.absolute(s_spec)
        s_phase = sp.angle(s_spec)
        gamma = self._calc_aposteriori_snr(s_amp,n_pow)
        xi = self._calc_apriori_snr(gamma)
        self._prevGamma = gamma
        nu = gamma * xi / (1.0+xi)
        self._G = (self._gamma15*sp.sqrt(nu)/gamma)*sp.exp(-nu/2.0)* ((1.0+nu)*spc.i0(nu/2.0)+nu*spc.i1(nu/2.0))
        idx = sp.less(s_amp**2.0,n_pow)
        self._G[idx] = self._constant
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = xi[idx] / ( xi[idx] + 1.0)
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = self._constant
        self._G = sp.maximum(self._G,0.0)
        amp = self._G * s_amp
        amp = sp.maximum(amp,0.0)
        amp2 = self._ratio*amp + (1.0-self._ratio)*s_amp
        self._prevAmp = amp
        spec = amp2 * sp.exp(s_phase*1j)
        return sp.real(sp.ifft(spec))


class MMSE_LogSTSA(SpectrumReconstruction):
    def __init__(self,winsize,window,constant=0.001,ratio=1.0,alpha=0.99):
        self._gamma15=spc.gamma(1.5)
        super(self.__class__,self).__init__(winsize,window,constant=constant,ratio=ratio,alpha=alpha)

    def compute_by_noise_pow(self,signal,n_pow):
        s_spec = sp.fft(signal*self._window)
        s_amp = sp.absolute(s_spec)
        s_phase = sp.angle(s_spec)
        gamma = self._calc_aposteriori_snr(s_amp,n_pow)
        xi = self._calc_apriori_snr(gamma)
        #xi = self._calc_apriori_snr2(gamma,n_pow)
        self._prevGamma = gamma
        nu = gamma * xi / (1.0+xi)
        self._G = xi/(1.0+xi)*sp.exp(0.5*spc.exp1(nu))
        self._G[np.isnan(self._G)] = 0
        idx = sp.less(s_amp**2.0,n_pow)
        self._G[idx] = self._constant
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = xi[idx] / ( xi[idx] + 1.0)
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = self._constant
        self._G = sp.maximum(self._G,0.0)
        amp = self._G * s_amp
        amp = sp.maximum(amp,0.0)
        amp2 = self._ratio*amp + (1.0-self._ratio)*s_amp
        self._prevAmp = amp
        spec = amp2 * sp.exp(s_phase*1j)
        return sp.real(sp.ifft(spec))

class JointMap(SpectrumReconstruction):
    def __init__(self,winsize,window,constant=0.001,ratio=1.0,alpha=0.99,mu=1.74,tau=0.126):
        self._mu = mu
        self._tau = tau
        super(self.__class__,self).__init__(winsize,window,constant=constant,ratio=ratio,alpha=alpha)

    def compute_by_noise_pow(self,signal,n_pow):
        s_spec = sp.fft(signal *self._window)
        s_amp = sp.absolute(s_spec)
        s_phase = sp.angle(s_spec)
        gamma = self._calc_aposteriori_snr(s_amp,n_pow)
        #xi = self._calc_apriori_snr2(gamma,n_pow)
        xi = self._calc_apriori_snr(gamma)
        self._prevGamma = gamma
        u = 0.5 - self._mu/(4.0*sp.sqrt(gamma*xi))
        self._G = u + sp.sqrt(u**2.0 + self._tau/(gamma*2.0))
        idx = sp.less(s_amp**2.0,n_pow)
        self._G[idx] = self._constant
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = xi[idx] / ( xi[idx] + 1.0)
        idx = sp.isnan(self._G) + sp.isinf(self._G)
        self._G[idx] = self._constant
        self._G = sp.maximum(self._G,0.0)
        amp = self._G * s_amp
        amp = sp.maximum(amp,0.0)
        amp2 = self._ratio*amp + (1.0-self._ratio)*s_amp
        self._prevAmp = amp
        spec = amp2 * sp.exp(s_phase*1j)
        return sp.real(sp.ifft(spec))


def get_frame(signal, winsize, no):
    shift=winsize/2
    start=no*shift
    end = start+winsize
    return signal[start:end]

def add_signal(signal, frame, winsize, no ):
    shift=winsize/2
    start=no*shift
    end=start+winsize
    signal[start:end] = signal[start:end] + frame
    
def reduce_noise(signal, noisy_signal, method, winsize=2**10, window=sp.hanning(2**10)):
    """ Reduce noise """
    if method == 'SS' or method == 0:
        method = SpectralSubtraction(winsize, window)    
    elif method == 'MMSE_STSA' or method == 1:
        method = MMSE_STSA(winsize, window)    
    elif method == 'MMSE_LogSTSA' or method == 2:
        method = MMSE_LogSTSA(winsize, window)
    elif method == 'JointMap' or method == 3:
        method = JointMap(winsize, window)        
    
    out = sp.zeros(len(signal),sp.float32)
    power = sig.welch(noisy_signal, window=window, return_onesided=False, scaling='spectrum')[1] * window.sum()**2
    nf = len(signal)/(winsize/2) - 1
    for no in xrange(nf):
        s = get_frame(signal, winsize, no)
        add_signal(out, method.compute_by_noise_pow(s, power), winsize, no)
    return out
    
def get_noise(signal, rate, intervals):
    interval = intervals.popitem()
    if interval[1][0] == 0:
        start = 0
    else:
        start = interval[1][0] + 3*rate
    end = interval[1][1] - rate
    return signal[start:end]
    
