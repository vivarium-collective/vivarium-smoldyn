'''
Execute by running: ``python vivarium_smoldyn/process/colloidal.py``
'''

import os

from vivarium.core.process import Process
from vivarium.core.composition import (
    simulate_process_in_experiment,
    PROCESS_OUT_DIR,
)
from vivarium.plots.simulation_output import plot_simulation_output

from smoldyn.smoldyn import Species


NAME = 'vivarium_smoldyn'


class Colloidal(Process):

    name = NAME
    defaults = {}

    def __init__(self, parameters=None):
        super(Colloidal, self).__init__(parameters)


        import ipdb; ipdb.set_trace()

    def ports_schema(self):
        return {
            'internal': {
                'A': {
                    '_default': 1.0,
                    '_updater': 'accumulate',
                    '_emit': True,
                },
            },
        }

    def next_update(self, timestep, states):

        internal_A = states['internal']['A']

        internal_update = internal_A * timestep

        return {
            'internal': {
                'A': internal_update},
        }


# functions to configure and run the process
def run_template_process():

    # initialize the process by passing in parameters
    parameters = {}
    template_process = Colloidal(parameters)

    # declare the initial state, mirroring the ports structure
    initial_state = {
        'internal': {
            'A': 0.0
        },
        'external': {
            'A': 1.0
        },
    }

    # run the simulation
    sim_settings = {
        'total_time': 10,
        'initial_state': initial_state}
    output = simulate_process_in_experiment(template_process, sim_settings)

    return output


def test_template_process():
    output = run_template_process()
    # TODO: Add assert statements to ensure correct performance.


def main():
    out_dir = os.path.join(PROCESS_OUT_DIR, NAME)
    os.makedirs(out_dir, exist_ok=True)

    output = run_template_process()

    # plot the simulation output
    plot_settings = {}
    plot_simulation_output(output, plot_settings, out_dir)


# run module with python vivarium_smoldyn/process/colloidal.py
if __name__ == '__main__':
    main()
