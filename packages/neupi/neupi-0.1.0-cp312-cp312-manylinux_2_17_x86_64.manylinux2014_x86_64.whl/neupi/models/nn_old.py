from typing import List

import torch
import torch.nn as nn


class NeuralNetwork(nn.Module):
    def __init__(
        self,
        cfg,
        input_size: int,
        hidden_sizes: List[int],
        output_size: int,
        supervised_loss_lambda: float,
        library_pgm,
        is_teacher: bool = False,
    ):
        """
        Initializes a neural network with configurable layers.

        :param cfg: Configuration object containing network options.
        :param input_size: Number of features in the input data.
        :param hidden_sizes: List of neuron counts for each hidden layer.
        :param output_size: Number of neurons in the output layer.
        :param library_pgm: External library or tool specific parameter.
        """
        super(NeuralNetworkTwo, self).__init__()
        self.library_pgm = library_pgm
        self.cfg = cfg
        self.num_hidden_layers = cfg.student_layers if not is_teacher else cfg.teacher_layers
        self._set_activation_func(cfg)
        # Layer definition
        layers = []
        last_hidden_layer_size = self.init_hidden_layers(
            cfg,
            input_size,
            hidden_sizes,
            output_size,
            is_teacher,
            layers,
        )
        self.output_layer = nn.Linear(last_hidden_layer_size, output_size)
        self.dropout = nn.Dropout(cfg.dropout_rate) if not cfg.no_dropout else None
        self.no_dropout = cfg.no_dropout
        self.device = cfg.device
        self.initialize_weights()

    def init_hidden_layers(
        self,
        cfg,
        input_size,
        hidden_sizes,
        output_size,
        is_teacher,
        layers,
    ):
        for i, hidden_size in enumerate(hidden_sizes):
            layers.append(nn.Linear(input_size if i == 0 else hidden_sizes[i - 1], hidden_size))
            layers.append(self.hidden_activation())
            if not cfg.no_batchnorm and not is_teacher:
                layers.append(nn.BatchNorm1d(hidden_size))

        if self.num_hidden_layers == 0:
            # Initialize a LR model
            # layers.append(nn.Linear(input_size, output_size))
            last_hidden_layer_size = input_size
        if self.num_hidden_layers > 0:
            self.hidden_layers = nn.Sequential(*layers)
            last_hidden_layer_size = hidden_sizes[-1]
        return last_hidden_layer_size

    def _set_activation_func(self, cfg):
        self.hidden_activation_function = cfg.hidden_activation_function
        if cfg.hidden_activation_function == "relu":
            self.hidden_activation = nn.ReLU
        elif cfg.hidden_activation_function == "leaky_relu":
            self.hidden_activation = nn.LeakyReLU

    def initialize_weights(self):
        """
        Initializes the weights of the neural network.
        """
        # check if the model has hidden layers
        if self.num_hidden_layers > 0:
            for layer in self.hidden_layers:
                if isinstance(layer, nn.Linear):
                    nn.init.kaiming_normal_(
                        layer.weight,
                        mode="fan_in",
                        nonlinearity=self.hidden_activation_function,
                    )
                    nn.init.zeros_(layer.bias)
        if self.num_hidden_layers > -1:
            nn.init.xavier_uniform_(self.output_layer.weight)
            nn.init.zeros_(self.output_layer.bias)

    def forward(self, x):
        """
        The forward function applies a series of hidden layers to the input, with optional dropout, and
        returns the model output.

        :param x: The input to the forward function, which is the input to the neural network model. It
        could be a single data point or a batch of data points
        :return: The output of the model.
        """
        if self.num_hidden_layers > 0:
            for layer in self.hidden_layers:
                x = layer(x)
                # Apply dropout
                if not self.no_dropout and isinstance(layer, nn.ReLU):
                    x = self.dropout(x)
        else:
            raise ValueError("Invalid number of hidden layers")
        model_output = self.output_layer(x)
        return model_output

    def process_buckets_single_row_for_pgm(self, nn_output, true, buckets):
        """
        Process the buckets based on the given sample tensor for a single row.

        cfg:
            sample (torch.Tensor): Input tensor of shape (n_vars,) containing binary values.
            buckets (list): List of bucket indices where each bucket is represented by a list of variable indices.

        Returns:
            torch.Tensor: Processed tensor of the same shape as the input sample,
                        where the buckets have been modified according to the provided rules.
        """

        final_sample = nn_output.clone().requires_grad_(True)
        # Handle the first bucket
        # Modify the tensor based on 'evid' and 'unobs' buckets
        evid_indices = buckets["evid"]
        unobs_indices = buckets["unobs"]

        final_sample[evid_indices] = true[evid_indices]
        final_sample[unobs_indices] = float("nan")
        return final_sample

    def train_iter(
        self,
        pgm,
        data,
        data_pgm,
        initial_data,
        evid_bucket,
        query_bucket,
        unobs_bucket,
        return_mean=True,
    ):
        input_to_model = self._select_input(data, data_pgm)
        model_output = self(input_to_model)
        output = self._apply_activation(model_output)

        if torch.isnan(output).any():
            print("Nan in output")
            print(output)
            raise (ValueError("Nan in output"))

        buckets = {"evid": evid_bucket, "query": query_bucket, "unobs": unobs_bucket}
        output_for_pgm = self.process_buckets_single_row_for_pgm(
            nn_output=output, true=initial_data, buckets=buckets
        )

        loss = self._calculate_loss(pgm, output_for_pgm, output, initial_data, buckets)
        if return_mean:
            return loss.mean()
        return loss

    def validate_iter(
        self,
        pgm,
        all_unprocessed_data,
        all_nn_outputs,
        all_outputs_for_pgm,
        all_buckets,
        data,
        data_pgm,
        initial_data,
        evid_bucket,
        query_bucket,
        unobs_bucket,
        attention_mask,
        return_mean=True,
    ):
        input_to_model = self._select_input(data, data_pgm)
        model_output = self(input_to_model)
        model_output = self._apply_activation(model_output)

        if torch.isnan(model_output).any():
            print(model_output)
            raise (ValueError("Nan in output"))

        buckets = {"evid": evid_bucket, "query": query_bucket, "unobs": unobs_bucket}
        output_for_pgm = self.process_buckets_single_row_for_pgm(
            nn_output=model_output, true=initial_data, buckets=buckets
        )

        loss = self._calculate_loss(pgm, output_for_pgm, model_output, initial_data, buckets)
        all_nn_outputs.extend(model_output.detach().cpu().tolist())
        all_unprocessed_data.extend(initial_data.detach().cpu().tolist())
        all_outputs_for_pgm.extend(output_for_pgm.detach().cpu().tolist())
        for each_bucket in buckets:
            all_buckets[each_bucket].extend(buckets[each_bucket].detach().cpu().tolist())
        if return_mean:
            return loss.mean()
        else:
            return loss

    def _select_input(self, data, data_pgm):
        if self.cfg.input_type == "data":
            return data
        else:
            raise ValueError("Input type not supported for NN model 2")

    def _apply_activation(self, model_output):
        if self.cfg.activation_function == "sigmoid":
            model_output = torch.sigmoid(model_output)
        elif self.cfg.activation_function == "hard_sigmoid":
            model_output = nn.Hardsigmoid()(model_output)
        else:
            raise ValueError("Activation function not supported for NN model 2")
        return model_output

    def _calculate_loss(self, pgm, output_for_pgm):
        final_func_value = pgm.evaluate(output_for_pgm)
        loss_from_pgm = (
            -final_func_value if not self.cfg.no_log_loss else -torch.exp(final_func_value)
        )
        loss = loss_from_pgm
        return loss
