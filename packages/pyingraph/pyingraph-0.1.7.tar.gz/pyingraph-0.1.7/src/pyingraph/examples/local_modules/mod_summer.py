#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for a summing block.
"""

import pyingraph

class Summer(pyingraph.BlockBase):
    """
    A block that computes a scaled sum of its inputs.
    """
    def __init__(self):
        super().__init__()
        self.attrNamesArr = ['scales']
        self._inputs = []

    def read_inputs(self, inputs: list) -> None:
        """Reads and stores the input values."""
        self._inputs = inputs

    def compute_outputs(self, time: float) -> list:
        """Computes the scaled sum of the inputs."""
        if not hasattr(self, 'scales') or not self._inputs:
            return [0.0]

        if len(self.scales) != len(self.scales):
            raise ValueError("Length of scales and inputs must be the same.")

        # if one input item in inputs is None, set that input to zero
        for i, input_item in enumerate(self._inputs):
            if input_item is None:
                self._inputs[i] = 0.0
        scaled_inputs = [i * s for i, s in zip(self._inputs, self.scales)]
        total_sum = sum(scaled_inputs)
        return [total_sum]

    def reset(self) -> None:
        """Resets the internal state of the block."""
        self._inputs = []

# Example usage
if __name__ == "__main__":
    summer_block = Summer()
    
    # Set parameters
    params = {'scales': [0.5, 1.0, -2.0]}
    summer_block.read_parameters(params)
    
    # Provide inputs
    inputs = [10, 20, 5]
    summer_block.read_inputs(inputs)
    
    # Compute output
    output = summer_block.compute_outputs(time=0)
    print(f"Inputs: {inputs}")
    print(f"Scales: {summer_block.scales}")
    print(f"Computed Output: {output}") # Expected: (10*0.5) + (20*1.0) + (5*-2.0) = 5 + 20 - 10 = 15