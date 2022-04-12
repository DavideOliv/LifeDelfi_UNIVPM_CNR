import numpy as np
import scipy.signal as sg
import scipy.stats as st
import json


class Layer:
    """
    Interfaccia, da non usare direttamente
    """
    # DA OVERRIDARE NELLE SOTTOCLASSI
    def process(self, data: np.ndarray):
        """
        data: np.ndarray spezzone di segnale da processare

        Ritorna:
        result: bool risultato elaborazione
        elab_data: dati output elaborazione
        """
        pass


class FilterLayer(Layer):
    """
    Layer che applica un filtro passa alto o passa banda al chunk
    """
    def __init__(self, type: str, band, sr):
        """
        Vedi scipy.signal.butter per la documentazione sui parametri
        """
        self.filter = sg.butter(N=4, Wn=band, btype=type,
                                analog=False, output='sos', fs=sr)
        self.props = {
            "filterJson": json.dumps({
                "filter_type": type,
                "band": band
            })
        }

    def process(self, data: np.ndarray) -> tuple[bool, np.ndarray, dict]:
        return True, sg.sosfilt(self.filter, data), self.props


class PeaksLayer(Layer):
    """
    Layer che tramite la funzione scipy.signal.find_peaks trova i picchi nel chunk
    """
    def __init__(self, threshold: float, distance: int, min_num_peaks: int):
        self.threshold = threshold
        self.distance = distance
        self.min_num_peaks = min_num_peaks

    def process(self, data: np.ndarray) -> tuple[bool, np.ndarray, dict]:
        ss = data - np.mean(data)
        nn = np.sqrt(np.mean(np.square(ss)))
        snr = np.abs(ss) / nn

        peaks, peak_props = sg.find_peaks(
            snr, height=self.threshold, distance=self.distance)
        result = peaks.shape[0] >= self.min_num_peaks

        props = {
            "nPeaks": peaks.shape[0],
            "action": str(result),
            "levelMax": None,
            "levelMin": None,
            "classification": "click" if result else "noise"
        }

        if peaks.shape[0]>0:
            props["levelMax"] = np.max(peak_props["peak_heights"])
            props["levelMin"] = np.min(peak_props["peak_heights"])

        return result, peaks, props


class PeaksVarianceLayer(Layer):
    """
    Layer che calcola statistiche sui picchi del layer PeaksLayer e effettua un test chi2
    """
    def __init__(self, sigma_0: float, alpha: float):
        self.alpha = alpha
        self.sigma_0_2 = sigma_0**2

    def process(self, peaks: np.ndarray):
        peaks_dist = np.diff(peaks)
        df = peaks.shape[0] - 1
        std = float(np.std(peaks_dist))
        mean = float(np.mean(peaks_dist))
        min=float(np.min(peaks_dist))
        max=float(np.max(peaks_dist))

        chi_test = (std ** 2) * df / (self.sigma_0_2)
        pval = st.chi2.sf(chi_test, df)
        result = pval < self.alpha

        props = {
            "statisticsJson": json.dumps({
                "dists_min": min,
                "dists_max": max,
                "dists_mean": mean,
                "dists_std": std,
                "chi_test": chi_test,
                "chi_pval": pval
            })
        }

        return result, None, props
