'''
Execute by running: ``python vivarium_smoldyn/process/smoldyn_process.py``
'''

import os

import smoldyn as sm

from vivarium.core.process import Process
from vivarium.core.composition import (
    simulate_process_in_experiment,
    PROCESS_OUT_DIR,
)
from vivarium.plots.simulation_output import plot_simulation_output


NAME = 'smoldyn'


class SmoldynProcess(Process):

    name = NAME
    defaults = {}

    def __init__(self, parameters=None):
        super(SmoldynProcess, self).__init__(parameters)

        self.dt = 0.1

        self.smoldyn = sm.Simulation(
            low=[0, 0],
            high=[10, 10],
            types="p")

        # species X A B A2 B2
        X = self.smoldyn.addSpecies("X", difc=0, color="green", display_size=3)
        A = self.smoldyn.addSpecies("A", difc=1, color="red", display_size=3)
        B = self.smoldyn.addSpecies("B", difc=1, color="blue", display_size=3)
        A2 = self.smoldyn.addSpecies("A2", difc=1, color="red", display_size=5)
        B2 = self.smoldyn.addSpecies("B2", difc=1, color="blue", display_size=5)

        # mol 1 X 5 5
        X.addToSolution(1, pos=[5, 5])

        express = self.smoldyn.addReaction("express", subs=[X], prds=[X, A, B], rate=1)
        Adimer = self.smoldyn.addBidirectionalReaction("Adimer", subs=[A, A], prds=[A2], kf=1, kb=1)
        Bdimer = self.smoldyn.addBidirectionalReaction("Bdimer", subs=[B, B], prds=[B2], kf=1, kb=1)
        AxB = self.smoldyn.addReaction("AxB", subs=[A2, B], prds=[A2], rate=1)
        BxA = self.smoldyn.addReaction("BxA", subs=[B2, A], prds=[B2], rate=1)
        Adegrade = self.smoldyn.addReaction("Adegrade", subs=[A], prds=[], rate=0.01)
        Bdegrade = self.smoldyn.addReaction("Bdegrade", subs=[B], prds=[], rate=0.01)

        # self.smoldyn.addCommand("molcount bistableout.txt", cmd_type="N", step=10)

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

        results = self.run(timestep)



        return {}

    def run(
            self,
            time
    ):
        self.smoldyn.run(
            time,
            dt=self.dt)

        import ipdb;
        ipdb.set_trace()

# functions to configure and run the process
def run_template_process():

    # initialize the process by passing in parameters
    parameters = {}
    template_process = SmoldynProcess(parameters)

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
