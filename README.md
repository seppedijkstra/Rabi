# Determining Rabi oscillations

In this project there can be found different folders. In the experiment folder you can find the actual experiments. The experiments that are present right now are as follows:

## ESR Experimet
In this experiment you can sweep over a certain range with a step. These values can be found in CONSTANTS, but can be altered of course, same goes for the repetitions. The goal of this experiment is to show the influence of a MW of a certain frequency on the SPIN State change. The theory can be found somewhere else. This experiment is to show that the antenna is worling properly

## Rabi Experiment
In this experiment different sequences will be loaded onto the AWR to determine the Rabi oscillations, to let this work every other experiment must run. We will try different drafts where we switch around the parameters to find the best graph of the Rabi oscillations

## Things to notice
Some things are important sicne they can heavily influence the circuits:
- The output range of the RF output which is mostly channel 1 (0 in code) must be 0 dbm otherwise it can have negative impact on the amplifier. 
