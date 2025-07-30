import torch
import torch.nn as nn
import torch.nn.functional as F
from dlsia.core.networks.fcnet import FCNetwork
import random

class DQR(nn.Module):
    def __init__(self,
                 in_channels,
                 base_network,
                 projection_layers = None,
                 dropout = 0.0,
                 clip_low = None,
                 clip_high = None,
                 final_action = None
                 ):
        super(DQR, self).__init__()
        self.in_channels = in_channels
        self.base_network =  base_network
        self.intermediate_channels = self.base_network.out_channels
        self.dropout = dropout
        self.projection_layers = projection_layers
        self.final_action = final_action

        if self.projection_layers is None:
            self.projection_layers = [ int(in_channels+self.intermediate_channels)//2 ]

        # projection head for the lower quantile

        self.median_head = FCNetwork(self.intermediate_channels,
                                     self.projection_layers,
                                     self.in_channels,
                                     dropout_rate=dropout)

        self.dqr_head = FCNetwork(self.intermediate_channels+in_channels,
                                  self.projection_layers,
                                  1,
                                  dropout_rate=dropout)

    def forward(self, x, directions):
        for i,j in zip(x.shape,directions.shape):
            assert i==j

        median = self.median_head(x)

        x = self.base_network(x)

        x_a = torch.cat([x, directions], dim=1)
        quantile_a = F.softplus(self.dqr_head(x_a))

        x_b = torch.cat([x, -directions], dim=1)
        quantile_b = F.softplus(self.dqr_head(x_b))


        if self.final_action is not None:
            lower_quantile = self.final_action(lower_quantile)
            median = self.final_action(median)
            upper_quantile = self.final_action(upper_quantile)

        return median, quantile_a, quantile_b



class NORandomizedPinballLoss(nn.Module):
    def __init__(self, quantiles, biases=None, channel_weights=None):
        """ Initialize the Randomized Pinball Loss module.

        Args:
            quantiles (list of floats): Quantiles for which to calculate the pinball loss (e.g., [0.25, 0.5, 0.75]).
            biases (list of floats, optional): Relative likelihoods of selecting each quantile. If not provided, each quantile has equal chance.
        """
        super(RandomizedPinballLoss, self).__init__()
        assert len(quantiles) == len(biases) if biases else True, "Length of quantiles must match length of biases"
        self.quantiles = quantiles
        self.biases = biases if biases else [1] * len(quantiles)  # Equal probability if no biases are provided
        self.channel_weights = None

    def forward(self, predictions, y_true):
        """ Calculate the randomized pinball loss.

        Args:
            y_true (Tensor): The true values.
            predictions (list of Tensors): Predictions corresponding to each quantile.

        Returns:
            Tensor: The pinball loss for a randomly selected quantile.
        """
        # Normalize biases to get probabilities
        total_bias = sum(self.biases)
        probabilities = [b / total_bias for b in self.biases]

        # Select a quantile based on the given probabilities
        index = random.choices(range(len(self.quantiles)), weights=probabilities, k=1)[0]
        selected_quantile = self.quantiles[index]
        selected_prediction = predictions[index]

        # Compute pinball loss for the selected quantile
        return self.pinball_loss(y_true, selected_prediction, selected_quantile, self.channel_weights)

    @staticmethod
    def pinball_loss(y_true, y_pred, tau, channel_weights=None):
        """ Calculate the pinball loss for a single quantile.

        Args:
            y_true (Tensor): The true values.
            y_pred (Tensor): The predicted values.
            tau (float): The quantile to calculate the loss for.

        Returns:
            Tensor: The pinball loss.
        """
        errors = y_true - y_pred
        if channel_weights is not None:
            errors = errors * channel_weights
        return torch.mean(torch.maximum(tau * errors, (tau - 1) * errors))





