import torch
import torch.nn as nn
import torch.nn.functional as F

class Encoder(nn.Module):
    def __init__(self, pre_encoder, in_features, latent_sequence, dropout_p):
        super(Encoder, self).__init__()
        self.pre_encoder = pre_encoder
        self.flatten = nn.Flatten()

        layers = []
        previous_layer_features = in_features
        for num_features in latent_sequence:
            layers.append(nn.Linear(previous_layer_features, num_features))
            layers.append(nn.BatchNorm1d(num_features))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_p))
            previous_layer_features = num_features

        self.fc_layers = nn.Sequential(*layers)

    def forward(self, x):
        x = self.pre_encoder(x)
        x = self.flatten(x)
        x = self.fc_layers(x)
        return x

class Decoder(nn.Module):
    def __init__(self, post_decoder, latent_sequence, in_features, dropout_p, C, K):
        super(Decoder, self).__init__()
        self.post_decoder = post_decoder

        layers = []
        previous_layer_features = latent_sequence[-1]
        for num_features in reversed(latent_sequence[:-1]):
            layers.append(nn.Linear(previous_layer_features, num_features))
            layers.append(nn.BatchNorm1d(num_features))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_p))
            previous_layer_features = num_features

        layers.append(nn.Linear(previous_layer_features, in_features))
        self.fc_layers = nn.Sequential(*layers)
        self.reshape = nn.Unflatten(1, (C, K, K))

    def forward(self, x):
        x = self.fc_layers(x)
        x = self.reshape(x)
        x = self.post_decoder(x)
        return x

class Autoencoder(nn.Module):
    def __init__(self, pre_encoder, post_decoder, in_features, latent_sequence, dropout_p, C, K):
        super(Autoencoder, self).__init__()
        self.encoder = Encoder(pre_encoder, in_features, latent_sequence, dropout_p)
        self.decoder = Decoder(post_decoder, latent_sequence, in_features, dropout_p, C, K)

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x
