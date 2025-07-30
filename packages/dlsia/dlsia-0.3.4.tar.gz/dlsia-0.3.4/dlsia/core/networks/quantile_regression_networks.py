import torch
import torch.nn as nn
import torch.nn.functional as F
from dlsia.core.networks.fcnet import FCNetwork
import random


class QuantileRegressionNetwork(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 base_network,
                 projection_layers = None,
                 dropout = 0.0,
                 final_action = None
                 ):
        super(QuantileRegressionNetwork, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.base_network =  base_network
        self.intermediate_channels = self.base_network.out_channels
        self.dropout = dropout
        self.projection_layers = projection_layers
        self.final_action = final_action



        if self.projection_layers is None:
            self.projection_layers = [ int(out_channels+self.intermediate_channels)//2 ]

        # projection head for the lower quantile
        self.quantile_head = FCNetwork(Cin=self.intermediate_channels,
                                       Cmiddle=self.projection_layers,
                                       Cout=self.out_channels,
                                       dropout_rate=self.dropout,
                                       is_monotonic=True)



    def forward(self, x, quantile):
        x = self.base_network(x)

        self.quantile_head(x)





    def save_network_parameters(self, name=None):
        """
        Save the network parameters
        :param name: The filename
        :type name: str
        :return: None
        :rtype: None
        """
        network_dict = OrderedDict()
        network_dict["base_network"] = self.squash_head.topology_dict()
        network_dict["head_m1"] = self.squash_head.topology_dict()
        network_dict["head_0"] = self.squash_head.topology_dict()
        network_dict["head_p1"] = self.squash_head.topology_dict()

        if name is None:
            return network_dict
        torch.save(network_dict, name)
