import numpy as np
from PySide6 import QtCore
import pyqtgraph as pg
from sympy.physics.quantum.gate import normalized


class TimeDomainGraphs:
    def __init__(self):
        # Set up three PyQtGraph plot widgets
        self.signal_plot = pg.PlotWidget()
        self.reconstruction_plot = pg.PlotWidget()
        self.difference_plot = pg.PlotWidget()

        self.original_pen = pg.mkPen(color='b', width=2)
        self.reconstruction_pen = pg.mkPen(color='g', width=2)
        self.difference_pen = pg.mkPen(color='r', width=2, style=QtCore.Qt.DashLine)

        # Set titles and labels
        self.signal_plot.setTitle("Signal Plot")
        self.signal_plot.setLabel("bottom", "Time", units="s")
        self.signal_plot.setLabel("left", "Amplitude")

        self.reconstruction_plot.setTitle("Reconstruction Plot")
        self.reconstruction_plot.setLabel("bottom", "Time", units="s")
        self.reconstruction_plot.setLabel("left", "Amplitude")

        self.difference_plot.setTitle("Difference Plot")
        self.difference_plot.setLabel("bottom", "Time", units="s")
        self.difference_plot.setLabel("left", "Amplitude")
        self.difference_plot_legend = pg.LegendItem(offset=(-10, 2))
        self.difference_plot_legend.setParentItem(self.difference_plot.plotItem)

        # Link the plots for synchronized panning and zooming
        self.reconstruction_plot.setXLink(self.signal_plot)
        self.reconstruction_plot.setYLink(self.signal_plot)
        self.difference_plot.setXLink(self.signal_plot)

    def draw_signal(self, linspace, data_points):
        """Draws a continuous signal in the signal plot."""
        self.signal_plot.clear()
        self.signal_plot.plot(linspace, data_points, pen=self.original_pen, name='Signal')

    def draw_samples(self, linspace, sampled_data):
        """Draws samples as 'x' markers in the signal plot."""
        self.signal_plot.plot(linspace, sampled_data, pen=None, symbol='x', symbolSize=10, symbolBrush='r', name='Samples')

    def draw_reconstruction(self, linspace, reconstruction_data):
        """Draws the reconstructed signal in the reconstruction plot."""
        self.reconstruction_plot.clear()
        self.reconstruction_plot.plot(linspace, reconstruction_data, pen=self.reconstruction_pen, name='Reconstructed Signal')


    def draw_difference(self, linspace, signal_data1, signal_data2, sampling_freq_spinBox, is_snr_checked, freq_slider):
        """Draws the difference between two signals in the difference plot."""
        if len(signal_data1) != len(signal_data2):
            print("Error: Signal lengths do not match.")
            return

        difference = signal_data1 - signal_data2
        self.difference_plot.clear()
        self.difference_plot_legend.clear()

        # Calculate the normalized difference
        normalized_difference = (4 * (difference - np.min(difference)) / (np.max(difference) - np.min(difference))) - 2

        # Adjust the error based on the sampling frequency
        if sampling_freq_spinBox > 2 * freq_slider and is_snr_checked and sampling_freq_spinBox < 6 * freq_slider:
            error_factor = np.exp(-sampling_freq_spinBox / (2 * freq_slider))
            adjusted_difference = normalized_difference * error_factor
        else:
            adjusted_difference = normalized_difference


        difference_plot_item = pg.PlotDataItem(linspace, adjusted_difference, pen=self.difference_pen)
        self.difference_plot.addItem(difference_plot_item)

        root_mean_squared_error = np.sqrt(np.mean(adjusted_difference ** 2))
        rmse_text = f"RMSE: {root_mean_squared_error:.4f}"
        rmse_text_item = pg.TextItem(rmse_text, color=(200, 50, 50), anchor=(0, 1))
        rmse_text_item.setPos(linspace[0], np.max(adjusted_difference))

        self.difference_plot.addItem(rmse_text_item)

